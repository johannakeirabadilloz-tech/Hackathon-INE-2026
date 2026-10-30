# Tendencia de clustering: por qué no hay grupos naturales y qué significa para los perfiles

Este documento explica la justificación técnica de los cuatro notebooks de esta carpeta y la relaciona con los perfiles de [`reports/perfiles_sexo_edad/`](../reports/perfiles_sexo_edad/README.md).

| Notebook | Qué mide |
|---|---|
| [`tendencia_clustering.ipynb`](tendencia_clustering.ipynb) | Tendencia a formar grupos en el **nivel** de participación (las 6 tasas 2009–2024) |
| [`tendencia_clustering_forma.ipynb`](tendencia_clustering_forma.ipynb) | Lo mismo, pero quitando el nivel y usando solo la **forma** de la trayectoria (ciclo presidencial/intermedio y tendencias) |
| [`tendencia_clustering_segmentos.ipynb`](tendencia_clustering_segmentos.ipynb) | Lo mismo sobre la tabla exacta que se agrupó en `perfiles_sexo_edad`: los **164 segmentos** sexo × edad simple |
| [`tendencia_clustering_fichas.ipynb`](tendencia_clustering_fichas.ipynb) | Lo mismo sobre la tabla exacta que se agrupó en las fichas de `reports/sociodemografico/`: los **144 segmentos** región × sexo × grupo de edad × sección |

**Los resultados describen participación observada en grupos de personas, no a individuos ni las causas de su comportamiento.**

---

## 1. Resumen

- **No hay evidencia de grupos naturales** ni en el nivel ni en la forma de la trayectoria de participación. Los datos se leen como un continuo.
- **Lo que ordena el nivel es la edad**; lo que ordena la forma es, sobre todo, el estado. Ninguno de los dos produce cortes naturales.
- Esto **no contradice** los cuatro perfiles de `perfiles_sexo_edad`: ese documento ya los presenta como cortes de una curva continua. Aquí se agrega la prueba técnica que lo respalda y se explica por qué las métricas que sí salieron altas (silhouette, ARI) no prueban que existan grupos.
- **También se probó sobre los 164 segmentos que sí se agruparon** (sección 3.6): sin evidencia de grupos frente a una curva continua, y sin saltos en las fronteras salvo en el borde (18 años).
- **Y sobre los 144 segmentos de las fichas** (sección 3.7): veredicto formal ambiguo; con una sensibilidad que modela mejor el ruido, sin estructura más allá del gradiente por edad. Los dos perfiles por región son cortes de edad (el 85+ siempre en el perfil A, los de 45–84 años siempre en el B).
- **Cómo debe leerse un perfil:** una tipología útil para diseñar acciones, no un grupo que "apareció" en los datos.

## 2. Qué se probó

**Unidad de análisis.** Una fila es una combinación **entidad × sexo × grupo de edad × tipo de sección** (por ejemplo, "Jalisco, mujer, 25–34, urbana"). Tras los filtros de calidad quedan 1,458 unidades (521 norte, 560 centro, 377 sur). Se hace un test por región (análisis A) y uno con las tres juntas (control B).

**Variables.**
- *Nivel:* las 6 tasas de participación (2009, 2012, 2015, 2018, 2021, 2024), escaladas.
- *Forma:* `forma` (las 6 tasas menos el promedio de la fila, en 5 componentes PCA) y `ciclo` (brecha presidencial–intermedia, tendencia 2012→2024 y tendencia 2009→2021).
- Sexo, edad y sección **no** son variables: definen quién es la fila y se usan después para describir.

**Dos pruebas.**
- **Hopkins (H):** compara la distancia de los puntos reales a su vecino más cercano con la de puntos aleatorios uniformes. Cerca de 0.5 = sin estructura; cerca de 1 = los puntos se agrupan.
- **VAT:** imagen de la matriz de distancias, con filas y columnas reordenadas por cercanía. Los grupos aparecen como cuadrados oscuros en la diagonal; un degradado indica gradiente.

## 3. Justificación técnica

### 3.1 Un Hopkins alto no basta

