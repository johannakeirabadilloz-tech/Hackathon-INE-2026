"""Contenido del documento técnico (lenguaje claro). Lo consumen el generador de Word y el de PDF.
Marcado en el texto: **negritas**. Bloques: (tipo, ...)."""
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
FIG = RAIZ / "reports/perfiles_sexo_edad"

TITULO = "Perfiles ciudadanos de participación electoral en México, 2009–2024"
SUBTITULO = "Documento técnico · Hackathon INE 2026 · Reto 1: Perfiles ciudadanos de participación"
PROYECTO = "Centro de Inteligencia y Visualización de Información para el Análisis Electoral"
EQUIPO = ("Equipo: Valeria Jahzeel Castañon Hernandez, Johanna Keira Badillo Zavala, "
          "Ernesto Mendieta Cuecuecha y Rodrigo Paredes Urrusquieta.")

B = []
add = B.append

# ------------------------------------------------------------------ 0. RESUMEN
add(("h1", "Resumen"))
add(("p", "**La pregunta.** ¿Quiénes participan menos en las elecciones federales, dónde se nota la diferencia y qué se puede "
          "hacer de forma distinta para cada grupo?"))
add(("p", "**Los cuatro perfiles de un vistazo.**"))
add(("table", {
    "header": ["#", "Perfil", "Quiénes son", "% de la lista nominal 2024", "Participación 2024"],
    "rows": [
        ["1", "**Participación alta**", "Mujeres de 39 a 77 años y hombres de 52 a 81", "41.0 %", "70.6 %"],
        ["2", "**Participación intermedia**", "Mujeres de 19 a 38 años y hombres de 37 a 51 (más algunos tramos pequeños)", "39.0 %", "56.5 %"],
        ["3", "**Participación baja**", "Hombres de 20 a 36 años (casi todo el perfil) y personas de 84 a 92", "19.6 %", "43.6 %"],
        ["4", "**Edades muy avanzadas (90+)**", "Mujeres de 90 a 99 años y hombres de 93 a 99", "0.4 %", "31.1 %"],
    ],
    "widths": [0.05, 0.22, 0.43, 0.16, 0.14],
    "align": ["C", "L", "L", "C", "C"],
    "note": "Participación = votaron ÷ (votaron + no votaron). Fuente: Conteos de Participación Ciudadana del INE.",
}))
add(("p", "**Lo que encontramos.**"))
add(("bullets", [
    "**La edad es lo que más ordena la participación, y el sexo cambia el momento.** En 2024, la participación baja después de los 18 "
    "años hasta un mínimo entre los 24 y los 28, sube hasta un máximo entre los 65 y los 72 y vuelve a bajar en edades muy avanzadas. "
    "Las mujeres llegan al nivel más alto unos 13 años antes que los hombres (a los 39 frente a los 52).",
    "**Cuatro perfiles resumen ese patrón.** En 2024 participan 70.6 %, 56.5 %, 43.6 % y 31.1 %. La distancia entre un perfil y el "
    "siguiente (de 11 a 23 puntos) se repite en las seis elecciones. Tres perfiles reúnen 99.6 % de la lista nominal; el cuarto es "
    "muy pequeño (0.4 %) y debe leerse con reserva.",
    "**Los perfiles son cortes útiles, no grupos naturales.** Probamos si los datos forman grupos separados por sí solos y no es así: "
    "la participación cambia de forma continua con la edad. Por eso defendemos el número de perfiles por su utilidad y su estabilidad.",
    "**Las estrategias se diferencian por perfil, por momento del ciclo electoral y por territorio.** Hay dos grupos con más margen "
    "de mejora: el perfil intermedio (39 % de la lista nominal), que baja unos 14 puntos en las elecciones intermedias, y los hombres "
    "de 20 a 36 años (18.7 % de la lista nominal; 43 % de participación en 2024).",
]))
# ------------------------------------------------------------------ 1. PROBLEMA
add(("h1", "1. Qué queremos saber"))
add(("p", "El reto pide estudiar los patrones electorales de distintos grupos de la población para construir perfiles que ayuden a "
          "entender su participación y a plantear estrategias para incentivarla. Lo abordamos con un análisis de seis elecciones "
          "federales (2009, 2012, 2015, 2018, 2021 y 2024) por edad, sexo y territorio."))
