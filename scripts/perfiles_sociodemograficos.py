"""Segmenta grupos sociodemográficos agregados; no identifica personas."""
from pathlib import Path
import os
import sys
import json
import re
from html import escape

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '.analysis_deps'))
os.environ.setdefault('MPLCONFIGDIR', str(ROOT / '.mplconfig'))
os.environ.setdefault('OMP_NUM_THREADS', '2')
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans, AgglomerativeClustering
from sklearn.mixture import GaussianMixture
from sklearn.preprocessing import StandardScaler, RobustScaler
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score, davies_bouldin_score, adjusted_rand_score

OUT = ROOT / 'reports/local/sociodemografico'
AGES = ['18-24', '25-34', '35-44', '45-54', '55-64', '65-74', '75-84', '85+']
YEARS = [2009, 2012, 2015, 2018, 2021, 2024]
KEY = ['region', 'sexo', 'grupo_edad', 'tipo_seccion']
COUNTS = ['lista_nominal', 'si_votaron', 'no_votaron', 'no_especificados']
COLORS = ['#207b9b', '#e28632']


def estimator(name, k, seed=42):
    if name == 'kmeans':
        return KMeans(n_clusters=k, n_init=30, random_state=seed)
    if name == 'ward':
        return AgglomerativeClustering(n_clusters=k, linkage='ward')
    return GaussianMixture(n_components=k, covariance_type='diag', n_init=10,
                           reg_covar=1e-4, random_state=seed)


