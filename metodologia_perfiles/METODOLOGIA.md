# Metodología de los perfiles de participación por sexo y edad

Esta carpeta reúne **solo** lo necesario para obtener y revisar los cuatro perfiles: los scripts, las tablas que producen, las figuras y este documento. Los resultados explicados y su interpretación están en [reports/perfiles_sexo_edad/README.md](../reports/perfiles_sexo_edad/README.md); aquí se describe **cómo se obtuvieron**.

Los perfiles describen participación observada en grupos agregados (sexo × edad), no a personas ni sus motivos.

---

## 1. Datos de entrada

| Dato | Origen |
|---|---|
| Conteos de participación 2009, 2012, 2015, 2018, 2021 y 2024 | Seis paquetes del INE en `data/raw/` (un CSV por entidad y elección) |
| Tabla de trabajo `data/processed/conteos_seccion_sexo_edad.parquet` | Generada por `scripts/01_etl_calidad.py` a partir de los ZIP, **sin eliminar filas** (54,872,712 filas) |
| Regionalización norte / centro / sur | `REGIONES_A` en `scripts/config.py`: propuesta del proyecto, **no** una división oficial |

Cada fila original es una sección electoral × sexo × edad × elección, con cuatro conteos:

- `LN`: lista nominal.
- `SV`: registros con marca de voto.
- `NV`: registros sin marca de voto.
- `NS`: registros con participación no especificada. Se cumple `LN = SV + NV + NS`.

`data/processed/` está ignorado por Git: hay que generarlo (paso 0 de la sección 7).

## 2. Variable de participación

```
participación = 100 × SV / (SV + NV)
```

Los no especificados (`NS`) **no entran al numerador ni al denominador**: no se cuentan como voto ni como abstención. Al agregar grupos se suman primero los conteos y después se calcula el porcentaje (no se promedian porcentajes).

## 3. Qué se excluye y por qué

| Exclusión | Motivo | Peso |
|---|---|---|
| Personas no binarias (`SEXO = 2`) | El INE solo registra esta categoría en 2024 (105 registros); sin historial no hay trayectoria | 0.0001% de la lista nominal de 2024 |
| Edades de 100 años o más | El original llega a 140 años; probables errores de registro | ≈0.02% de la lista nominal |
| Menores de 18 años | No hay filas (la lista nominal parte de 18 años) | 0 |

Todo lo demás se conserva, incluidos los no especificados (con su prueba de sensibilidad, sección 6).

## 4. Obtención de los perfiles (`scripts/17_perfiles_edad_sexo.py`)

### 4.1 Unidad de análisis
**164 segmentos nacionales** = 2 sexos × 82 edades simples (18 a 99 años). Para cada segmento se suman los conteos de todo el país.

### 4.2 Variables de agrupamiento
Un vector de **6 valores** por segmento: su participación en cada elección (2009, 2012, 2015, 2018, 2021 y 2024). Describen la *trayectoria* del segmento, no un solo año.

### 4.3 Preparación
- Estandarización (`StandardScaler`): cada elección se centra y se escala sobre los 164 segmentos. Así ninguna elección pesa más que otra por tener mayor varianza.
- **Cada segmento pesa igual en el agrupamiento**, sin importar cuántas personas tenga. El tamaño se usa solo para describir los perfiles (participación ponderada por votantes y porcentaje de lista nominal).

### 4.4 Algoritmos y número de perfiles
Se compararon **k-means** (30 inicializaciones, semilla 42) y **Ward** (jerárquico) para `k = 2, …, 6`, con tres criterios:

| Criterio | Qué mide |
|---|---|
| Silhouette | Qué tan separados y compactos quedan los grupos (en datos estandarizados) |
| Tamaño mínimo | Proporción de segmentos del grupo más pequeño |
| Estabilidad (ARI) | 20 submuestras del 80% de los segmentos, sin reemplazo; se reagrupa y se compara con el agrupamiento completo con el índice de Rand ajustado (1 = idéntico, 0 = azar). Se reportan media y mínimo |

Resultados con k-means (`tablas/perfiles_edad_sexo_comparacion.csv`):

| k | Silhouette | ARI medio | ARI mínimo |
|---|---|---|---|
| 2 | **0.605** | 0.897 | 0.636 |
| 3 | 0.593 | **0.966** | 0.852 |
| 4 | 0.566 | 0.959 | 0.817 |
| 5 | 0.518 | 0.889 | 0.759 |
| 6 | 0.505 | 0.916 | 0.781 |

Ward resultó menos estable (por ejemplo, con k = 4 el ARI mínimo es 0.42) y se descartó.

**Decisión: k = 4, con k-means (50 inicializaciones, semilla 42).** Es una decisión de criterio: la silhouette favorece k = 2, pero ese resultado es el menos estable, y con 3 y 4 grupos aparecen estructuras que k = 2 mezcla (los muy mayores y la diferencia por sexo). No se afirma que existan exactamente cuatro tipos.