Las 6 tasas están muy correlacionadas (casi todo es "participa más o menos"), así que los puntos forman una **nube alargada**. Los puntos uniformes de la prueba se generan en la caja que contiene los datos, y en una nube alargada la mayoría cae lejos de los datos reales. Eso infla H **aunque no haya grupos**.

Por eso cada resultado se compara con una referencia sin grupos: una **nube gaussiana con la misma media y covarianza**. Lo que cuenta es `delta = H_real − H_gauss`. La regla de veredicto es heurística y exploratoria (`clara`: H > 0.75 y delta > 0.10; `moderada`: H > 0.60 y delta > 0.05; en otro caso `sin evidencia`).

### 3.2 Resultados sobre el nivel

| | Resultado |
|---|---|
| Hopkins real | 0.86 a 0.89 |
| `delta` frente a la gaussiana | −0.017 a +0.012 (máximo +0.035, conjunto con PCA) |
| Veredicto | `sin evidencia` en los 12 casos (4 casos × 3 representaciones) |
| Efecto entidad (η²) | 0.10 a 0.40; quitarlo no cambia el veredicto |

H es alto, pero la nube sin grupos con la misma covarianza da prácticamente lo mismo: el valor viene de la forma alargada, no de grupos. En el VAT el panel real no muestra cuadrados nítidos y se parece al nulo gaussiano.

### 3.3 Resultados sobre la forma

Para comprobar que ya no es el mismo eje, se verificó que las variables de forma casi no se correlacionan con el nivel (|r| ≤ 0.17).

| Variante | `delta` frente a la gaussiana | Veredicto |
|---|---|---|
| `ciclo` (con y sin entidad) | −0.02 a +0.01 | `sin evidencia` en los 8 casos |
| `forma` con entidad | 0.09 a 0.10 (conjunto 0.086) | `moderada` |
| `forma` sin entidad | 0.03 a 0.07 | conjunto `sin evidencia`; sur en el límite de `moderada` (H = 0.72) |

La única señal, `forma` con entidad, desaparece o se debilita al quitar el efecto entidad. Los diagnósticos con Ward lo confirman: la forma coincide con la entidad (NMI 0.25 a 0.60) y casi nada con la edad (0.00 a 0.09). El bloque oscuro visible en el VAT de `ciclo` agrupa ≈12 % de las unidades, de solo 10 estados (Nuevo León, Colima, Sonora y Campeche suman ≈60 %), con una brecha presidencial–intermedia de ≈3 puntos frente a ≈12 en el resto. Es un conjunto de estados con ciclo débil y no un perfil de votante.

### 3.4 Qué ordena realmente los datos: un gradiente por edad

Al cortar el nivel con Ward en 2 a 4 grupos, la coincidencia (NMI) es de 0.19 a 0.29 con edad, de 0.03 a 0.12 con entidad y de 0.02 o menos con sexo y sección. Es un gradiente por edad, no cortes naturales. Una NMI de 0.2 a 0.3 es modesta: la edad explica **una parte** de la estructura, no toda, y como edad y nivel de participación son casi el mismo eje, con estos datos no se separan.

La forma deja una huella suave de la edad (promedios en puntos de participación, conjunto):

| Edad | `brecha_ciclo` | `tend_pres` (2024 − 2012) | `tend_inter` (2021 − 2009) |
|---|---|---|---|
| 18–24 | 11.3 | −6.0 | 7.4 |
| 35–44 | 11.9 | −6.1 | 7.2 |
| 55–64 | 10.4 | −3.0 | 7.4 |
| 65–74 | 9.8 | 2.4 | 9.9 |
| 85+ | 10.2 | 3.2 | 13.0 |

El ciclo presidencial sube la participación unos 10 a 12 puntos **a todas las edades**; lo que cambia con la edad es la tendencia: baja hasta los 64 años y sube desde los 65.

### 3.5 Cómo se ve en el VAT

Revisión puntual (cortando la diagonal por contraste; **no está en el notebook**, por lo que los límites son aproximados).

En los datos reales hay unas cinco manchas oscuras a lo largo de la diagonal, y las dos centrales (3.ª y 4.ª) forman el bloque más grande. Cada una es una franja de edad ordenada por participación:

