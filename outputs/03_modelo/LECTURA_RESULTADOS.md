# Experimento 3 · Modelo explicativo (regresión logística binomial)

**Conclusión.** La edad es el factor que más asocia con la participación (33% de la variación entre celdas por sí sola), seguida de la elección (26%), la entidad (11%), el sexo (8%) y el tipo de sección (1.5%). Con todo lo demás igual, las mujeres participan 7.8 puntos más que los hombres (IC 95%: 7.2 a 8.4) y los de 60-69 años participan 18.0 puntos más que los de 30-39 (17.0 a 18.8); los de 25-29, 6.4 puntos menos. El efecto del sexo cambia de signo con la edad y la ventaja rural casi desaparece en 2024. Son asociaciones: no identifican causas.

## Modelo

Variable: conteos SV (votaron) y NV (no votaron) por celda elección × entidad × tipo de sección × sexo × grupo de edad (8,064 celdas, 32 entidades). Logit binomial. Errores estándar robustos agrupados por entidad (32 grupos, pocos: se interpretan con cautela) y, para los efectos en puntos, intervalos por bootstrap de entidades (150 réplicas, todas válidas). Se excluyó a no binario (105 filas, solo 2024).

## Cuánto explica cada factor (`tablas/mod_01_factores.csv`)

Medida: devianza explicada (pseudo-R²) frente al modelo sin factores.

| Factor | Solo | Incremento secuencial* | Aporte al añadirlo al final |
| --- | --- | --- | --- |
| Elección | 26.0% | 26.0% | 26.1% |
| Edad | 33.3% | 33.0% | 33.0% |
| Sexo | 8.4% | 8.1% | 8.1% |
| Tipo de sección | 1.5% | 2.0% | 2.0% |
| Entidad | 10.9% | 11.3% | 11.3% |

*Orden: elección, edad, sexo, tipo, entidad; acumulado 26.0%, 58.9%, 67.0%, 69.0%, 80.4%. Los aportes cambian poco según el orden en que se añaden los factores. "Explicado" se mide sobre las 8,064 celdas; la variación dentro de cada celda (secciones, personas) no entra.

## Interacciones (`tablas/mod_02_interacciones.csv`)

Todas significativas por prueba de Wald robusta (p < 0.001), pero con tamaño distinto: ganancia de devianza explicada, sobre el modelo de efectos principales (80.4%): elección × entidad 9.7 puntos (155 parámetros), sexo × edad 3.1, elección × edad 0.9, elección × tipo 0.9, edad × tipo 0.4, sexo × tipo 0.2, elección × sexo 0.1. Modelo final (efectos principales + sexo × edad, elección × edad, elección × sexo, elección × tipo): 85.4%. No incluye elección × entidad, que es la interacción más grande (se omitió por su número de parámetros): el territorio cambia entre elecciones.

## Sobredispersión

Pearson χ²/gl = 957 (efectos principales) y 716 (modelo final): muy por encima de 1. Hay mucha variación entre secciones y personas dentro de cada celda que el binomial no recoge. Por eso las inferencias usan errores robustos agrupados / bootstrap por entidad, no los del modelo binomial; con 32 grupos, los intervalos pueden quedar angostos.

## En puntos porcentuales (efectos marginales promedio; `tablas/mod_03_efectos_pp.csv`)

| Comparación (mismo resto de factores) | Puntos | IC 95% |
| --- | --- | --- |
| Mujeres vs hombres | +7.8 | 7.2 a 8.4 |
| 18-24 vs 30-39 | −3.4 | −4.2 a −2.8 |
| 25-29 vs 30-39 | −6.4 | −7.0 a −6.1 |
| 40-49 vs 30-39 | +8.4 | 8.1 a 8.6 |
| 50-59 vs 30-39 | +13.9 | 13.4 a 14.4 |
| 60-69 vs 30-39 | +18.0 | 17.0 a 18.8 |
| 70+ vs 30-39 | +8.7 | 7.2 a 10.1 |
| Elección 2024 vs 2018 | −3.4 | −4.4 a −2.3 |
| Elección 2024 vs 2021 | +7.5 | 4.9 a 9.5 |
| Brecha M−H en 2024 a los 18-24 / 30-39 / 60-69 / 70+ | +10.3 / +13.5 / +2.2 / −4.4 | — |
| Rural vs urbana, 2015 | +10.4 | 7.6 a 13.6 |
| Rural vs urbana, 2024 | +0.9 | −2.0 a 3.8 (incluye 0) |

Los efectos de edad, sexo y tipo "promedio" son sobre todas las elecciones; los marcados con año son específicos. La diferencia 2024 vs 2018 (−3.4) con composición ajustada es mayor que la nacional observada (−2.7); la diferencia viene de igualar la composición (sexo, edad, entidad, tipo de sección), no se investigó su causa.

**Contraste con la descripción.** La brecha M−H por edad en 2024 según el modelo (10.3, 13.3, 13.5, 11.0, 7.4, 2.2, −4.4) coincide con la descriptiva (10.3, 13.3, 13.7, 11.6, 7.6, 2.1, −5.4), con diferencias de hasta 1.1 puntos en 70+ y 0.6 en 40-49.

## Límites

- Asociaciones transversales sobre grupos; no hay causas, motivos ni conducta individual.
- Entidad y año se modelan como efectos fijos; no hay variables socioeconómicas (el INE no las incluye aquí).
- Pocos grupos (32) para errores agrupados; el bootstrap por entidad es la verificación más conservadora disponible.