### 4.5 Numeración y descripción de los perfiles
Los perfiles se ordenan de mayor a menor participación en 2024 (1 = alta, 4 = muy mayores). Para cada uno se reporta (`scripts/20_figuras_perfiles.py`):

- los rangos de edad por sexo (`tablas/composicion_perfiles.csv`);
- su participación en cada elección, ponderada por votantes más no votantes (`tablas/trayectorias_perfiles.csv`);
- su porcentaje de la lista nominal de 2024.

## 5. Comparación por región y tipo de sección (`scripts/18_perfiles_por_region_tipo.py`)

**Pregunta:** ¿los perfiles son los mismos en todos los lugares, o cambian por región o por tipo de sección (urbana, mixta, rural)?

Se repite la tabla de participación (sexo × edad × elección) en **15 cortes**: 3 regiones, 3 tipos de sección y 9 combinaciones región × tipo. Para cada corte, frente a la curva nacional (ponderada por el tamaño del segmento), se calcula:

| Métrica | Definición |
|---|---|
| `nivel_vs_nacional_pts` | Diferencia promedio en puntos porcentuales |
| `rmse_total_pts` | Raíz del error cuadrático medio frente a la curva nacional |
| `rmse_sin_nivel_pts` | Lo que queda al quitar el nivel: `√(rmse_total² − nivel²)`. Recoge diferencias en el patrón por edad y de una elección a otra. Descomposición exacta |
| `ari_perfiles_propios_vs_nacional` | ARI entre los 4 perfiles obtenidos agrupando solo dentro del corte y los perfiles nacionales |
| `perfilK_2024` | Participación 2024 del corte dentro de cada perfil nacional |

Además se calcula cuánto de la variación de las celdas explica la curva nacional (R² ponderado), y cuánto cuando se suma un nivel propio por grupo y elección. Resultados (`tablas/perfiles_region_tipo_comparacion.csv`):

| Corte | Nivel (pts) | Tras quitar el nivel (pts) | ARI |
|---|---|---|---|
| Norte | −3.7 | 1.5 | 0.99 |
| Centro | +1.0 | 1.1 | 0.94 |
| Sur | +2.3 | 2.7 | 0.83 |
| Urbana | −1.1 | 1.2 | 0.93 |
| Mixta | +0.3 | 1.4 | 0.93 |
| Rural | +4.1 | 3.6 | 0.73 |
| Sur rural | +6.7 | 4.8 | 0.64 |

- R² con la curva nacional: 0.949 (regiones) y 0.954 (tipos). Con un nivel propio por grupo y elección: 0.996 y 0.989.
- **El orden de los perfiles se conserva en todos los cortes**: el perfil 1 siempre participa más que el 2, el 2 más que el 3 y el 3 más que el 4.

**Conclusión metodológica:** en el norte, el centro, las secciones urbanas y las mixtas, el lugar mueve sobre todo el nivel, así que se trata como un ajuste y no como perfiles distintos. El sur y las secciones rurales (sobre todo el sur rural) son una excepción, porque lo que queda tras quitar el nivel es del mismo orden que el nivel.

**Cuidado con el R²:** como la edad domina tanto la variación, un R² alto no significa que 4 a 7 puntos de diferencia sean irrelevantes.

## 6. Pruebas de robustez (`scripts/19_revision_ns_nobinario.py`)

| Prueba | Resultado |
|---|---|
| Contar los no especificados como "no votó" (`SV / LN` en vez de `SV / (SV + NV)`) | Ningún segmento cambia de perfil (ARI = 1.0); `tablas/perfiles_sensibilidad_ns.csv` queda vacío porque no hay cambios |
| Quitar 2009 (elección con pocos no especificados, 2.4%) | ARI = 0.939 frente a los perfiles principales |
| Usar solo las presidenciales (2012, 2018 y 2024) | ARI = 0.913 |

Los no especificados representan entre 0.2% (2012) y 6.8% (2018) de la lista nominal y **no se concentran en ninguna edad ni sexo** (diferencia máxima de unos 0.7 puntos entre tramos de edad dentro de un año, y de 0.1 entre hombres y mujeres). Lo que no se puede saber es cuántos de ellos votaron: la participación de las elecciones con más no especificados es más incierta, aunque esa incertidumbre afecta a todos los grupos por igual.

Resultados en `tablas/sensibilidad_perfiles.csv`, `tablas/ns_pct_por_eleccion_y_tramo.csv` y `tablas/no_binario_registros.csv`.

## 7. Cómo reproducir

Desde la raíz del repositorio, con el entorno `.venv` (dependencias en `requirements-analysis.txt`: `pandas`, `numpy`, `scikit-learn`, `matplotlib` y `pyarrow`) y los ZIP de `data/raw/`:

```bash
cd metodologia_perfiles/scripts

# 0. Generar data/processed/conteos_seccion_sexo_edad.parquet (solo si no existe; tarda varios minutos)
python 01_etl_calidad.py

# 1. Perfiles nacionales por sexo y edad
python 17_perfiles_edad_sexo.py

# 2. Comparación por región y tipo de sección
python 18_perfiles_por_region_tipo.py

# 3. No especificados, no binarios y sensibilidad
python 19_revision_ns_nobinario.py

# 4. Figuras y tablas finales
python 20_figuras_perfiles.py
```