add(("p", "**Objetivo.** Identificar, describir y comparar perfiles de participación y abstención ciudadana en México, para generar "
          "hallazgos y recomendaciones basados en evidencia que sirvan para diseñar estrategias focalizadas."))

# ------------------------------------------------------------------ 2. DATOS
add(("h1", "2. Los datos y cómo medimos la participación"))
add(("p", "**Qué datos usamos.** Seis paquetes de Conteos de Participación Ciudadana del INE (uno por elección). Provienen de los "
          "cuadernillos de las listas nominales y vienen por sección electoral, sexo y edad, con cuatro cifras: la lista nominal "
          "(personas inscritas), las que votaron, las que no votaron y las que no tienen participación especificada. No incluyen "
          "casillas especiales ni voto desde el extranjero."))
add(("p", "**Cómo medimos.** Participación = votaron ÷ (votaron + no votaron). Los registros “no especificados” no se cuentan "
          "como voto ni como abstención. Si se contaran como “no votó”, ningún grupo cambia de perfil."))
add(("p", "**Calidad.** El dataset maestro del proyecto (546,968 celdas) coincide celda por celda con las 54,872,712 filas originales. "
          "Dejamos fuera dos casos: las personas no binarias (el INE solo las registra en 2024, con 105 personas; sin historial no se "
          "puede construir su trayectoria) y las edades de 100 años o más (0.02 % de la lista nominal; probables errores de registro)."))
add(("p", "**Con qué grupos trabajamos.** Según la etapa usamos tres formas de agrupar los datos: 144 grupos de región, sexo, edad y "
          "tipo de sección (fichas por región); 1,458 grupos de entidad, sexo, edad y tipo de sección (pruebas de agrupamiento natural), y "
          "**164 grupos de sexo y edad simple, de 18 a 99 años (perfiles adoptados)**. En todas, cada grupo se describe con seis números: "
          "su participación en cada elección."))

# ------------------------------------------------------------------ 3. METODOLOGÍA
add(("h1", "3. Cómo construimos los perfiles"))
add(("h2", "3.1 Punto de partida: dos perfiles por región"))
add(("p", "Primero agrupamos 144 grupos de región, sexo, edad y tipo de sección (urbana, mixta o rural). Se compararon tres métodos "
          "de agrupamiento y se eligieron dos perfiles por región: uno de menor participación (44.9 % a 47.1 % en 2024, según la región) y "
          "otro de mayor participación (63.1 % a 67.7 %)."))
add(("p", "Las propias fichas advierten que dos perfiles “no demuestran que existan únicamente dos tipos naturales de ciudadanía”. "
          "Esa duda —si los datos separan grupos por sí solos— es la que contestamos a continuación."))
add(("h2", "3.2 ¿Los datos forman grupos naturales?"))
add(("p", "Para saberlo aplicamos dos pruebas que miden la “tendencia al agrupamiento”: la **estadística de Hopkins** (un número entre "
          "0.5 y 1; cerca de 0.5 significa puntos sin estructura y cerca de 1, puntos agrupados) y el **VAT**, una imagen de las "
          "distancias entre grupos donde los grupos aparecerían como cuadrados oscuros y un gradiente como un degradado. Como las "
          "seis tasas de participación están muy relacionadas entre sí, cada resultado se compara con datos de referencia sin grupos."))
add(("callout", "Resultado",
     "Ninguna de las cuatro pruebas encontró estructura más allá del gradiente por edad. La participación cambia de forma continua: "
     "es una rampa, no un conjunto de islas. El detalle de las pruebas está en el Anexo A."))
add(("p", "**¿Qué significa para los perfiles?** Que no existen “tipos de personas” que los datos separen solos. Aun así se puede "
          "segmentar: los métodos de agrupamiento producen cortes útiles y estables sobre una curva continua. Por eso decidimos "
          "segmentar por el valor de la **edad**, que es el eje que ordena los datos, con la resolución suficiente (edad simple) e "
          "incluir el **sexo**; la región y el tipo de sección se tratan como un ajuste (sección 5)."))