| Mancha | Edades | Participación media |
|---|---|---|
| Inicio de la diagonal | 85+ | 0.31 |
| 2.ª | 18–44 | 0.46 |
| 3.ª y 4.ª (bloque central) | 45–84 | 0.64 a 0.65 |
| Final | mezcla de 18–34 y 85+ | 0.51 |

Ninguna mancha está dominada por un estado. Sin efecto entidad quedan tres bloques: 45–74 años (0.64), 18–44 (0.48) y un bloque pequeño casi solo de 85+ (0.34). Son los mismos tramos del mismo gradiente, con menos ruido: que se vea más limpio no prueba que haya grupos (Hopkins sigue sin superar al nulo).

### 3.6 Prueba directa sobre los 164 segmentos

Los resultados anteriores usan otra tabla (1,458 unidades). Para cerrar esa brecha, [`tendencia_clustering_segmentos.ipynb`](tendencia_clustering_segmentos.ipynb) aplica Hopkins y VAT a **la misma matriz de 164×6 que se agrupó** (`asignacion_segmentos_sexo_edad.csv`). Antes de analizar comprueba que es la misma: la silhouette de k = 2 a 6 coincide con `perfiles_edad_sexo_comparacion.csv`, el agrupamiento con k = 4 coincide con `perfil_numero` (ARI = 1) y una celda coincide con los datos originales.

**Un nulo adicional.** Los 164 puntos son dos curvas finas (una por sexo), y Hopkins sube con cualquier estructura delgada. Por eso, además de la gaussiana y las columnas permutadas, se usa un **nulo de curva continua**: se ajusta una curva suave a cada sexo y elección, y se generan 164 puntos sobre ella con el mismo ruido y las mismas edades. Es una población continua por construcción, con la misma forma. Se explica dentro del notebook.

| Prueba | Resultado |
|---|---|
| Hopkins real | 0.946 |
| Nulo gaussiano / nulo de curva | 0.935–0.936 / 0.929–0.937 |
| `delta_curva` | +0.009 a +0.017 (`sin evidencia`) |
| Columnas permutadas | 0.604 (la forma de curva es lo que eleva H) |
| VAT | Sin bloques nítidos; el orden del VAT es el orden por edad, con las curvas de hombres y mujeres paralelas |
| Contraste de saltos en las fronteras (11 fronteras) | 1.37 frente a un p90 del nulo de 1.21–1.27 |
| Sin las fronteras del borde (edad < 20) | 1.07 frente a un p90 de 1.15–1.20 (p empírico 0.45–0.57) |

**Veredicto formal: ambiguo.** La regla se fijó antes de ejecutar: "continuo" exigía `delta_curva` < 0.05 **y** un contraste de saltos bajo el p90 del nulo. Hopkins cumple la primera condición; el contraste no cumple la segunda, por una sola frontera: los 18 años. Esa edad se separa de los 19 con un paso de distancia más del doble que el de cualquier otra edad (en 2024, hombres: 57.9 % a los 18 frente a 49.0 % a los 19). Sin esa frontera, el contraste queda dentro de lo esperado para una curva continua. Ese análisis de sensibilidad se agregó después de ver el primer resultado, así que **no sustituye** al veredicto formal. Los cortes de 36–38, 51 y 77–92 años caen donde la curva no da saltos (contraste ≈ 1).

Los 18 años son una discontinuidad real de los datos. La causa no se puede determinar aquí (una hipótesis es el efecto del primer voto, no probada). Es coherente con que `perfiles_sexo_edad` ponga a las mujeres de 18 años en el perfil 1 junto con las de 39 a 77: es un punto aislado del borde, no un grupo.

### 3.7 Prueba directa sobre los 144 segmentos de las fichas

[`tendencia_clustering_fichas.ipynb`](tendencia_clustering_fichas.ipynb) aplica Hopkins y VAT a la matriz de 144×6 que se agrupó para las fichas (`perfiles_segmentos.csv`: 48 segmentos por región = 2 sexos × 8 grupos de edad × 3 secciones). Antes de analizar comprueba que es la misma: la silhouette de k = 2 y el agrupamiento (ARI = 1) coinciden con las fichas, con el algoritmo elegido por región, y una celda coincide con el maestro.

