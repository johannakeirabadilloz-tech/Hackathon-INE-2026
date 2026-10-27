# Centro de Inteligencia y Visualizaci?n de Informaci?n para el An?lisis Electoral

Proyecto para el **Hackathon INE 2026**. El nombre es provisional.

El proyecto busca facilitar la exploraci?n y el an?lisis de la participaci?n electoral mediante un centro de extracci?n, transformaci?n y carga (ETL), normalizaci?n, limpieza y visualizaci?n de datos abiertos del Instituto Nacional Electoral (INE).

## Objetivo

Transformar los archivos originales en informaci?n consistente y trazable para analizar la participaci?n por a?o, entidad federativa, municipio, sexo, grupo de edad y tipo de secci?n electoral.

## Alcance previsto

- Ingesta de archivos CSV contenidos en los ZIP originales.
- Limpieza y normalizaci?n de textos, tipos de datos y valores faltantes.
- Validaci?n de conteos y generaci?n de reportes de calidad.
- Consolidaci?n municipal y agrupaci?n anal?tica en tres regiones: norte, centro y sur.
- Visualizaci?n de patrones y comparaciones de participaci?n electoral.

Estas funcionalidades describen el alcance del proyecto; este repositorio contiene por ahora los archivos fuente y esta documentaci?n.

## Datos originales

Se incluyen seis paquetes de Conteos Censales de Participaci?n Ciudadana del INE, correspondientes a **2009, 2012, 2015, 2018, 2021 y 2024**. Cada paquete contiene 32 CSV, uno por entidad federativa, y un diccionario de campos.

Los ZIP se conservan sin modificaciones en `data/raw/`.

| Campo | Significado |
| --- | --- |
| LN | Lista nominal |
| SV | Registros con marca de voto |
| NV | Registros sin marca de voto |
| NS | Registros con participaci?n no especificada |

La validaci?n de consistencia considera `LN = SV + NV + NS`. Los registros no especificados deben conservarse como una categor?a independiente al analizar la participaci?n.

Seg?n los diccionarios incluidos en los paquetes, la fuente son los cuadernillos de las listas nominales; no contempla la participaci?n en casillas especiales ni el voto desde el extranjero. Estos conteos no equivalen a resultados por partido o candidatura.

## Criterios de an?lisis

La regionalizaci?n en norte, centro y sur es una **propuesta propia del proyecto basada en informaci?n del INEGI**; no constituye una divisi?n oficial del INEGI. La referencia espec?fica utilizada queda pendiente de documentar.

En el maestro local, la participaci?n se calcula como `SV / (SV + NV) ? 100`. Si el denominador es cero, el porcentaje queda sin valor. Para consolidar grupos se suman primero los conteos y despu?s se recalcula el porcentaje.

## Organizaci?n

```text
data/
  raw/          # ZIP originales incluidos en el repositorio
  processed/    # Maestro y datos procesados: solo locales, ignorados por Git
  catalogs/     # Diccionarios de trabajo: solo locales, ignorados por Git
```

El dataset maestro y el diccionario de regiones permanecen exclusivamente en el entorno local y no se publican en este repositorio.

## Equipo desarrollador

- Valeria Jahzeel Casta?on Hernandez
- Johanna Keira Badillo Zavala
- Ernesto Mendieta Cuecuecha
- Rodrigo Paredes Urrusquieta