add(("h2", "3.3 Los cinco pasos"))
add(("numbered", [
    "**Armamos 164 grupos nacionales:** 2 sexos × 82 edades (de 18 a 99 años).",
    "**Describimos cada grupo con seis números:** su participación en cada una de las seis elecciones, ajustada para que ninguna "
    "elección pese más que otra.",
    "**Juntamos los grupos más parecidos** con k-means, un método que reúne en un mismo perfil los grupos cuya trayectoria es similar.",
    "**Elegimos cuántos perfiles formar,** comparando de 2 a 6 (cuadro siguiente).",
    "**Comprobamos que los perfiles no cambien** al quitar datos o cambiar decisiones (cuadro de robustez).",
]))
add(("table", {
    "header": ["Número de perfiles", "Separación (silhouette)", "Coincidencia media (ARI)", "Coincidencia mínima (ARI)"],
    "rows": [["2", "0.605", "0.897", "0.636"], ["3", "0.593", "0.966", "0.852"], ["**4**", "**0.566**", "**0.959**", "**0.817**"],
             ["5", "0.518", "0.889", "0.759"], ["6", "0.505", "0.916", "0.781"]],
    "widths": [0.22, 0.26, 0.26, 0.26], "align": ["C", "C", "C", "C"],
    "note": "La separación (silhouette) mide qué tan distintos quedan los perfiles. La coincidencia (índice de Rand ajustado, ARI) mide "
            "qué tan parecido sale el resultado al repetirlo con el 80 % de los datos: 1 es idéntico y 0 es azar.",
}))
add(("p", "Con dos perfiles la separación es mayor, pero es el resultado menos estable. Con tres y cuatro el resultado es muy estable y "
          "aparece lo que dos perfiles mezclan: las edades más avanzadas y la diferencia por sexo. **Elegimos cuatro por criterio**, "
          "no porque los datos prueben que existan exactamente cuatro tipos."))
add(("table", {
    "header": ["Prueba de robustez", "Resultado (ARI)", "Lectura"],
    "rows": [
        ["Quitar la elección de 2009", "0.94", "Casi iguales"],
        ["Usar solo elecciones presidenciales", "0.91", "Casi iguales"],
        ["Contar los no especificados como “no votó”", "1.0", "Idénticos"],
        ["Agrupar dentro de cada región y tipo de sección", "0.93 a 0.99 (centro, norte, urbana, mixta)",
         "Parecidos; excepción: rural 0.73 y sur rural 0.64"],
        ["Orden de los perfiles", "—", "El perfil 1 participa más que el 2, el 2 más que el 3 y el 3 más que el 4, en todos los cortes"],
    ],
    "widths": [0.38, 0.27, 0.35], "align": ["L", "C", "L"], "note": None,
}))
add(("p", "Un modelo predictivo (boosting con interpretación SHAP) apunta en el mismo sentido: la edad es la variable que más pesa (11.6 "
          "puntos de importancia media, frente a 5.5 del tipo de elección, 3.5 de la entidad, 2.1 del sexo y 1.7 del tipo de sección) "
          "y el modelo no supera una regla simple de promedios por edad."))

# ------------------------------------------------------------------ 4. PERFILES
add(("h1", "4. Los perfiles ciudadanos"))
add(("h2", "4.1 Qué significa “claramente diferenciados”"))
add(("p", "Los perfiles se distinguen por su **nivel de participación y su trayectoria**, no porque estén separados en los datos "
          "(sección 3.2). Se sostiene por tres razones que se pueden verificar:"))
add(("numbered", [
    "**Brechas amplias y sostenidas.** Entre un perfil y el siguiente hay de 10.6 a 23.2 puntos de diferencia en cada una de las seis elecciones.",
    "**Orden estable.** El perfil 1 participa siempre más que el 2, el 2 más que el 3 y el 3 más que el 4, en las seis elecciones y en "
    "todos los cortes por región y tipo de sección.",
    "**Composición distinta por sexo y edad** (sección 4.3).",
]))
add(("image", FIG / "fig1_perfiles_por_sexo_y_edad.png", 12.5,
     "Figura 1. Participación en 2024 por edad, para hombres y mujeres. El color indica el perfil. Los límites entre perfiles son "
     "cortes de una curva continua, no umbrales reales."))