**Qué se puede probar.** La edad viene en solo 8 grupos, así que **no se puede comprobar si la participación es continua a lo largo de la edad** (eso lo hace la sección 3.6, con edad simple). Aquí se pregunta si hay estructura **más allá** de un gradiente por edad con el sexo y la sección desplazándolo, y si la silhouette (el criterio con el que las fichas eligieron k = 2) distingue una tabla real de una sin grupos. Se usan dos nulos de gradiente, uno suave (polinomio de grado 4 en la edad por sexo) y uno por celdas (una media libre por sexo × edad), ambos más el efecto de la sección.

| Prueba | Resultado |
|---|---|
| Hopkins real (n = 48 por región) | 0.831 a 0.867 |
| Nulo gaussiano / columnas permutadas | `delta_gauss` entre −0.022 y −0.001 / H = 0.51 a 0.55 |
| `delta` frente al nulo de gradiente (ruido independiente) | +0.051 a +0.070 (suave); +0.041 a +0.061 (celdas) |
| Silhouette real de k = 2 | 0.596 a 0.617; sobre el percentil 95 del nulo suave en las tres regiones |
| `delta` con ruido de covarianza completa (sensibilidad) | +0.005 a +0.019 |
| Silhouette real frente a esos nulos | dentro en centro y sur; en el borde en el norte (p = 0.045) |
| Varianza de las 6 tasas explicada por edad / sexo × edad | 80–81 % / 94–96 % (sexo solo 1–3.5 %, sección 2–4 %) |
| Una regla de solo edad reproduce el perfil publicado | 87.5–91.7 % de los segmentos (referencia 62.5–75 %) |

**Veredicto formal: ambiguo en las tres regiones.** La regla (fijada antes de ejecutar) pedía `delta` < 0.05 y silhouette dentro del nulo para decir "sin estructura"; con ruido independiente el `delta` queda en +0.05 a +0.07 y la silhouette supera el percentil 95. Esa diferencia desaparece con ruido que respeta la correlación entre elecciones: los residuos reales están muy correlacionados y la tabla real es más "delgada" que un nulo con ruido independiente, lo que eleva Hopkins sin que haya grupos. Ese cambio se agregó **después de ver el primer resultado**, por lo que no sustituye al veredicto formal.

**Lo que muestra la tabla.** El perfil A contiene siempre los 85+ y casi todos los segmentos jóvenes (entre la mitad en el centro y cinco de seis en norte y sur de los de 18–34); el perfil B contiene siempre los de 45–84. La participación forma una U invertida con el máximo a los 65–74 años. Los dos perfiles por región son, por lo tanto, cortes de edad. Los 85+ son un solo grupo de edad (85–99) y aparecen como un bloque pequeño y separado en el VAT, con un salto de ≈24 puntos desde 75–84; con la edad simple (sección 3.6) no se ve un salto ahí. Es coherente con que el bloque se deba en parte al tamaño del grupo de edad, pero no se probó con esta tabla.

## 4. Relación con `perfiles_sexo_edad`

### 4.1 Los hallazgos son compatibles

| Lo que dice `perfiles_sexo_edad` | Lo que añade esta carpeta |
|---|---|
| "Los perfiles son cortes de una curva continua, no grupos con fronteras naturales" (fig. 1). | Es la conclusión de Hopkins y VAT: sin evidencia de grupos, y la estructura es un gradiente por edad. |
| "Se eligió 4 por criterio, no porque los datos prueben que existan exactamente cuatro tipos". | No hay un k natural que descubrir. Cualquier k es una decisión de resumen. |
| La edad es el factor principal (SHAP 11.6 puntos). | La edad es lo que más ordena el nivel (NMI 0.19–0.29). |
| El ciclo sube todos los perfiles entre 10 y 14 puntos. | `brecha_ciclo` es de 10 a 12 puntos a todas las edades: las curvas son paralelas, y los perfiles se distinguen por nivel, no por forma. |
| Región y sección mueven el nivel, poco la forma. | Hay estructura de forma, pero es territorial y sigue sin dar grupos (ver 4.4). |

