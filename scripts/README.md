# Perfiles sociodemográficos de participación

Análisis para el Reto 1 del Hackathon INE 2026. La unidad es región × sexo × grupo de edad × tipo de sección, con una trayectoria de participación en seis elecciones de 2009 a 2024.

## Ejecución

Desde la raíz del repositorio:

```powershell
python -m pip install -r requirements-analysis.txt
python scripts/perfiles_sociodemograficos.py
```

En esta sesión se instalaron dependencias en `.analysis_deps/`; el script detecta esa carpeta automáticamente. Si no existe, usa el entorno Python activo.

Entrada: `data/processed/dataset_maestro_municipal_2009_2024_con_region.csv` (solo local).

Informe: `reports/local/sociodemografico/informe_sociodemografico.html`. Abrir en un navegador; requiere los siete PNG de la misma carpeta. También se generan tablas CSV de indicadores, composición, asignaciones, comparación de algoritmos, narrativas y estrategias, y parámetros en JSON.

Cada ejecución genera resultados en `reports/local/`, excluido de Git. La versión autorizada para publicación está en `reports/sociodemografico/`: contiene el informe, siete PNG, seis fichas, parámetros y tablas de resultados. El maestro y el diccionario de trabajo permanecen locales. Para actualizar la versión publicada, revisar y copiar los resultados de la ejecución a esa carpeta.

## Método e interpretación

Se recalculan tasas desde los conteos, se estandarizan las seis tasas por elección y se comparan K-means, Ward y mezclas gaussianas diagonales con dos a cinco grupos. La selección de dos perfiles considera separación, tamaños y estabilidad por submuestras y omisión de elección. Los umbrales son exploratorios y están documentados en el informe.

Las matrices muestran exactamente qué combinaciones de edad, sexo y sección componen cada perfil. Los nombres y estrategias son propuestas para validar. Cada segmento pesa igual en el ajuste; los indicadores agregados se calculan desde los conteos.

No se sigue a individuos entre elecciones ni se atribuyen causas. No binario se conserva descriptivamente porque solo aparece en 2024. No hay escolaridad en la fuente. No fue necesario recuperar campos originales para este primer análisis; edad exacta y sección quedan para una posible ampliación.

Antes de fijar perfiles, falta cotejar el maestro contra los originales y evaluar la sensibilidad a la agregación regional y a otras representaciones de variables.

Referencias: [clustering](https://scikit-learn.org/stable/modules/clustering.html) y [mezclas gaussianas](https://scikit-learn.org/stable/modules/mixture.html), documentación de scikit-learn.