add(("table", {
    "header": ["Perfil", "2009", "2012", "2015", "2018", "2021", "2024", "Media presid.", "Media interm.", "Dif."],
    "rows": [
        ["1. Alta", "54.8", "72.3", "58.4", "71.3", "62.9", "70.6", "71.4", "58.7", "12.7"],
        ["2. Intermedia", "42.4", "60.8", "44.5", "60.7", "48.7", "56.5", "59.3", "45.2", "14.1"],
        ["3. Baja", "31.2", "48.4", "32.6", "49.4", "36.8", "43.6", "47.1", "33.5", "13.6"],
        ["4. Muy mayores", "11.4", "26.4", "20.1", "26.2", "23.4", "31.1", "27.9", "18.3", "9.6"],
    ],
    "widths": [0.18, 0.08, 0.08, 0.08, 0.08, 0.08, 0.08, 0.13, 0.13, 0.08], "align": ["L"] + ["C"] * 9,
    "note": "Participación (%) entre registros con situación especificada. Presidenciales: 2012, 2018 y 2024; intermedias: 2009, 2015 y 2021. "
            "Las medias son simples; “Dif.” = presidenciales menos intermedias.",
}))
add(("h2", "4.2 Lo que comparten los cuatro perfiles"))
add(("bullets", [
    "**El ciclo electoral.** Todos suben entre 9.6 y 14.1 puntos en las presidenciales frente a las intermedias. Las curvas son casi "
    "paralelas: los perfiles se distinguen por nivel, no por forma.",
    "**Las intermedias subieron, las presidenciales de 2024 bajaron.** De 2009 a 2021, las intermedias subieron entre 5.6 y 8.1 puntos "
    "en los perfiles 1 a 3. En 2024, las presidenciales quedaron por debajo de 2018 en los perfiles 2 y 3 (−4.2 y −5.8 puntos) y casi "
    "igual en el 1 (−0.7). Las elecciones con más registros no especificados tienen una participación más incierta.",
    "**Las intermedias son el momento con más margen de mejora,** si se asume que el nivel de una presidencial es alcanzable; por "
    "grupo de edad, los jóvenes son los que más suben en las presidenciales.",
]))
add(("h2", "4.3 Ficha de cada perfil"))
add(("p", "Los tamaños y las participaciones por bloque de sexo y edad se calcularon con los conteos originales de 2024."))
add(("h3", "Perfil 1 · Participación alta: el núcleo adulto"))
add(("table", {
    "header": ["Bloque", "% de la lista nominal", "Participación 2024"],
    "rows": [["Mujeres de 39 a 77 años", "26.9 %", "71.0 %"], ["Hombres de 52 a 81 años", "13.4 %", "70.3 %"], ["Mujeres de 18 años", "0.8 %", "65.1 %"]],
    "widths": [0.5, 0.25, 0.25], "align": ["L", "C", "C"], "note": None,
}))
add(("bullets", [
    "**Qué lo caracteriza.** El mayor nivel (70 a 72 % en presidenciales y 55 a 63 % en intermedias) y la mayor parte de la lista "
    "nominal. Las mujeres entran a este nivel unos 13 años antes que los hombres.",
    "**Qué no se puede decir.** Que sea un grupo “comprometido” por naturaleza: es un corte de edad. Las mujeres de 18 años están aquí por "
    "un salto aislado en el borde de la curva, no porque formen un grupo con las de 39 a 77.",
]))
add(("h3", "Perfil 2 · Participación intermedia: la transición"))
add(("table", {
    "header": ["Bloque", "% de la lista nominal", "Participación 2024"],
    "rows": [["Mujeres de 19 a 38 años", "22.2 %", "56.8 %"], ["Hombres de 37 a 51 años", "13.3 %", "55.5 %"],
             ["Hombres de 18 a 19 años", "1.8 %", "52.7 %"], ["Mujeres de 78 a 83 años", "1.1 %", "63.7 %"],
             ["Hombres de 82 a 87 años", "0.6 %", "62.8 %"]],
    "widths": [0.5, 0.25, 0.25], "align": ["L", "C", "C"], "note": None,
}))
add(("bullets", [
    "**Qué lo caracteriza.** Es el perfil de las mujeres jóvenes y de los hombres de mediana edad. Su participación sube unos 14 puntos "
    "de las intermedias a las presidenciales y fue de las que más cayó en 2024 frente a 2018 (−4.2 puntos).",
    "**Qué no se puede decir.** Que su distancia con el perfil 1 sea “falta de interés”. El 91 % del perfil son dos bloques de naturaleza "
    "distinta (mujeres jóvenes y hombres de mediana edad). Los tramos de 78 a 87 años (1.7 %) participan en 2024 más que el promedio del "
    "perfil: están aquí por su trayectoria de seis elecciones, no por su nivel de 2024.",
]))
add(("h3", "Perfil 3 · Participación baja: sobre todo hombres jóvenes"))
add(("table", {
    "header": ["Bloque", "% de la lista nominal", "Participación 2024"],
    "rows": [["Hombres de 20 a 36 años", "18.7 % (18.4 millones)", "43.3 %"], ["Mujeres de 84 a 89 años", "0.6 %", "49.6 %"],
             ["Hombres de 88 a 92 años", "0.2 %", "48.0 %"]],
    "widths": [0.5, 0.25, 0.25], "align": ["L", "C", "C"], "note": None,
}))
add(("bullets", [
    "**Qué lo caracteriza.** Es el perfil de población amplia con menor participación; los hombres de 20 a 36 años son casi todo su "
    "tamaño. La participación masculina baja de 57.9 % a los 18 años a 49.0 % a los 19 y 45.6 % a los 20 (2024). Las mujeres "
    "participan más que los hombres hasta los 66 años, con una diferencia máxima de 14 puntos hacia los 29.",
    "**Qué no se puede decir.** Que las personas de 84 a 92 años (0.8 % de la lista nominal) comparten razones con los hombres jóvenes: "
    "solo se parecen en el nivel de sus seis tasas. Aun con cinco perfiles el método los sigue juntando; por eso, al diseñar acciones "
    "(sección 6), se tratan por separado según su composición.",
]))
add(("h3", "Perfil 4 · Edades muy avanzadas (90+)"))
add(("table", {
    "header": ["Bloque", "% de la lista nominal", "Participación 2024"],
    "rows": [["Mujeres de 90 a 99 años", "0.3 %", "30.9 %"], ["Hombres de 93 a 99 años", "0.1 %", "31.8 %"]],
    "widths": [0.5, 0.25, 0.25], "align": ["L", "C", "C"], "note": None,
}))
add(("bullets", [
    "**Qué lo caracteriza.** Participación de 11 % a 31 %. Es el perfil más pequeño.",
    "**Qué no se puede decir.** Que sus datos sean errores. Es un perfil con reserva: la lista nominal podría incluir personas "
    "fallecidas o que ya no viven en su sección, lo que haría parecer menor su participación real. No se verificó con los datos disponibles.",
]))

