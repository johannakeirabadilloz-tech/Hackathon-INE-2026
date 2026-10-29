# Centro de Inteligencia y Visualización de Información para el Análisis Electoral

Proyecto para el **Hackathon INE 2026 · Reto 1: Perfiles ciudadanos de participación**. El nombre del proyecto es provisional.

Buscamos identificar quiénes participan, qué características comparten, dónde se presentan diferencias y qué estrategias podrían contribuir a aumentar la participación ciudadana en México.

## Contexto del reto

El Reto 1 propone estudiar los patrones electorales de distintos grupos poblacionales para construir perfiles que ayuden a comprender su participación y plantear estrategias para incentivarla. Nuestro proyecto aborda este reto mediante análisis histórico, territorial y demográfico.

Fuente oficial: [Hackathon INE 2026](https://www.ine.mx/hackathon-2026/).

## Objetivo general

Desarrollar una plataforma inteligente de análisis de participación electoral, mediante técnicas de ciencia de datos, estadística y aprendizaje automático, que permita identificar, caracterizar y comparar perfiles de participación y abstención ciudadana en México, utilizando información histórica de los procesos electorales de 2009 a 2024, con el propósito de generar hallazgos y recomendaciones basadas en evidencia que contribuyan al diseño de estrategias focalizadas para fortalecer la participación democrática.

## Objetivos específicos

1. Identificar perfiles de participación electoral mediante variables sociodemográficas y territoriales, como sexo, grupo de edad, entidad federativa, municipio y tipo de sección electoral.
2. Analizar patrones históricos de participación y abstención electoral durante el periodo 2009–2024.
3. Comparar diferencias regionales entre norte, centro y sur, identificando características comunes y diferencias entre los grupos poblacionales.
4. Implementar técnicas de segmentación, como clustering, para identificar grupos con comportamientos electorales similares.
5. Generar hallazgos e interpretaciones sobre qué grupos presentan mayores o menores tasas de participación y cómo varían territorialmente.
6. Proponer estrategias focalizadas de educación cívica, comunicación y promoción de la participación ciudadana, sustentadas en los perfiles identificados.

## Enfoque técnico previsto

1. **Datos históricos del INE:** seis procesos electorales de 2009 a 2024 y un dataset maestro local de 546,968 registros agregados.
2. **Procesamiento y análisis:** ETL, normalización, limpieza, validación de conteos, construcción de indicadores y segmentación territorial y demográfica.
3. **Construcción de perfiles ciudadanos:** estadística multivariada y aprendizaje no supervisado para explorar grupos con comportamientos similares.
4. **Exploración interactiva:** visualizaciones, comparación de perfiles y presentación de hallazgos.
5. **Recomendaciones estratégicas:** propuestas diferenciadas de educación cívica, comunicación y promoción de la participación, sustentadas en los resultados del análisis.

La etapa de exploración ya cuenta con una segmentación sociodemográfica y resultados publicados. La plataforma interactiva y la validación adicional siguen dentro del alcance previsto.

## Resultados de la segmentación sociodemográfica

El análisis agrupa 144 segmentos definidos por región, sexo, grupo de edad y tipo de sección, comparando su participación en seis elecciones. Se presentan dos perfiles por región, con nombres descriptivos, composición exacta e indicadores históricos.

- [Seis fichas completas: dos perfiles por región](reports/sociodemografico/fichas_dos_perfiles_por_region.md).
- [Informe con gráficas y metodología](reports/sociodemografico/informe_sociodemografico.html). Para visualizarlo, descargar el repositorio y abrir este HTML en un navegador, conservando los PNG en la misma carpeta.
- [Todos los plots y tablas de resultados](reports/sociodemografico/).
- [Instrucciones para reproducir el análisis](scripts/README.md).

Los archivos CSV de esta carpeta son resultados agregados del análisis; el dataset maestro y el diccionario de trabajo permanecen locales. Los perfiles son exploratorios y no identifican personas ni causas de participación. La categoría no binario se describe aparte por disponer únicamente de registros de 2024.

## Preguntas que buscamos responder

- ¿Qué perfiles demográficos presentan menor participación electoral?
- ¿Existen patrones similares entre municipios de distintas entidades?
- ¿La participación de mujeres y hombres muestra diferencias según la edad y la región?
- ¿Qué características distinguen a los territorios con mayor participación?
- ¿Qué estrategias podrían ser más pertinentes para cada perfil identificado?

Los perfiles serán **estadísticos y agregados**. Las unidades de análisis son grupos poblacionales y territorios; los resultados no describen el comportamiento de votantes individuales. Las diferencias y asociaciones observadas no permiten atribuir causas sin evidencia adicional.

## Datos originales

Se incluyen seis paquetes de Conteos Censales de Participación Ciudadana del INE, correspondientes a **2009, 2012, 2015, 2018, 2021 y 2024**. Cada paquete contiene 32 CSV, uno por entidad federativa, y un diccionario de campos.

Los ZIP se conservan sin modificaciones en `data/raw/`.

| Campo | Significado |
| --- | --- |
| LN | Lista nominal |
| SV | Registros con marca de voto |
| NV | Registros sin marca de voto |
| NS | Registros con participación no especificada |

La validación de consistencia considera `LN = SV + NV + NS`. Los registros no especificados se conservan como una categoría independiente y no se contabilizan como abstención.

Según los diccionarios incluidos en los paquetes, la fuente son los cuadernillos de las listas nominales; no contempla la participación en casillas especiales ni el voto desde el extranjero. Estos conteos no equivalen a resultados por partido o candidatura.

## Criterios de análisis

La [distribución de las 32 entidades en las tres regiones](docs/regionalizacion_tres_regiones.md) documenta las claves, la asignación y su uso en los análisis.

La regionalización en norte, centro y sur es una **propuesta propia del proyecto basada en información del INEGI**; no constituye una división oficial del INEGI. La referencia específica utilizada queda pendiente de documentar.

En el maestro local, la participación se calcula como `SV / (SV + NV) × 100`: participación entre registros con situación especificada. Si el denominador es cero, el porcentaje queda sin valor. Para consolidar grupos se suman primero los conteos y después se recalcula el porcentaje. El porcentaje de registros no especificados se analiza por separado para contextualizar los resultados.

## Organización

```text
data/
  raw/          # ZIP originales incluidos en el repositorio
  processed/    # Maestro y datos procesados: solo locales, ignorados por Git
  catalogs/     # Diccionarios de trabajo: solo locales, ignorados por Git
reports/
  sociodemografico/  # Resultados autorizados para publicación
  local/            # Resultados de ejecución local, ignorados por Git
scripts/            # Análisis reproducible
```

El dataset maestro y el diccionario de regiones permanecen exclusivamente en el entorno local y no se publican en este repositorio.

## Equipo desarrollador

- Valeria Jahzeel Castañon Hernandez
- Johanna Keira Badillo Zavala
- Ernesto Mendieta Cuecuecha
- Rodrigo Paredes Urrusquieta
