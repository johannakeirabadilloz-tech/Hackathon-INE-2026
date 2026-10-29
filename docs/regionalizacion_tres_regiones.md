# Regionalización de las 32 entidades federativas

El proyecto agrupa las 32 entidades federativas de México en **tres regiones analíticas: norte, centro y sur**, para comparar la participación electoral y presentar los resultados territoriales.

Es una **propuesta propia del equipo, basada en información del INEGI**. No constituye una regionalización oficial del INEGI ni del INE. La página específica del INEGI utilizada como referencia y la justificación detallada de las asignaciones están pendientes de documentar; la tabla siguiente registra la decisión efectivamente utilizada, sin atribuirle carácter oficial.

## Distribución

| Región | Entidades |
| --- | ---: |
| Norte | 12 |
| Centro | 12 |
| Sur | 8 |
| **Total** | **32** |

## Norte

| Clave de entidad INE | Entidad federativa |
| --- | --- |
| 01 | Aguascalientes |
| 02 | Baja California |
| 03 | Baja California Sur |
| 05 | Coahuila |
| 08 | Chihuahua |
| 10 | Durango |
| 19 | Nuevo León |
| 24 | San Luis Potosí |
| 25 | Sinaloa |
| 26 | Sonora |
| 28 | Tamaulipas |
| 32 | Zacatecas |

## Centro

| Clave de entidad INE | Entidad federativa |
| --- | --- |
| 06 | Colima |
| 09 | Ciudad de México |
| 11 | Guanajuato |
| 13 | Hidalgo |
| 14 | Jalisco |
| 15 | Estado de México |
| 16 | Michoacán |
| 17 | Morelos |
| 18 | Nayarit |
| 21 | Puebla |
| 22 | Querétaro |
| 29 | Tlaxcala |

## Sur

| Clave de entidad INE | Entidad federativa |
| --- | --- |
| 04 | Campeche |
| 07 | Chiapas |
| 12 | Guerrero |
| 20 | Oaxaca |
| 23 | Quintana Roo |
| 27 | Tabasco |
| 30 | Veracruz |
| 31 | Yucatán |

## Cómo se asigna una región

La relación se realiza con la **clave de entidad del INE**: `EDOCVE` en los originales y `entidad_clave` en el maestro. Cada clave pertenece a una sola región. Todos los municipios y segmentos de una entidad heredan esa misma región.

Se usa la clave para evitar diferencias de escritura y nombres históricos. Por ejemplo, **Distrito Federal y Ciudad de México corresponden a la clave 09 y se asignan al centro**. La clave de municipio por sí sola no identifica una entidad ni determina su región.

Las claves se muestran con dos dígitos en esta documentación; en las tablas pueden almacenarse como enteros de 1 a 32. Los valores de región en el maestro son `norte`, `centro` y `sur`; algunos scripts los presentan con inicial mayúscula.

## Implementación y uso en el análisis

- La asignación de tres regiones está implementada como **`REGIONES_A`** en [scripts/config.py de la rama neto-jahzz-combinada](https://github.com/johannakeirabadilloz-tech/Hackathon-INE-2026/blob/neto-jahzz-combinada/scripts/config.py).
- El diccionario de trabajo `data/catalogs/diccionario_regiones.json` permanece local y contiene la misma relación.
- La regionalización se aplica a las elecciones de **2009, 2012, 2015, 2018, 2021 y 2024**.
- Los conteos se suman para obtener indicadores regionales; la participación se recalcula como `SV / (SV + NV) × 100`. No se promedian directamente porcentajes municipales.
- La asignación permite comparar territorios; no implica que todas las personas o municipios de una región se comporten igual.

En la propuesta actual, los **cuatro perfiles son nacionales y se definen por sexo y edad**. La región es una capa de comparación territorial y no crea cuatro perfiles diferentes en cada zona. Véase [la explicación de los perfiles actuales en neto-jahzz-combinada](https://github.com/johannakeirabadilloz-tech/Hackathon-INE-2026/blob/neto-jahzz-combinada/reports/perfiles_sexo_edad/README.md).

El análisis anterior de dos perfiles por región está documentado en [las fichas regionales](../reports/sociodemografico/fichas_dos_perfiles_por_region.md).

El `scripts/config.py` de la rama combinada incluye también una alternativa exploratoria de **cinco regiones (`REGIONES_B`)**. Esa alternativa es distinta de la división de tres regiones descrita aquí; no debe confundirse con ella.

## Controles de consistencia

La asignación debe cumplir:

1. Incluir exactamente las 32 claves de entidad, de 01 a 32.
2. No repetir ninguna clave entre regiones.
3. Mantener 12 entidades en norte, 12 en centro y 8 en sur.
4. Coincidir con `REGIONES_A` y con el diccionario local del equipo.

Esta documentación publica la relación de entidades y regiones; no publica el dataset maestro ni el diccionario local.