# ------------------------------------------------------------------ 5. LUGAR Y CICLO
add(("h1", "5. Dónde y cuándo cambia el nivel"))
add(("h2", "5.1 Región y tipo de sección: mueven el nivel, no la forma"))
add(("p", "La curva nacional de sexo, edad y elección explica 95 % de la variación en cada región y en cada tipo de sección. Si a cada "
          "grupo se le suma un nivel propio, el ajuste sube a 99.6 % (regiones) y 98.9 % (tipos de sección). El ajuste de nivel, en "
          "puntos porcentuales, es:"))
add(("table", {
    "header": ["Norte", "Centro", "Sur", "Urbana", "Mixta", "Rural"],
    "rows": [["−3.7", "+1.0", "+2.3", "−1.1", "+0.3", "+4.1"]],
    "widths": [1 / 6] * 6, "align": ["C"] * 6, "note": None,
}))
add(("p", "Que 95 % se explique con edad y sexo no vuelve irrelevante el lugar: la edad domina tanto que 4 a 7 puntos de diferencia por "
          "región o tipo de sección siguen siendo importantes en la práctica."))
add(("p", "**Excepción: las secciones rurales, sobre todo las del sur.** Ahí cambia también la forma del patrón por edad y sus perfiles "
          "propios coinciden menos con los nacionales. Se recomienda tratarlas como un caso aparte."))
