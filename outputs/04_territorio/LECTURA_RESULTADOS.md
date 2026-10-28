# Experimento 4 · Territorio: ¿una región recoge el efecto de la entidad?

**Conclusión.** Depende de la regionalización. Las 3 regiones (norte, centro, sur) recogen 21% del efecto de entidad, **lo mismo que lograría una partición al azar del mismo tamaño** (percentil 95 del azar: 24%). Las 5 regiones recogen 54%, claramente por encima del azar (p95: 33%). Aun así, dentro de cada región los municipios difieren mucho: el 80% central abarca de 18 a 36 puntos de participación en 2024, y 30% de los municipios de la región con menor mediana (Sur) supera la mediana de la de mayor mediana (Centro).

## Regiones usadas (supuestos, no oficiales)

Definidas en `scripts/config.py`, cada entidad aparece una vez: **A** = Norte (12 entidades), Centro (12), Sur (8); **B** = Noroeste (6), Noreste (5), Occidente y Bajío (7), Centro (6), Sur-Sureste (8). Las propuse yo antes de ver resultados; no son divisiones oficiales y el catálogo del equipo no estaba disponible. No usé la agrupación de circunscripciones del INE porque no pude verificar su composición.

## 1. Captura del efecto de entidad (`tablas/ter_01_captura.csv`, `ter_02_captura_por_eleccion.csv`)

Captura = (devianza explicada al añadir región − sin territorio) / (al añadir entidad − sin territorio), con elección, sexo, edad y tipo de sección como controles. Referencia: 200 particiones al azar con los mismos tamaños.

| | Global | Con territorio cambiante por elección | Azar: mediana | Azar: p95 |
| --- | --- | --- | --- | --- |
| A · 3 regiones | 20.7% | 17.0% | 7.0% | 23.9% |
| B · 5 regiones | 54.1% | 44.8% | 13.6% | 32.7% |

Por elección (A / B): 2009 4% / 15%; 2012 28% / 45%; 2015 4% / 24%; 2018 31% / 76%; 2021 22% / 58%; 2024 28% / 70%. La regionalización recoge mucho más en las presidenciales recientes que en 2009 y 2015.

## 2. Variación dentro de la región con municipios (`tablas/ter_03_descomposicion_municipal.csv`, `ter_04_dispersion_dentro_region.csv`)

Participación municipal ajustada por sexo y edad (estandarización indirecta frente a las tasas nacionales de cada elección); municipios con ≥ 300 registros con situación conocida (supuesto; 2,441 en 2024). Descomposición de la varianza ponderada por registros, 2024:

| | Entre regiones | Entre entidades dentro de la región | Entre municipios dentro de la entidad |
| --- | --- | --- | --- |
| A (3) | 14.2% | 34.7% | 51.1% |
| B (5) | 34.8% | 14.2% | 51.1% |

La varianza entre municipios dentro de la entidad es entre 42% y 67% del total según la elección. El ruido de muestreo binomial es ≤ 0.2% de la varianza total, así que esa dispersión no es solo azar de conteos pequeños.

Dispersión dentro de región en 2024 (regionalización B; p10–p90): Noroeste 27.7 puntos; Occidente y Bajío 19.2; Sur-Sureste 36.3; Noreste 22.3; Centro 17.8. En la regionalización A: Centro 23.3, Norte 25.4, Sur 36.3.

## Límites

- 32 entidades: el "azar" se evalúa con particiones de 32 puntos; la diferencia A vs B también se debe a tener más grupos (el placebo controla eso comparando contra particiones del mismo tamaño).
- B fue diseñada para este análisis; con otra agrupación el resultado puede cambiar. Se puede probar editando `config.py`.
- Que una región "capture" el efecto describe un patrón estadístico, no una explicación; no se identifican causas de la variación entre municipios.
