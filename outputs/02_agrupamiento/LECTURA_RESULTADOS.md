# Experimento 2 · ¿Existen tipos naturales de entidad?

**Conclusión.** No. Al agrupar las 32 entidades por su trayectoria de participación en las 6 elecciones no aparecen tipos naturales: la mejor separación observada (silhouette 0.33) es igual o peor que la de datos simulados sin grupos en 67% de los casos; el mejor agrupamiento (2 grupos) explica 42% de la variación entre entidades y un simple corte por nivel promedio explica 41%. Lo que sí existe es un **continuo** descrito por dos ejes: el nivel general (64% de la variación) y si la entidad es relativamente más alta en 2009–2015 o en 2018–2024 (20%). Se recomienda usar esos dos ejes, no etiquetas de grupo.

## Qué se hizo

- Unidades: 32 entidades. Variable: participación en 6 elecciones, estandarizada por elección (quita el efecto común del ciclo presidencial/intermedio).
- **Por distancia:** K-means y Ward, de 2 a 6 grupos. **Por densidad:** DBSCAN y HDBSCAN.
- Cuatro definiciones de la métrica: sobre situación conocida, sobre lista nominal, estandarizada por sexo × edad y desvío frente al nacional.
- Validación: cambio de métrica, retirar una entidad, retirar una elección, referencia por corte del nivel promedio y un nulo gaussiano (300 simulaciones con la misma media y covarianza, sin grupos).
- Repetido con 2,320 municipios (los que tienen ≥ 500 registros con situación conocida en las 6 elecciones; supuesto).

## Resultados (`tablas/agr_*.csv`)

| Prueba | Resultado |
| --- | --- |
| Mejor silhouette (K-means, 2 grupos) | 0.33. Nulo sin grupos: mediana 0.35, p95 0.42; el nulo iguala o supera lo observado en 67% de simulaciones |
| 3 a 6 grupos | silhouette 0.28–0.29; desde 4 grupos aparecen grupos de 1 a 2 entidades |
| Estabilidad al cambiar la métrica (2 grupos, K-means) | ARI mínimo 0.88, medio 0.92 |
| Estabilidad al retirar una entidad | ARI medio 0.90 (mín. 0.87) |
| Estabilidad al retirar una elección | ARI medio 0.82 (mín. 0.55): el más afectado, depende de qué elección se omita |
| Referencia (2 grupos) | Agrupamiento 42% de variación explicada vs 41% del corte por nivel; ARI entre ambos 0.76 |
| Referencia (3 grupos, K-means) | 55% vs 49% |
| DBSCAN (min. 3 puntos) | Con eps = 1.56: 2 grupos y 10 entidades como ruido; con eps ≥ 2.0: 1 solo grupo |
| HDBSCAN | tamaño mín. 3: 2 grupos, 11 ruido; 4: 2 grupos, 15 ruido; 5: 0 grupos (todo ruido) |
| Municipios | 2 grupos: silhouette 0.35, 43.2% explicado vs 42.8% del corte por nivel; HDBSCAN (mín. 20): 2 grupos con 57.5% de ruido; (mín. 50): todo ruido |

**Lectura.** La partición en 2 grupos es estable, pero esa estabilidad solo dice que "alto vs bajo nivel" es un corte reproducible, y el corte por mediana hace casi lo mismo (ARI 0.76). Las métricas de separación son poco confiables aquí: la entrada ya contiene lo que se quiere separar (una dimensión dominante de nivel, 64% de la varianza), y el nulo gaussiano con esa misma estructura produce silhouettes iguales o mayores. Los métodos de densidad confirman la ausencia de islas: o hay un solo grupo o declaran la mayoría de las entidades como ruido.

## Alternativa continua (`tablas/agr_05_pca_cargas.csv`, `agr_06_pca_entidades.csv`)

PCA de las trayectorias estandarizadas: PC1 = 64.2% (cargas positivas en las 6 elecciones: 0.30–0.47) → nivel general relativo; PC2 = 19.9% (+0.64 en 2009, +0.56 en 2015, ≈ 0 en 2012 y −0.31, −0.28, −0.32 en 2018, 2021, 2024) → entidades relativamente más altas en elecciones tempranas frente a recientes. Con municipios, PC1 = 71.4% y PC2 = 14.3%. Figuras `08`, `09`, `10`.

## Límites

- Solo 32 entidades: poco poder para detectar grupos pequeños; con k ≥ 4 los grupos son de 1–2 entidades.
- "No hay grupos nítidos" no es "no hay diferencias": el rango entre entidades es amplio (ver Experimento 1); simplemente forman un gradiente.
- Los nombres de grupo de análisis previos del repositorio (perfiles por región × sexo × edad × sección) no se reevaluaron aquí.