add(("h2", "5.2 El lugar importa más a nivel de municipio que de región"))
add(("bullets", [
    "En unos 1,600 municipios con datos suficientes en 2024, la diferencia de participación entre adultos de 35 a 64 años y jóvenes de "
    "18 a 34 va de 7.9 a 21.6 puntos entre municipios; la de adultos frente a personas de 85 años o más, de 14.0 a 33.3. La entidad "
    "explica 41 % y 28 % de esa variación; el resto ocurre dentro de la entidad.",
    "Las dos brechas casi no se relacionan entre sí (correlación de −0.01 a 0.19). Es el argumento más directo para diseñar acciones "
    "separadas para jóvenes y para edades muy avanzadas.",
    "Los municipios más grandes tienden a una brecha juvenil mayor y los más rurales a brechas mayores en ambos grupos. Son "
    "asociaciones construidas con variables del propio padrón, no causas.",
]))
# ------------------------------------------------------------------ 6. ESTRATEGIAS
add(("h1", "6. Estrategias diferenciadas"))
add(("h2", "6.1 Principios"))
add(("bullets", [
    "**Son hipótesis, no resultados.** Los datos dicen quién participa menos, no por qué. Cada estrategia parte de una evidencia, "
    "plantea una idea sobre la barrera y define cómo se mediría su efecto (sección 7).",
    "**Se dirigen a grupos y territorios, no a personas.** Se focaliza por perfil, municipio y sección electoral.",
    "**Son informativas y de facilitación:** educación cívica, comunicación y promoción de la participación, sin contenido partidista.",
    "**Se prioriza por tamaño y por distancia** respecto del perfil de mayor participación.",
]))
add(("h2", "6.2 Dónde está el mayor espacio de mejora"))
add(("p", "La cuenta siguiente es un tope teórico, no una meta: cuántos puntos subiría la participación nacional si un grupo alcanzara "
          "la participación del perfil 1 en 2024 (tamaño × distancia)."))
add(("table", {
    "header": ["Grupo", "% de la lista nominal", "Distancia con el perfil 1 (puntos)", "Efecto máximo en la participación nacional (puntos)"],
    "rows": [["2. Intermedia", "39.0", "14.1", "5.5"], ["3. Baja: hombres de 20 a 36 años", "18.7", "27.3", "5.1"],
             ["3. Baja: personas de 84 a 92 años", "0.8", "21.4", "0.2"], ["4. Edades muy avanzadas (90+)", "0.4", "39.5", "0.2"]],
    "widths": [0.34, 0.18, 0.24, 0.24], "align": ["L", "C", "C", "C"], "note": None,
}))
add(("p", "El perfil 2 y los hombres jóvenes del perfil 3 concentran casi todo el margen. Los grupos de edades muy avanzadas pesan "
          "poco en tamaño y su brecha puede ser en parte un efecto del padrón."))
