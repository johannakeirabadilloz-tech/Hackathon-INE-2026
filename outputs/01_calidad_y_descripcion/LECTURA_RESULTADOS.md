# Experimento 1 · Calidad de los datos y descripción

**Conclusión.** Los conteos están aritméticamente limpios (en las 54.9 millones de filas, `LN = SV + NV + NS`), así que el análisis se apoya en datos consistentes. La participación (sobre registros con situación conocida) sube en elecciones presidenciales (62.1% en 2012, 62.4% en 2018, 59.7% en 2024) y cae en las intermedias (44.1% en 2009, 47.1% en 2015, 51.8% en 2021). Las mujeres participan más que los hombres en todas las elecciones, y esa diferencia **no** se debe a la edad: pasa de 6.3 a 9.3 puntos al igualar la estructura de edad, y se invierte a partir de los 70 años. De 2018 a 2024 la participación bajó en menores de 60 años y subió en mayores de 60.

## 1. Datos y calidad (se reporta, no se corrige)

Fuente: seis Conteos Censales de Participación del INE (2009–2024), 32 CSV por elección; nivel sección × sexo × edad simple. Tabla de trabajo: 54,872,712 filas. Los ZIP originales no se modificaron.

| Verificación | Resultado |
| --- | --- |
| `LN = SV + NV + NS` | Se cumple en todas las filas de las 6 elecciones |
| Duplicados en la llave (elección, entidad, municipio, sección, sexo, edad) | 0 |
| Valores vacíos o no numéricos | 0 |
| Valores negativos / `SV > LN` | 0 / 0 |
| Edad | 18 a 140 años; 91,629 filas con edad > 100 (0.01%–0.04% de la lista nominal; participación de ese grupo 3%–18%, muy por debajo del total). **Se conservan**; caen dentro del grupo 70+ |
| Tamaño máximo de fila | LN máx. 982; p99.9 = 141; 5,406 filas sobre el p99.99. Plausibles en secciones grandes; no se tocaron |
| Sexo = 2 (no binario) | 105 filas, solo en 2024. Se excluyen del análisis (no hay serie) |
| Sección que cambia de tipo (U/M/R) entre elecciones | 1,617 secciones. Se usa el tipo de cada año |
| Filas con `SV + NV = 0` (tasa indefinida) | 0.1% (2012) a 3.9% (2018) de las filas; en agregados no afecta porque se suman conteos |

Archivo: `tablas/calidad_hallazgos.json`, `tablas/calidad_por_eleccion.csv`, `tablas/calidad_edades_extremas.csv`.

**Lo que no pude verificar:** el maestro local (546,968 registros según el README) no estaba disponible, así que no lo cotejé contra los originales; todo se reconstruyó desde los ZIP. El cubo usado aquí (478,917 filas por municipio × tipo × sexo × grupo de edad × elección) no es comparable con ese maestro.

## 2. Métricas y cuándo engañan

| Métrica | Fórmula | Cuándo engaña |
| --- | --- | --- |
| **Participación** (principal) | SV / (SV + NV) | Excluye NS. Si NS no es aleatorio (se concentra en algunas entidades) sesga comparaciones |
| Sobre lista nominal | SV / LN | Trata NS como abstención. Penaliza a entidades con muchos NS (cuadernillos no capturados), que no son abstención |
| % NS | NS / LN | Es una medida de captura de la fuente, no de comportamiento |

La diferencia entre las dos primeras crece con NS: 1.1 puntos en 2009, 0.1 en 2012, 2.9 en 2015, 4.3 en 2018, 2.2 en 2021, 3.8 en 2024 (`tablas/eda_01_nacional_por_eleccion.csv`). NS pasa de 0.2% (2012) a 6.1%–6.8% (2015, 2018, 2024); en 2024 llega a 14.9% en Chihuahua y Campeche y 14.5% en Coahuila, frente a 1.9% en Ciudad de México. Por eso las comparaciones entre elecciones y entidades se hacen sobre registros con situación conocida y se advierte la sensibilidad.

Además: la lista nominal no equivale a la población adulta (incluye personas que ya no residen o fallecieron; sugerido por la baja participación en edades > 100, **no demostrado**), y la fuente excluye casillas especiales y voto en el extranjero (según el diccionario de campos). Todos los agregados suman conteos y recalculan la tasa.

## 3. Hallazgos descriptivos

Estandarización directa: pesos = distribución de la lista nominal (todas las elecciones) por grupo de edad (para sexo) o por sexo × edad (para entidad, región y tipo de sección). Es un supuesto; cambiarla a los pesos de 2024 mueve la brecha de sexo de 6.3–9.3 a 6.0–9.0 puntos, sin cambiar la conclusión.

1. **Ciclo electoral.** Presidenciales vs intermedias (clasificación conocida, no proviene de los datos): ver arriba. Figura `01_participacion_nacional.png`.
2. **Sexo.** Brecha mujeres − hombres: 6.8 → 9.4 puntos observada; 6.3 → 9.3 con misma estructura de edad (2009–2024; 2024 es el valor más alto, 9.3 vs 7.5–7.9 en 2012–2021). La edad explica una parte pequeña. `02_brecha_sexo.png`.
3. **El promedio oculta una inversión.** Por edad, en 2024 la brecha es +10.3 (18-24), +13.3 (25-29), +13.7 (30-39), +11.6 (40-49), +7.6 (50-59), +2.1 (60-69) y **−5.4 (70+)**: entre los 70+ participan más los hombres, en las seis elecciones. `03_brecha_sexo_edad.png`.
4. **Edad.** La participación sube con la edad hasta 60-69; los 25-29 años son los más bajos en todas las elecciones. De 2018 a 2024: −4.4 (18-24), −5.6 (25-29), −6.0 (30-39), −4.2 (40-49), −2.2 (50-59), +1.5 (60-69), +4.5 (70+); total −2.7. `04_cambio_edad_2018_2024.png`.
5. **Entidad.** En 2024, de 46.7% (Baja California) a 71.1% (Yucatán), 24.4 puntos de rango con sexo y edad igualados. Igualar sexo y edad cambia el orden en más de 3 lugares solo en 1 de 32 entidades: la composición explica poco de las diferencias territoriales. `05_entidades_2024.png`.
6. **Región (propuesta propia, ver supuestos).** Con sexo y edad igualados el orden cambia: Sur es primera en 2012 (65.3), 2015 (49.5), 2018 (66.1) y 2021 (57.3), y Centro en 2009 (45.8) y 2024 (61.3); Norte es la más baja en 2012–2024 (54.3 en 2024) y queda empatada con Sur en 2009. `06_regiones_tiempo.png`.
7. **Tipo de sección.** La ventaja rural frente a la urbana pasó de +10.0 puntos en 2015 a +0.8 en 2024 (con sexo y edad igualados). `07_tipo_seccion.png`.

## 4. Supuestos y límites

- Regiones: dos particiones propias en `scripts/config.py` (3 y 5 regiones). **No son oficiales** del INEGI ni del INE; el catálogo del equipo no estaba disponible y no verifiqué ninguna fuente oficial.
- Grupos de edad (18-24, 25-29, 30-39, 40-49, 50-59, 60-69, 70+): decisión mía; editable.
- Lo observado describe grupos y territorios; **no** permite inferir motivos ni conducta individual. Las diferencias por edad son transversales (cada elección), no siguen a personas.