def save(fig, name):
    fig.tight_layout()
    fig.savefig(OUT / (name + '.png'), dpi=180, bbox_inches='tight')
    plt.close(fig)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    d = pd.read_csv(ROOT / 'data/processed/civia_dataset_maestro_municipal_2009_2024_con_region.csv')
    d[['sexo', 'tipo_seccion']] = d[['sexo', 'tipo_seccion']].apply(lambda s: s.str.lower())  # el maestro actual trae 'Hombre', 'Urbana'…
    assert (d.lista_nominal == d.si_votaron + d.no_votaron + d.no_especificados).all()
    assert not d.duplicated(['anio', 'entidad_clave', 'municipio_clave', 'sexo_codigo', 'grupo_edad', 'tipo_seccion_codigo']).any()
    a = d.groupby([*KEY, 'anio'], observed=True)[COUNTS].sum()
    a['especificados'] = a.si_votaron + a.no_votaron
    a['participacion_pct'] = 100 * a.si_votaron / a.especificados.replace(0, np.nan)
    a['ns_pct'] = 100 * a.no_especificados / a.lista_nominal.replace(0, np.nan)
    a.to_csv(OUT / 'segmentos_por_eleccion.csv')
    trajectories = a.participacion_pct.unstack('anio').reindex(columns=YEARS)
    support = a.especificados.unstack('anio').reindex(columns=YEARS)
    missing = a.ns_pct.unstack('anio').reindex(columns=YEARS)
    eligible = trajectories.notna().all(axis=1) & support.ge(100).all(axis=1) & missing.le(20).all(axis=1)
    coverage = pd.DataFrame({'elegible': eligible, 'elecciones_disponibles': trajectories.notna().sum(axis=1),
                             'minimo_especificados': support.min(axis=1), 'maximo_ns_pct': missing.max(axis=1)})
    coverage.to_csv(OUT / 'cobertura_segmentos.csv')
    # No binario se conserva en el descriptivo, sin imputar cinco elecciones inexistentes.
    special = a.reset_index().query("sexo == 'no binario'")
    special.to_csv(OUT / 'no_binario_descriptivo.csv', index=False)
    metrics, assignments, totals, compositions, differences = [], [], [], [], []
    chosen, rules = [], []
    for region in ['norte', 'centro', 'sur']:
        raw =trajectories.loc[eligible].xs(region, level='region', drop_level=False)
        X = StandardScaler().fit_transform(raw)
        fits = {}
        for name in ['kmeans', 'ward', 'gmm']:
            for k in range(2, 6):
                m = estimator(name, k)
                labels = m.fit_predict(X)
                if len(set(labels)) != k:
                    continue
                row = dict(region=region, algoritmo=name, k=k, segmentos=len(raw),
                           silhouette=silhouette_score(X, labels),
                           davies_bouldin=davies_bouldin_score(X, labels),
                           segmento_minimo_pct=100*np.bincount(labels).min()/len(labels),
                           bic=m.bic(X) if name == 'gmm' else np.nan)
                if k == 2:
                    subsamples = []
                    for seed in range(10):
                        ids = np.sort(np.random.default_rng(seed).choice(len(raw), int(.8*len(raw)), replace=False))
                        sx = StandardScaler().fit_transform(raw.iloc[ids])
                        sl = estimator(name, 2, seed).fit_predict(sx)
                        subsamples.append(adjusted_rand_score(labels[ids], sl))
                    leave_out = []
                    for year in YEARS:
                        reduced = StandardScaler().fit_transform(raw.drop(columns=year))
                        alternative = estimator(name, 2).fit_predict(reduced)
                        leave_out.append(adjusted_rand_score(labels, alternative))
                    robust = estimator(name, 2).fit_predict(RobustScaler().fit_transform(raw))
                    row.update(ari_submuestras_media=np.mean(subsamples), ari_submuestras_min=min(subsamples),
                               ari_sin_una_eleccion_media=np.mean(leave_out), ari_sin_una_eleccion_min=min(leave_out),
                               ari_escala_robusta=adjusted_rand_score(labels, robust))
                    fits[name] = (labels, m)
                metrics.append(row)
        candidates = pd.DataFrame([r for r in metrics if r['region'] == region and r['k'] == 2])
        stable = candidates[(candidates.segmento_minimo_pct >= 10) &
                            (candidates.ari_submuestras_media >= .75) &
                            (candidates.ari_sin_una_eleccion_media >= .75) &
                            (candidates.ari_submuestras_min >= .6) &
                            (candidates.ari_sin_una_eleccion_min >= .6)]
        best = (stable if not stable.empty else candidates).sort_values('silhouette', ascending=False).iloc[0]
        labels, fitted = fits[best.algoritmo]
        # Etiquetas ordenadas por media de tasas de las seis elecciones, con igual peso por segmento.
        order = pd.Series(raw.mean(axis=1).to_numpy()).groupby(labels).mean().sort_values().index
        mapping = {order[0]: 'A', order[1]: 'B'}
        profile = pd.Series([mapping[label] for label in labels], index=raw.index, name='perfil')
        assigned = raw.rename(columns=lambda y: 'participacion_' + str(y)).join(profile)
        assigned['algoritmo'] = best.algoritmo
        assignments.append(assigned)
        # ¿Cuánto del perfil lo reproduce una regla simple "categoría -> perfil mayoritario"? Si edad sola acierta casi todo,
        # el agrupamiento aporta poco más que rangos de edad. Referencia: proporción del perfil más grande.
        key = raw.index.to_frame(index=False).assign(perfil=profile.to_numpy())
        for cols in (['grupo_edad'], ['sexo'], ['tipo_seccion'], ['grupo_edad', 'tipo_seccion'], ['grupo_edad', 'sexo']):
            hits = key.perfil.eq(key.groupby(cols).perfil.transform(lambda s: s.mode()[0])).mean()
            rules.append(dict(region=region, regla='+'.join(cols), acierto=hits, referencia=key.perfil.value_counts(normalize=True).max()))
        chosen.append(dict(region=region, algoritmo=best.algoritmo, silhouette=float(best.silhouette),
                           cumple_filtros_estabilidad=not stable.empty))
        cells = a.join(profile, how='inner').reset_index()
        for (p, year), g in cells.groupby(['perfil', 'anio']):
            totals.append(dict(region=region, perfil=p, anio=year, segmentos=len(g),
                               lista_nominal=int(g.lista_nominal.sum()),
                               participacion_pct=100*g.si_votaron.sum()/g.especificados.sum(),
                               ns_pct=100*g.no_especificados.sum()/g.lista_nominal.sum()))
        current = cells[cells.anio == 2024]
        for variable in ['grupo_edad', 'sexo', 'tipo_seccion']:
            for (p, category), g in current.groupby(['perfil', variable]):
                denominator = current.loc[current.perfil == p, 'lista_nominal'].sum()
                compositions.append(dict(region=region, perfil=p, variable=variable, categoria=category,
                                         segmentos=len(g), lista_nominal=int(g.lista_nominal.sum()),
                                         porcentaje_ln_perfil=100*g.lista_nominal.sum()/denominator))
        # Contrastes descriptivos (no pruebas causales ni independientes del clustering).
        for variable in ['sexo', 'tipo_seccion']:
            dist = pd.crosstab(profile, raw.index.get_level_values(variable))
            for category in dist.columns:
                differences.append(dict(region=region, variable=variable, categoria=category,
                                        proporcion_segmentos_A=100*dist.loc['A', category]/dist.loc['A'].sum(),
                                        proporcion_segmentos_B=100*dist.loc['B', category]/dist.loc['B'].sum()))

        fig, axes = plt.subplots(1, 2, figsize=(13, 4.5))
        pca = PCA(n_components=2).fit(X)
        points = pca.transform(X)
        for p, color in zip(['A', 'B'], COLORS):
            mask = profile.eq(p).to_numpy()
            axes[0].scatter(points[mask, 0], points[mask, 1], color=color, label=p, s=45, alpha=.8)
            for values in raw.loc[mask].to_numpy():
                axes[1].plot(YEARS, values, color=color, alpha=.12, linewidth=1)
            axes[1].plot(YEARS, raw.loc[mask].mean(), color=color, marker='o', linewidth=3, label=p)
        axes[0].set(title=f'PCA: {100*pca.explained_variance_ratio_.sum():.1f}% de varianza', xlabel='Componente 1', ylabel='Componente 2')
        axes[1].set(title='Trayectorias de segmentos; media sin ponderar', ylabel='SV / (SV + NV) · %', xticks=YEARS)
        for ax in axes:
            ax.legend(title='Perfil')
            ax.grid(alpha=.15)
        fig.suptitle(f'{region} · {best.algoritmo} · silhouette={best.silhouette:.3f} · segmentos sociodemográficos')
        save(fig, f'01_trayectorias_{region}')

        fig, axes = plt.subplots(1, 3, figsize=(14, 5), sharey=True)
        for ax, section in zip(axes, ['urbana', 'mixta', 'rural']):
            grid = profile.xs(section, level='tipo_seccion').reset_index()
            grid['valor'] = grid.perfil.map({'A': 0, 'B': 1})
            matrix = grid.pivot(index='grupo_edad', columns='sexo', values='valor').reindex(index=AGES, columns=['hombre', 'mujer'])
            ax.imshow(matrix, vmin=0, vmax=1, cmap=matplotlib.colors.ListedColormap(COLORS), aspect='auto')
            ax.set_xticks([0, 1], ['hombre', 'mujer'])
            ax.set_yticks(range(8), AGES)
            ax.set_title(section)
            for i in range(8):
                for j in range(2):
                    v = matrix.iloc[i, j]
                    ax.text(j, i, 'A' if v == 0 else 'B' if v == 1 else '—', ha='center', va='center', color='white', fontsize=13)
        fig.suptitle(f'{region}: ¿qué grupos componen A y B? · no son etiquetas individuales')
        save(fig, f'02_composicion_{region}')
        print(region, chosen[-1], flush=True)

    scores = pd.DataFrame(metrics)
    assigned = pd.concat(assignments)
    total = pd.DataFrame(totals)
    comp = pd.DataFrame(compositions)
    scores.to_csv(OUT / 'comparacion_algoritmos.csv', index=False)
    assigned.to_csv(OUT / 'perfiles_segmentos.csv')
    pd.DataFrame(rules).to_csv(OUT / 'perfil_vs_variables.csv', index=False)
    total.to_csv(OUT / 'indicadores_perfil_eleccion.csv', index=False)
    comp.to_csv(OUT / 'composicion_perfiles_2024.csv', index=False)
    # Seis fichas con pertenencia exhaustiva: exactamente dos perfiles por región.
    fichas = ['# Dos perfiles sociodemográficos por región',
              'Segmentación operativa de datos agregados 2009–2024. No clasifica personas individuales. '
              'Los nombres describen participación observada, no causas o actitudes. '
              'Cada combinación elegible pertenece a un solo perfil; no binario se conserva aparte por falta de historial.']
    executive = []
    for region in ['norte', 'centro', 'sur']:
        for profile in ['A', 'B']:
            group = assigned.xs(region, level='region').query('perfil == @profile').reset_index()
            label = 'Participación menor: segmentos jóvenes y de edad avanzada' if profile == 'A' else 'Participación mayor: segmentos adultos y combinaciones jóvenes específicas'
            fichas.extend([f'## {region.capitalize()} · Perfil {profile}', f'**{label}.**',
                           f'Incluye {len(group)} combinaciones de sexo, edad y tipo de sección.',
                           '| Sexo | Edad | Tipos de sección incluidos |', '| --- | --- | --- |'])
            for (sex, age), members in group.groupby(['sexo', 'grupo_edad'], sort=False):
                sections = ', '.join(sorted(members.tipo_seccion))
                fichas.append(f'| {sex} | {age} | {sections} |')
            history = total[(total.region == region) & (total.perfil == profile)].sort_values('anio')
            fichas.extend(['', '**Participación entre registros especificados:**',
                           ' · '.join(f'{r.anio}: {r.participacion_pct:.2f}%' for r in history.itertuples()), ''])
            if profile == 'A':
                fichas.append('Hipótesis de acción: investigar por separado las barreras de los segmentos jóvenes y de 85+; '
                              'probar formatos accesibles e información cívica útil. Compartir perfil no significa necesitar la misma intervención.')
            else:
                fichas.append('Hipótesis de acción: sostener acceso a información cívica y espacios comunitarios; '
                              'evaluar experiencias locales antes de intentar trasladarlas a otros segmentos.')
            latest_row = history[history.anio == 2024].iloc[0]
            executive.append(dict(region=region, perfil=profile, nombre_descriptivo=label,
                                  segmentos=len(group), participacion_2024=float(latest_row.participacion_pct)))
    fichas.extend(['## Alcance de la conclusión',
                   'Dos grupos dieron la mejor silhouette entre k=2..5 en la representación probada. '
                   'Esto no demuestra que existan únicamente dos tipos naturales de ciudadanía. '
                   'Falta contrastar la agregación regional y cotejar el maestro con los originales. '
                   'Las estrategias requieren validación; el modelo no identifica motivos ni escolaridad.'])
    fichas_text = re.sub(r'\|\n\n(?=\|)', '|\n', '\n\n'.join(fichas))
    (OUT / 'fichas_dos_perfiles_por_region.md').write_text(fichas_text + '\n', encoding='utf-8')
    pd.DataFrame(executive).to_csv(OUT / 'seis_perfiles_resumen.csv', index=False)
    pd.DataFrame(differences).to_csv(OUT / 'contrastes_descriptivos.csv', index=False)
    fig, axes = plt.subplots(1, 3, figsize=(13, 4), sharey=True)
    for ax, region in zip(axes, ['norte', 'centro', 'sur']):
        for name, g in scores[scores.region == region].groupby('algoritmo'):
            ax.plot(g.k, g.silhouette, marker='o', label=name)
        ax.set(title=region, xlabel='Número de perfiles', ylabel='Silhouette', xticks=[2, 3, 4, 5])
        ax.legend()
    save(fig, '03_numero_perfiles')

    methods = dict(unidad='región × sexo × grupo de edad × tipo de sección',
                   variables_clustering=['participación especificada en ' + str(y) for y in YEARS],
                   peso='igual por segmento; los conteos solo ponderan indicadores descriptivos',
                   escala='StandardScaler por elección dentro de cada región',
                   filtros='seis elecciones presentes, >=100 especificados y NS<=20% en cada elección',
                   gmm='covarianza diagonal, regularización 0.0001, diez inicializaciones',
                   comparacion='k=2..5; selección k=2 por silhouette con tamaño mínimo 10%, ARI medio >=0.75 y mínimo >=0.60 en submuestras y omisión de elección, cuando hay candidatos; umbrales exploratorios',
                   estabilidad='diez submuestras sin reemplazo del 80%, recalculando escala; seis pruebas omitiendo una elección; escala robusta',
                   semilla=42, segmentos_elegibles=int(eligible.sum()), segmentos_total=len(eligible), modelos_elegidos=chosen,
                   limites=['sin seguimiento individual', 'sin escolaridad', 'agregación regional oculta variación local',
                            'tasas observadas no implican causas', 'segmentos no son cohortes de las mismas personas',
                            'falta cotejar maestro contra originales y validar en otra representación'])
    (OUT / 'metodologia.json').write_text(json.dumps(methods, ensure_ascii=False, indent=2), encoding='utf-8')
    best_k = scores.loc[scores.groupby('region').silhouette.idxmax(), ['region', 'algoritmo', 'k', 'silhouette']]
    report = '''<!doctype html><html lang="es"><meta charset="utf-8"><title>Perfiles sociodemográficos de participación</title>
    <style>body{font:16px system-ui;max-width:1200px;margin:35px auto;padding:20px;color:#173442;background:#f5f8fa}h1,h2{color:#145b70}table{border-collapse:collapse;background:white;font-size:13px;display:block;overflow:auto}td,th{padding:8px;border:1px solid #ccd7dd}img{max-width:100%}figure{margin:25px 0;background:white;padding:12px}.note{background:#fff0d4;padding:18px}</style>
    <h1>Perfiles sociodemográficos de participación</h1>
    <p>Exploración regional de segmentos por sexo, edad y tipo de sección · 2009–2024</p>
    <div class="note">Este análisis sustituye la agrupación municipal como propuesta de perfiles para el Reto 1.
    Cada punto representa un segmento sociodemográfico agregado en una región. No representa una persona
    ni permite identificar votantes habituales u ocasionales.</div>
    <h2>Qué agrupamos y cómo</h2><p>Se suman LN/SV/NV/NS de los municipios dentro de cada combinación región × sexo × edad × tipo de sección.
    Se recalculan seis tasas SV/(SV+NV), una por elección, y se agrupan sus trayectorias estandarizadas.
    Edad, sexo y sección definen y describen los segmentos; no se codifican como números ordinales en el modelo.
    Cada segmento pesa igual al ajustar; los indicadores agregados se recalculan desde conteos.</p>
    <p>Se conservan segmentos con seis elecciones, al menos 100 especificados y NS ≤20% en cada una.
    No se imputan elecciones ausentes. No binario aparece solo en 2024: se conserva en su tabla descriptiva
    y no se fuerza su asignación histórica. No hay escolaridad ni identidades individuales en la fuente.</p>
    <h2>Modelos elegidos para dos perfiles</h2>'''
    report += pd.DataFrame(chosen).to_html(index=False, float_format=lambda x: f'{x:.3f}')
    report += '<p>A indica menor media de participación entre las seis elecciones; B mayor media, dentro de cada región. Son nombres operativos, no categorías oficiales. Dos perfiles son una hipótesis; revisar solapamiento y alternativas.</p>'
    report += '<p><a href="fichas_dos_perfiles_por_region.md">Ver las seis fichas con pertenencia exacta y evolución histórica</a>.</p>'
    report += '<p>Selección: al menos 10% de segmentos en cada grupo, ARI medio ≥0.75 y mínimo ≥0.60 en submuestras y omisión de elección; luego mayor silhouette. Son umbrales exploratorios. Una mejor silhouette con baja estabilidad no se considera suficiente.</p>'
    narratives = []
    report += '<h2>Descripción de los perfiles y propuestas para explorar</h2>'
    for region in ['norte', 'centro', 'sur']:
        report += f'<h3>{region}</h3>'
        for p in ['A', 'B']:
            group = assigned.xs(region, level='region').query('perfil == @p').reset_index()
            title = 'Participación históricamente menor' if p == 'A' else 'Participación históricamente mayor'
            members = '; '.join(f'{r.sexo}, {r.grupo_edad}, sección {r.tipo_seccion}' for r in group.itertuples())
            action = ('Investigar barreras mediante escucha y pruebas piloto; separar acciones para juventud y para edades avanzadas. '
                      'Probar información cívica accesible y canales adecuados a cada segmento, sin asumir causas por su edad o sexo.'
                      if p == 'A' else
                      'Probar acciones de continuidad, información de servicio y espacios de participación comunitaria; '
                      'evaluar si las experiencias locales pueden aportar a otros grupos sin asumir que son transferibles.')
            narratives.append(dict(region=region, perfil=p, nombre_provisional=title, segmentos=members,
                                   estrategia_hipotesis=action))
            report += f'<p><strong>{p} · {title}.</strong> {escape(action)}</p><details><summary>Ver composición exacta</summary><p>{escape(members)}</p></details>'
    pd.DataFrame(narratives).to_csv(OUT / 'narrativas_y_estrategias.csv', index=False)
    report += '<h2>Participación de los perfiles en 2024</h2>' + total[total.anio == 2024].to_html(index=False, float_format=lambda x: f'{x:.2f}')
    report += '<h2>Composición por edad, sexo y sección</h2><p>Los porcentajes son proporciones de lista nominal dentro de cada perfil en 2024; no porcentajes de participación. Una categoría frecuente puede deberse a su tamaño poblacional. Las matrices muestran qué combinaciones específicas pertenecen a cada perfil.</p>'
    report += comp.to_html(index=False, float_format=lambda x: f'{x:.2f}')
    report += '<h2>Comparación de modelos para dos perfiles</h2>' + scores[scores.k == 2].to_html(index=False, float_format=lambda x: f'{x:.3f}')
    report += '<p>Silhouette mayor y Davies–Bouldin menor son preferibles; no prueban perfiles naturales. ARI cercano a 1 indica concordancia de asignaciones, no exactitud. BIC se compara solo entre GMM en la misma representación regional.</p>'
    report += '<h2>Mejor separación entre k=2 y k=5</h2>' + best_k.to_html(index=False, float_format=lambda x: f'{x:.3f}')
    for p in sorted(OUT.glob('*.png')):
        report += f'<figure><img src="{p.name}" alt="{escape(p.stem)}"></figure>'
    report += '''<h2>Interpretación y posibles acciones</h2><p>Describir primero las combinaciones visibles en cada matriz; evitar convertir el perfil en una regla universal por edad o sexo. Los segmentos de menor participación pueden orientar investigación cualitativa sobre barreras y pruebas piloto de educación cívica. Los de mayor participación pueden orientar acciones de continuidad e intercambio de experiencias. Los datos no establecen qué mensajes funcionan: las estrategias son hipótesis que deben validarse con evaluación.</p>
    <h2>Límites</h2><p>Son cortes repetidos de grupos de edad, no seguimiento de las mismas personas. El tipo de sección corresponde a cada año. Las mezclas regionales y demográficas pueden cambiar. Al sumar municipios se oculta heterogeneidad local; contrastar después dentro de entidades. No atribuir causas ni inferir comportamientos individuales. Falta cotejar la consolidación con originales. Una diferencia de tasas entre perfiles es esperable porque esas tasas entran al modelo; no es evidencia independiente.</p>
    <p>Fuentes metodológicas: <a href="https://scikit-learn.org/stable/modules/clustering.html">clustering</a> y <a href="https://scikit-learn.org/stable/modules/mixture.html">mezclas gaussianas</a>, scikit-learn.</p></html>'''
    (OUT / 'informe_sociodemografico.html').write_text(report, encoding='utf-8')
    print('Resultados:', OUT, flush=True)


if __name__ == '__main__':
    main()