### 4.2 Por qué silhouette y ARI altos no prueban que existan grupos

En `perfiles_sexo_edad` (sección 3.2) la silhouette va de 0.51 a 0.61 y la estabilidad (ARI medio) de 0.89 a 0.97. Ambas son altas, pero **miden otra cosa**:

- La silhouette mide qué tan bien separado queda un corte; asume el número de grupos y no pregunta si existen.
- El ARI mide si el mismo corte se repite con submuestras; un corte de una curva continua también es estable.

Se comprobó con una simulación mínima: 164 puntos (como los segmentos sexo × edad) sobre una curva continua con 6 coordenadas y ruido pequeño, **sin grupos por construcción**, y el mismo procedimiento de k-means con submuestras del 80 %.

| k | Silhouette (simulación sin grupos) | Silhouette (`perfiles_sexo_edad`) | ARI medio (simulación) | ARI medio (`perfiles_sexo_edad`) |
|---|---|---|---|---|
| 2 | 0.594 | 0.605 | 0.960 | 0.897 |
| 3 | 0.576 | 0.593 | 0.963 | 0.966 |
| 4 | 0.539 | 0.566 | 0.966 | 0.959 |
| 5 | 0.522 | 0.518 | 0.968 | 0.889 |
| 6 | 0.509 | 0.505 | 0.855 | 0.916 |

Los valores son muy parecidos. La simulación es estilizada y no usa los datos, pero muestra que esas dos métricas, por sí solas, no distinguen un continuo de un conjunto de grupos. La prueba que sí lo distingue, aplicada a los 164 segmentos reales, está en la sección 3.6: no hay evidencia de grupos frente a una curva continua, con la salvedad de la discontinuidad de los 18 años.

### 4.3 Qué explica el gradiente de los perfiles

- **Perfil 3 mezcla jóvenes y 85+.** En el VAT, los jóvenes (18–34) y los 85+ están en los extremos de baja participación del mismo gradiente y por eso caen juntos. `perfiles_sexo_edad` ya avisa que "compartir perfil no significa tener las mismas razones"; el VAT lo respalda: sin efecto entidad los separa en bloques distintos.
- **Perfil 4 ("valores atípicos") es el extremo del gradiente.** El bloque pequeño de 85+ del VAT (participación 0.22 a 0.41) coincide en nivel con el perfil 4 (11 % a 31 %). El grupo de edad 85+ del dataset maestro no distingue entre 84–92 y 93+, así que la coincidencia es de nivel y no una asignación exacta.
- **Perfil 1 es el núcleo adulto.** El bloque central del VAT (45–84 años, participación 0.64 a 0.65) corresponde a la zona de mayor participación, igual que el perfil 1.

### 4.4 Matices

- **No es el mismo ejercicio.** El notebook trabaja con entidad × sexo × grupo de edad × sección (1,458 unidades, edad en grupos); `perfiles_sexo_edad` agrupa 164 segmentos nacionales de sexo × edad simple. Para cerrar esa brecha se aplicó Hopkins y VAT directamente a los 164 segmentos (sección 3.6) y la conclusión se sostiene, con el veredicto formal en "ambiguo" por la frontera de los 18 años. Lo mismo se hizo con los 144 segmentos de las fichas (sección 3.7), con veredicto formal también ambiguo.
- **Sexo.** En el notebook, el sexo casi no coincide con los cortes (NMI ≤ 0.02). Eso es compatible con que en `perfiles_sexo_edad` el sexo defina perfiles: ahí el sexo **desplaza la curva** (las mujeres alcanzan el nivel alto unos 13 años antes), no forma grupos propios. Es una interpretación, no algo probado en estos notebooks.
- **Región frente a estado.** `perfiles_sexo_edad` dice que la región mueve el nivel y poco la forma; aquí el estado sí deja huella en la forma (NMI 0.25 a 0.60). No se contradicen: una región (norte, centro, sur) es una unidad gruesa que mezcla estados con ciclos distintos, y la sección 3.4 de `perfiles_sexo_edad` ya muestra más variación entre municipios que entre regiones.

