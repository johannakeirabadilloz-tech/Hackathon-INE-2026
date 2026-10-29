# Panel estadístico en Streamlit

La rama `Key-Dash` adapta la organización visual del panel Streamlit de `Dashboard_089`: sidebar de filtros, temas claro y oscuro, tarjetas de indicadores y secciones de gráficas. El flujo y los cálculos son específicos del análisis electoral. No requiere el código ni los datos de los repositorios 089/911.

## Ejecutar en Windows

Desde la raíz del repo:

```powershell
python -m venv .venv-dashboard
.\.venv-dashboard\Scripts\python.exe -m pip install -r requirements.txt
.\.venv-dashboard\Scripts\python.exe -m streamlit run app.py
```

Abrir la URL local que imprime Streamlit, normalmente `http://localhost:8501`.

En otros sistemas puede usarse un entorno virtual equivalente y `python -m streamlit run app.py`. No se necesitan las dependencias de modelos de `requirements-analysis.txt` para visualizar los resultados.

## Vistas

| Vista | Fuente | Filtros y alcance |
| --- | --- | --- |
| Panorama | Asignaciones, composición y trayectorias | Barras por edad en paneles de hombres y mujeres, tabla de perfiles y tabla de seis elecciones. Perfil y elección; la proporción de lista nominal siempre es de 2024. |
| Sexo y edad | `asignacion_segmentos_sexo_edad.csv`, `composicion_perfiles.csv` | Perfil, sexo, edad y elección; barras separadas por sexo o dispersión y brecha mujeres − hombres en puntos porcentuales. Solo se comparan edades con ambos sexos presentes en los filtros. |
| Evolución | `trayectorias_perfiles.csv` | Perfil y tipo de elección; serie nacional 2009–2024. |
| Territorio | `perfiles_region_tipo_comparacion.csv` | Perfil y región, tipo de sección o ambos; exclusivamente 2024. |
| Metodología | Comparación de algoritmos y documentación | Definiciones, selección de cuatro perfiles, límites y descargas. |

Todas las fuentes están publicadas en `reports/perfiles_sexo_edad/`. No se carga el maestro local, no se extraen ZIP ni se entrenan modelos al abrir la app. Los filtros no modifican las asignaciones publicadas.

La opción **Todos** en elección de referencia conserva las seis elecciones separadas: muestra un rango mínimo–máximo en las tarjetas, pestañas por año en las gráficas por edad y las seis columnas en la tabla resumen. No suma ni promedia porcentajes de distintas elecciones. Territorio mantiene su corte disponible de 2024.

## Reglas de los indicadores

- Participación: `SV / (SV + NV) × 100`; NS no es abstención.
- Proporción de lista nominal: denominador de hombres y mujeres de 18–99 años incluidos en los perfiles, en 2024. No se confunde con participación.
- Las tarjetas comparan contra la elección anterior del mismo tipo cuando existe en la serie.
- Las tasas nacionales publicadas están redondeadas a un decimal.
- No hay conteos desagregados en las tablas por edad publicadas: la app no inventa totales al filtrar edad o sexo.
- Región y sección son contexto de perfiles nacionales; no se suman ajustes territoriales para fabricar tasas de cruces ausentes.
- VALORES ATÍPICOS es el nombre del perfil 4, no un resultado de detección de anomalías.

Las tablas se muestran en HTML con el mismo tema que el panel, incluidos encabezados y filas. Las descargas CSV conservan los datos numéricos. El tema también se aplica a botones, menús y controles para plegar el sidebar.

## Comprobaciones

```powershell
.\.venv-dashboard\Scripts\python.exe -m unittest discover -s tests -p test_dashboard.py -v
```

Se comprueban límites de los perfiles, filtros vacíos, comparación de ciclos, denominadores, navegación y filtros con `streamlit.testing.v1.AppTest`.

El dashboard y los datos procesados se mantienen separados. El maestro, los catálogos privados y los entornos virtuales permanecen ignorados por Git.