add(("h2", "6.3 Matriz de estrategias"))
add(("table", {
    "header": ["Perfil", "Educación cívica", "Comunicación", "Promoción y facilitación"],
    "rows": [
        ["**1. Alta** (sostener)", "Mantener información sobre la función de las elecciones intermedias",
         "Recordatorio de fecha y lugar de votación, sobre todo en intermedias",
         "Documentar qué acciones locales funcionan antes de llevarlas a otros grupos"],
        ["**2. Intermedia** (continuidad en intermedias)", "Explicar qué se decide en las elecciones intermedias",
         "Mensajes distintos para mujeres de 19 a 38 años y para hombres de 37 a 51",
         "Facilitar el acceso a la casilla y la información práctica en el periodo intermedio"],
        ["**3A. Baja:** hombres de 20 a 36 años", "Educación cívica que acompañe la transición del primer voto",
         "Canales y formatos propios de este grupo", "Contacto en los puntos donde ya se relacionan con la institución"],
        ["**3B y 4.** Edades muy avanzadas (84+)", "Información accesible y en formatos adecuados",
         "Comunicación dirigida a la persona y a su entorno",
         "Primero verificar el padrón; después, accesibilidad y movilidad"],
    ],
    "widths": [0.22, 0.26, 0.26, 0.26], "align": ["L", "L", "L", "L"], "note": None,
}))
add(("h2", "6.4 Detalle por línea"))
add(("bullets", [
    "**Perfil 1 · Alta (sostener).** **Evidencia:** el nivel más alto (70 a 72 % en presidenciales) y 12.7 puntos de diferencia con las "
    "intermedias. **Idea a probar:** mantener el acceso a información cívica evita una caída y las experiencias locales exitosas sirven "
    "de referencia, sin asumir que funcionen igual en otros grupos. **Cómo medirlo:** participación en la intermedia de 2027 frente a su "
    "trayectoria en intermedias (54.8 %, 58.4 % y 62.9 % en 2009, 2015 y 2021).",
    "**Perfil 2 · Intermedia (continuidad en intermedias).** **Evidencia:** 39 % de la lista nominal, 14.1 puntos de diferencia entre "
    "presidenciales e intermedias y −4.2 puntos en 2024 frente a 2018. **Idea a probar:** la caída se reduce más con información práctica "
    "y oportuna (fecha, lugar, qué se elige) que con mensajes generales; no está probada. Prioritario donde la brecha entre adultos y "
    "jóvenes es mayor (municipios grandes y zonas del sur y centro-sur, por lectura aproximada del mapa). **Cómo medirlo:** la diferencia "
    "presidencial–intermedia del perfil en 2027 frente a 2021.",
    "**Perfil 3A · Hombres de 20 a 36 años.** **Evidencia:** 18.7 % de la lista nominal; la participación baja de 57.9 % a los 18 años a "
    "45.6 % a los 20, y las mujeres de su edad participan hasta 14 puntos más. **Idea a probar:** la caída ocurre justo después del primer "
    "voto, así que acompañar esa transición (hasta los 20–22 años) puede ser más eficaz que una campaña general; la causa no está "
    "probada. **Cómo medirlo:** participación de los hombres de 18 a 24 años en las secciones piloto frente a las de comparación.",
    "**Perfiles 3B y 4 · Edades muy avanzadas (84+).** **Evidencia:** suman alrededor de 1.2 % de la lista nominal y participan entre 31 % "
    "y 50 %. **Idea a probar:** antes de actuar, saber si la baja participación es real o un efecto del padrón (personas fallecidas o que "
    "ya no viven en la sección); si es real, las barreras probables son de movilidad y acceso. **Acción previa:** contrastar el padrón "
    "con registros administrativos externos, que este análisis no tiene.",
    "**Estrategia común y caso aparte.** Todos los perfiles bajan entre 10 y 14 puntos en las intermedias: una estrategia común para la "
    "próxima (prevista para 2027) tiene la mayor escala y las líneas por perfil afinan mensaje y canal. En las secciones rurales del sur, "
    "donde cambia la forma del patrón por edad, las acciones se diseñan con el contexto local.",
]))

# ------------------------------------------------------------------ 7. PILOTOS
add(("h1", "7. Cómo probar las estrategias"))
add(("p", "Cada estrategia se prueba en pequeño antes de escalarla:"))
add(("bullets", [
    "**Diseño.** Dentro de municipios elegidos, se asignan al azar secciones electorales a tratamiento y a comparación.",
    "**Indicador.** La participación del grupo objetivo (sexo × edad) en la elección siguiente, que se puede medir con los mismos "
    "conteos por sección, sexo y edad que publica el INE.",
    "**Comparación.** El cambio en las secciones con intervención frente al cambio en las de comparación, contra la tendencia previa "
    "(diferencia en diferencias).",
    "**Tamaño de la prueba.** El efecto que se puede detectar depende del número de secciones; debe calcularse antes de lanzar un piloto.",
    "**Criterio de éxito.** Se define antes de la intervención y se reporta aunque el resultado sea nulo.",
]))