## 5. Cómo usar los perfiles con esta información

- Presentarlos como **tipologías por cortes de un gradiente** (edad × nivel de participación × ciclo), no como "cuatro tipos de votante descubiertos".
- No justificar el número de perfiles con silhouette o ARI; justificarlo por utilidad y simplicidad, como ya hace `perfiles_sexo_edad`.
- Cualquier perfil basado en la forma de la trayectoria debe revisarse contra el efecto entidad antes de interpretarse.
- Que no haya grupos naturales **no impide** segmentar con K-means, Ward o mezclas gaussianas; cambia cómo se interpreta el resultado.

## 6. Límites

- Los umbrales del veredicto (0.75, 0.60, 0.10, 0.05) son heurísticos y no se calibraron.
- Las dos referencias nulas (gaussiana con la misma covarianza y columnas permutadas) son supuestos: si los datos reales fueran no gaussianos de otra forma, el nulo podría estar mal elegido.
- Solo se usaron como variables las tasas de participación. No se probaron variables de contexto municipal, escolaridad o ingreso, que podrían producir estructura distinta.
- La unidad es un grupo agregado, no una persona; edad, periodo y cohorte no se pueden separar con estos datos.
- Los cortes del VAT descritos en la sección 3.5 son automáticos y aproximados.
- Los nulos de gradiente de la sección 3.7 suponen un polinomio de grado 4 en solo 8 grupos de edad y, en su versión formal, ruido independiente entre elecciones; el modelo de ruido con covarianza completa se agregó después de ver el resultado.
- El nulo de curva continua (sección 3.6) depende del suavizado elegido (polinomios de grado 6 y 10, con el mismo resultado) y supone ruido independiente entre edades. El análisis sin la frontera de los 18 años se agregó después de ver el resultado.
- El notebook usa `part = SV/(SV+NV)` y excluye a no binarios; los no especificados solo filtran, igual que en `perfiles_sexo_edad`.

## 7. Cómo reproducirlo

Los dos primeros notebooks requieren `data/processed/civia_dataset_maestro_municipal_2009_2024_con_region.csv` (local, no versionado). El de las fichas requiere `reports/sociodemografico/perfiles_segmentos.csv` y `metodologia.json` (versionados), y opcionalmente el maestro para comprobar una celda. El de los 164 segmentos solo requiere `reports/perfiles_sexo_edad/asignacion_segmentos_sexo_edad.csv` y `perfiles_edad_sexo_comparacion.csv` (versionados); si está `data/raw/DatosAbiertos_DECEyEC_ConteosCensales2024/`, además comprueba una celda contra los originales. Dependencias en [`requirements-analysis.txt`](../requirements-analysis.txt); semilla 42 y 50 repeticiones de Hopkins.

Las imágenes y tablas se guardan en `reports/local/tendencia/`, `reports/local/tendencia_forma/`, `reports/local/tendencia_segmentos/` y `reports/local/tendencia_fichas/` (carpeta local, ignorada por git):

| Archivo | Contenido |
|---|---|
| `resumen_hopkins.csv`, `resumen_hopkins_forma.csv` | Hopkins real, gaussiano y permutado por caso y variante |
| `efecto_entidad_eta2.csv` | η² por entidad y elección (nivel) |
| `diagnostico_nmi.csv`, `diagnostico_nmi_forma.csv` | Coincidencia de cortes con entidad, sexo, edad y sección |
| `vat_*.png`, `vat_forma_*.png`, `vat_segmentos.png` | Imágenes VAT por caso |
| `resumen_hopkins_segmentos.csv`, `resumen_saltos.csv` | Hopkins con los tres nulos y contraste de saltos (164 segmentos) |
| `resumen_hopkins_fichas.csv`, `silhouette_vs_nulo_fichas.csv`, `varianza_explicada_fichas.csv`, `vat_fichas_*.png` | Hopkins con los nulos de gradiente, silhouette frente a los nulos, varianza explicada por factor e imágenes VAT (144 segmentos de las fichas) |
| `pasos_entre_edades.csv`, `contraste_fronteras.csv` | Distancia entre edades vecinas y contraste en cada frontera de perfil |