Los scripts escriben en `tablas/` y `figuras/` de esta carpeta. El orden importa: el script 20 lee los resultados del 17 y el 18. Semilla fija: 42. Los resultados se verificaron repitiendo los scripts desde esta carpeta, con tablas idénticas a las publicadas.

> `scripts/01_etl_calidad.py` escribe además `calidad_hallazgos.json` y `calidad_por_eleccion.csv` en `tablas/`; son el reporte de calidad de los datos originales (no es necesario para los perfiles).

## 8. Contenido de la carpeta

### Scripts (`scripts/`)

| Archivo | Función |
|---|---|
| `config.py` | Rutas, años y regionalización (`REGIONES_A`) |
| `estilo.py` | Paleta de colores y formato de las gráficas |
| `01_etl_calidad.py` | Lee los ZIP originales y genera la tabla de trabajo sin eliminar filas |
| `17_perfiles_edad_sexo.py` | Comparación de k = 2 a 6 y agrupamiento en 4 perfiles |
| `18_perfiles_por_region_tipo.py` | Comparación de los perfiles por región y tipo de sección |
| `19_revision_ns_nobinario.py` | Revisión de no especificados, no binarios y sensibilidad |
| `20_figuras_perfiles.py` | Figuras finales y tablas de composición y trayectorias |

### Tablas (`tablas/`)

| Archivo | Contenido |
|---|---|
| `perfiles_edad_sexo_comparacion.csv` | Silhouette, tamaño mínimo y ARI para k = 2 a 6 (k-means y Ward) |
| `perfiles_edad_sexo_k4_asignacion.csv` | Participación en cada elección de los 164 segmentos y su perfil (con la etiqueta numérica interna del agrupamiento) |
| `asignacion_segmentos_sexo_edad.csv` | Lo mismo, con el número de perfil final (1 a 4) |
| `composicion_perfiles.csv` | Rangos de edad de cada perfil por sexo |
| `trayectorias_perfiles.csv` | Participación por perfil y elección, y % de lista nominal |
| `perfiles_region_tipo_comparacion.csv` | Nivel, error y ARI por región, tipo y combinación |
| `sensibilidad_perfiles.csv` | Pruebas de robustez (no especificados, sin 2009, solo presidenciales) |
| `perfiles_sensibilidad_ns.csv` | Segmentos que cambian de perfil al contar los no especificados como no voto (vacío: ninguno) |
| `ns_pct_por_eleccion_y_tramo.csv` | % de no especificados por elección y tramo de edad |
| `brecha_sexo_edad_2024.csv` | Participación de hombres y mujeres por edad en 2024, y su diferencia |
| `no_binario_registros.csv` | Registros de personas no binarias (solo 2024) |

### Figuras (`figuras/`)

| Archivo | Muestra |
|---|---|
| `perfiles_edad_sexo_k4.png` | Participación 2024 por edad y sexo, coloreada por la etiqueta interna del agrupamiento |
| `fig1_perfiles_por_sexo_y_edad.png` | Perfil de cada sexo y edad, con la participación 2024 |
| `fig2_trayectorias.png` | Trayectoria de cada perfil, 2009–2024 |
| `fig3_ajuste_por_lugar.png` | Nivel por región y tipo de sección |
| `fig4_no_especificados.png` | % de no especificados por elección |
| `fig5_curvas_por_region_y_tipo.png` | Curvas de participación 2024 por región y tipo |
| `fig6_brecha_por_sexo_y_edad.png` | Diferencia entre mujeres y hombres por edad, 2024 |

## 9. Verificación previa de los datos

Antes de este análisis se comparó el **dataset maestro municipal** del proyecto contra los conteos originales: coinciden celda por celda (546,968 celdas, sin diferencias en lista nominal, votos, no votos, no especificados ni registros de origen). Los perfiles se calculan directamente de los conteos originales con edad simple, no del maestro, porque este solo trae grupos de edad (18-24, 25-34, …, 85+) y las edades de 100 años o más están incluidas en el 85+.

## 10. Límites

- **No hay causas.** Son datos agregados de grupos, sin motivos, escolaridad ni ingreso.
- **Los límites entre perfiles no son umbrales naturales.** La participación cambia de forma continua con la edad; los perfiles son cortes de esa curva y dependen del método y de k.
- **Edad, periodo y cohorte no se pueden separar.** Los segmentos no son las mismas personas a lo largo del tiempo.
- **Cada segmento pesa igual en el agrupamiento,** aunque algunos (muy mayores) tengan muy pocas personas.
- **Los muy mayores pueden estar mal medidos.** El padrón podría incluir personas fallecidas o que ya no residen en su sección. No se verificó con estos datos.
- **Las regiones son una propuesta del proyecto,** no una división oficial.
- **El análisis es nacional.** No sustituye el estudio por municipio, donde la brecha entre grupos de edad varía mucho.
- **No hay validación externa.**