# ------------------------------------------------------------------ 8. LÍMITES
add(("h1", "8. Límites"))
add(("bullets", [
    "**No hay causas.** Son datos agregados de grupos, no de personas, sin motivos, escolaridad ni ingreso; toda explicación de por qué "
    "participa menos un perfil es una hipótesis. Además, edad, época y generación no se pueden separar.",
    "**Los límites entre perfiles no son umbrales naturales.** Dependen del método y del número de perfiles (sección 3.2). Dos de las "
    "cuatro pruebas de agrupamiento quedaron en “ambiguo”, las pruebas que apuntan a “sin estructura” se agregaron después de ver los "
    "resultados y los umbrales para interpretar Hopkins son orientativos.",
    "**El perfil 4 puede estar mal medido:** la lista nominal puede incluir personas fallecidas o que ya no viven en su sección. No se verificó.",
    "**Los 18 años son un salto real** cuya causa no se determinó, y la tabla de 164 grupos no aplica un tamaño mínimo, por lo que las "
    "edades extremas tienen pocos registros.",
    "**La regionalización norte, centro y sur es una propuesta del proyecto,** no una división oficial; su referencia sigue pendiente "
    "de documentar. El análisis es nacional, las diferencias locales pueden ser grandes y no hay validación externa contra encuestas.",
    "**Personas no binarias:** quedaron fuera por falta de historial y se describen aparte.",
]))

# ------------------------------------------------------------------ ANEXOS
add(("h1", "Anexo A. Pruebas de tendencia al agrupamiento"))
add(("p", "Las cuatro pruebas se hicieron sobre unidades distintas para que la conclusión no dependa de una sola forma de armar la tabla. "
          "Cada resultado se compara con una referencia sin grupos (datos aleatorios con la misma relación entre las seis tasas, o una "
          "curva continua por construcción); la diferencia entre ambos se llama delta."))
add(("table", {
    "header": ["Prueba", "Unidad", "Resultado (Hopkins)", "Lectura"],
    "rows": [
        ["**1.** Forma de la trayectoria (ciclo y tendencias, sin el nivel)", "1,458 unidades",
         "Forma: real 0.748–0.810; referencia 0.649–0.723; delta +0.086 a +0.099. Ciclo: real 0.766–0.823; referencia 0.766–0.819; delta −0.016 a +0.013",
         "Sin evidencia en el ciclo; moderada solo en la forma con entidad"],
        ["**2.** Perfiles adoptados", "164 grupos", "Real 0.946; referencia 0.935–0.936; delta +0.010 a +0.011",
         "Ambiguo: un solo salto real, a los 18 años"],
        ["**3.** Fichas por región", "144 grupos", "Real 0.831–0.867; referencia 0.851–0.881; delta −0.022 a −0.001",
         "Ambiguo; sin estructura más allá del gradiente"],
    ],
    "widths": [0.24, 0.13, 0.40, 0.23], "align": ["L", "L", "L", "L"], "note": None,
}))
add(("p", "También se calcularon la separación (silhouette), que va de 0.51 a 0.61, y la coincidencia (ARI), de 0.89 a 0.97. Una "
          "simulación de 164 puntos sobre una curva continua, sin grupos por construcción, da 0.51 a 0.59 de separación y 0.86 a 0.97 de "
          "coincidencia. Ambas métricas miden qué tan separado y qué tan repetible es un corte, no si el corte corresponde a grupos que "
          "existen. La ausencia de grupos naturales no impide segmentar: k-means, Ward y otros métodos siguen dando cortes útiles y estables."))
add(("h1", "Anexo B. Reproducibilidad"))
add(("p", "Semilla fija: 42. Las dependencias están en requirements-analysis.txt; los ZIP originales están en data/raw/ y el dataset "
          "maestro permanece local. **Scripts:** 01_etl_calidad.py y 02_cubo.py (ETL y validación), perfiles_sociodemograficos.py "
          "(fichas por región), 17_perfiles_edad_sexo.py, 18_perfiles_por_region_tipo.py, 19_revision_ns_nobinario.py y "
          "20_figuras_perfiles.py (perfiles por sexo y edad), 21_tamano_bloques_perfiles.py (tamaño de cada bloque) y los cuatro "
          "notebooks de tendencia al agrupamiento (notebooks/README.md). **Más detalle:** metodologia_perfiles/METODOLOGIA.md y "
          "reports/perfiles_sexo_edad/README.md."))

BLOQUES = B
