# Métodos inversos: recuperación de algoritmos académicos

**Edgar Lemuel Fuentes Solano · EDGAR LEMUEL / GEOPHYSICS**

Recuperación documentada de cinco códigos MATLAB académicos y migración a Python de búsqueda local, recocido simulado y algoritmo genético binario. El proyecto separa una comparación sobre una función de prueba de dos parámetros y una inversión polinomial sobre datos sintéticos. No utiliza observaciones geofísicas reales.

Los cinco `.m` permanecen intactos. Los resultados publicados en esta carpeta se obtuvieron con **Python 3.12.0 en Windows**, NumPy 2.2.3 y Matplotlib 3.10.1. No se ejecutó MATLAB ni Octave, por lo que no se afirma equivalencia de ejecuciones entre lenguajes.

## Estado de la recuperación

Al reanudar ya estaban implementados los algoritmos Python y guardados los 30 experimentos comparativos, dos reproducciones continuas y dos historiales polinomiales. Se conservaron esos resultados sin sobrescribirlos.

Se completaron la revisión del código, las comprobaciones de entrada, la protección contra sobrescritura, las pruebas numéricas y de reproducibilidad, las cinco figuras en dos temas y este documento. El fallo previo al graficar se produjo al invocar `runpy` sin añadir la carpeta de módulos a la ruta de importación. La ejecución directa de los scripts resuelve sus importaciones y está comprobada en Windows.

El [diagnóstico técnico](diagnostico.md) describe por archivo las funciones de costo, dominios, aceptación, parada y correcciones. No hay cambios matemáticos aplicados sobre los originales.

## Estructura

```text
Metodos_Inversos/
├── matlab_original/              # Cinco fuentes originales, sin cambios
├── python/
│   ├── problemas.py              # Dos superficies y problema polinomial
│   ├── reproduccion_original.py  # Reproducciones Python, incluidos defectos documentados
│   ├── algoritmos.py             # Métodos corregidos y extensiones
│   ├── ejecutar.py               # Experimentos con semillas y presupuestos fijos
│   ├── visualizar.py             # Cinco figuras, temas oscuro y claro
│   ├── test_numerica.py          # 19 pruebas; recalculan resultados en memoria
│   └── validar.py                # Pruebas, revisión de figuras e informe
├── resultados/
│   ├── resumen.json
│   ├── comparacion.csv           # 30 filas, una por método y semilla
│   ├── superficies.npz
│   ├── polinomio.npz
│   ├── genetico_inicial_original.npz
│   └── historiales/              # 34 CSV de convergencia
├── Figuras/
│   ├── oscuro/                  # Cinco PNG a 300 dpi y cinco SVG
│   └── claro/                   # Los mismos nombres y formatos
├── diagnostico.md
├── requirements.txt
└── validacion.json
```

`comprobacion_windows.json` documenta además una ejecución completa desde otra carpeta, con resultados y figuras en salidas temporales nuevas, y las pruebas de rechazo de sobrescritura.

`matlab_original/` conserva `geneticos1.m`, `modelo22.m`, `modelo25.m`, `modelo27.m` y `recristalizacion_simulada.m`. Sus hashes SHA-256 están en `resultados/resumen.json` y se vuelven a comprobar al validar.

## Superficie de prueba

Los parámetros m₁ y m₂ son adimensionales. La función común es

```text
Z1 = 6 (m1/6 - m1³ - m2⁵) exp[-(m1 - 1/2)² - m2²]
Z2 = 2 exp[-(m1 + 1)² - m2²]
B  = (1 - m1)² exp[-2 m1² - (m2 + 1)²]
Z4 = 1/2 sin(3 m1) + cos(5 m2/2)
E(m1,m2) = Z1 + Z2 - 6 B + Z4 + 10
```

Es la expresión compartida por `modelo22`, `modelo25` y `geneticos1`. No es una norma de residuos asociada a datos observados. `recristalizacion_simulada` define otra superficie, `F = Z1 + Z2 + 6 B + Z4`, cuya diferencia con E es `10 - 12 B`; no se mezclan sus resultados.

La comparación utiliza **la misma malla de 61×61 nodos en [-3,3]²**, con paso 0.1, para los tres métodos. Esta discretización es una extensión de comparación: las reproducciones de búsqueda local y recocido MATLAB siguen siendo continuas. Se enumeran exhaustivamente los 3 721 nodos como referencia independiente de los optimizadores.

El menor costo de esa malla es **1.6859520740173402**, en **(-0.4, -1.0)**. Una malla adicional de 301×301 nodos produce **1.6824200872034822** en **(-0.4, -0.98)**. Ese valor menor muestra por qué alcanzar la referencia gruesa **no demuestra optimalidad global continua**. La malla fina se presenta como sensibilidad a la resolución, no como un error exigible al genético restringido a la malla gruesa.

## Tres niveles separados

1. **Fuentes originales MATLAB.** Inalteradas, incluidos sus problemas lógicos y partes ausentes.
2. **Reproducciones de operaciones en Python.** `modelo22` conserva amplitudes y propuestas sin límites. `modelo25` conserva el salto incorrecto de valores menores que −3 hacia +3. El polinomio conserva su caja incompatible. No se garantiza identidad de secuencias aleatorias con MATLAB.
3. **Versiones corregidas y extensiones.** Función común, propuestas acotadas y discretas, temperaturas nuevas para la comparación, representación binaria numérica, selección por torneo, reparación coherente, elitismo y registro de evaluaciones.

En el genético original no se suministró `vale(parejas)`, aparece la variable no definida `mil`, ambas ramas de mutación escriben cero y faltan evolución generacional y supervivientes. La inicialización de diez individuos con dos cromosomas de diez bits y la mutación defectuosa se reproducen de forma aislada. `evolucion_genetica_original()` falla explícitamente con una explicación: no se inventó un algoritmo MATLAB completo donde falta código. El **genético corregido sí está completo**.

`recristalizacion_simulada.m` solo define su superficie y el punto inicial `(0.7,-1.8)`. No se le atribuyen temperaturas, convergencia ni resultados de un recocido que el archivo no implementa. Su mínimo enumerado en la malla 61×61 es −6.376513515366941 en `(1.5,0)`.

## Configuración del experimento comparativo

Semillas, en orden:

```text
7, 19, 42, 73, 101, 137, 211, 307, 401, 503
```

Cada combinación de método y semilla dispone de **6 000 evaluaciones de costo**, incluida la evaluación inicial o la población inicial. Una llamada vectorizada que evalúa 40 individuos cuenta como 40 evaluaciones. Las repeticiones, propuestas que coinciden con un extremo y modelos duplicados también cuentan. Los costos almacenados de padres se reutilizan sin contarlos de nuevo.

| Método | Configuración corregida usada |
|---|---|
| Búsqueda local | Inicio `(-1.6,0.6)`, alterna coordenadas, desplaza un nodo en signo aleatorio y acepta solo mejoras estrictas. Proyecta a la malla si cruza un extremo. |
| Recocido simulado | Mismo inicio, desplaza entre uno y cinco nodos por coordenada. Ocho ciclos de dos propuestas por nivel; temperatura geométrica de 10 a 1e-5. Acepta mejoras, empates y propuestas peores según Metropolis. |
| Genético binario | 40 individuos iniciales aleatorios, seis bits por parámetro, selección por torneo de tres, cruce de un punto y mutación independiente por bit con probabilidad 1/12. Supervivientes: mejores 40 entre padres e hijos, con elitismo. |

El presupuesto puede terminar en un bloque incompleto. Con 6 000 evaluaciones se registran hasta 3 000 barridos locales, 375 niveles térmicos y 149 generaciones posteriores a la población inicial. Estos contadores no equivalen en esfuerzo; se comparan las evaluaciones y no el número bruto de iteraciones. La comparación no incluye una medida de tiempo de pared.

La codificación almacena los valores enteros 1..61, como en MATLAB, pero los índices NumPy son 0..60. Los códigos cero y 62..63 se reparan mediante muestreo uniforme y se **recodifican**. La función permite diez bits para verificar el diseño original; no es la configuración moderna por defecto. La mutación usa XOR: 0↔1. Los padres y los hijos conservan costos separados y el mejor superviviente no empeora.

El mejor costo se conserva también en el recocido, aunque el costo actual pueda aumentar. La aceptación de propuestas peores del recocido discreto compara `log(u) < -ΔE/T`, con tratamiento explícito de `u=0`. No hay parada por umbral absoluto en la comparación principal: todos los métodos consumen el mismo presupuesto.

## Resultados comparativos conservados

| Método | Mediana del mejor costo | Mediana de la brecha de malla | Ejecuciones que alcanzan la referencia |
|---|---:|---:|---:|
| Búsqueda local | 8.536123582899998 | 6.850171508882658 | 0/10 |
| Recocido simulado | 1.727963261714235 | 0.042011187696894936 | 5/10 |
| Genético binario | 1.6859520740173402 | 0 | 9/10 |

Se considera coincidencia con la referencia una diferencia de costo ≤1e-12. La brecha es `E_mejor − E_malla`; la distancia de parámetros es la norma euclidiana respecto al nodo de referencia. `comparacion.csv` registra ambas, el costo, el modelo, las evaluaciones, el contador de iteración/generación, las reparaciones y la primera evaluación donde se observa la referencia, si se alcanzó. En el genético la observación es por lote generacional, no por orden individual dentro del lote.

**No se descartan los fallos.** La búsqueda local queda atrapada en otro mínimo en las diez ejecuciones. El recocido no alcanza la referencia para semillas **42, 73, 211, 307 y 503**. El genético falla en la semilla **211**, con mejor costo 1.9254093049171122. La Figura 02 conserva la trayectoria de recocido de la semilla 42, aunque no alcance el mejor nodo. Diez realizaciones fijas no estiman una probabilidad universal de éxito ni prueban superioridad general de un método.

Las reproducciones continuas, calculadas en Python con semilla 42, son experimentos separados: `modelo22` alcanza costo 8.529618738619126 tras 1 001 evaluaciones y agota 500 barridos; `modelo25` conserva costo 1.720469114889914 tras 3 361 evaluaciones y termina por el umbral del estado actual. No deben compararse como si hubieran usado el presupuesto y el espacio discreto del experimento principal.

## Caso inverso polinomial

Se conserva la formulación de `modelo27.m`:

```text
x = -10:0.1:10                  # 201 muestras, sin ruido
G = [1, x, x², x³]
m_true = [500, 50, 5, 0.5]ᵀ
d = G m_true
E(m) = ||d - Gm||₂
```

El modelo es cúbico en x y **lineal en los coeficientes**. La migración utiliza `linspace` con los mismos extremos y número de puntos; esto no garantiza identidad bit a bit con la construcción de la malla en MATLAB. No hay unidades geofísicas asociadas a x o d.

La caja original `[-3,3]⁴` excluye tres coeficientes verdaderos. En x=0 impone un error de al menos 497, de modo que su tolerancia 1 es imposible. La reproducción conserva ese defecto para evidenciarlo: no se cambia el dato sintético para hacer que parezca converger.

La referencia de mínimos cuadrados usa `np.linalg.lstsq(G,d,rcond=None)` y G tiene rango 4. El escalado para la otra versión de recocido es:

```text
A_j = G_j / ||G_j||₂
y = d / ||d||₂
q_j = m_j ||G_j||₂ / ||d||₂
m_j = q_j ||d||₂ / ||G_j||₂
```

El recocido escalado minimiza `||y-Aq||₂`, con `q∈[-2,2]⁴`, inicio cero, amplitud 0.12, temperaturas `0.1→1e-8`, 1 000 niveles y 12 ciclos de cuatro coordenadas. Consume **48 001 evaluaciones**, sin parada por tolerancia. La normalización utiliza G y d, no los coeficientes verdaderos para proponer o aceptar. Los límites nuevos sí contienen la solución de este caso; no constituyen una elección universal para otros problemas.

El número de condición de G es aproximadamente **575.589** y el de sus columnas normalizadas, **4.79174**. Los errores siguientes están expresados en las unidades originales de d, no en la norma normalizada:

| Procedimiento | Coeficientes conservados | Residuo L₂ |
|---|---|---:|
| Verdadero | `[500, 50, 5, 0.5]` | 0 por construcción |
| Mínimos cuadrados | `[500.000000000002, 49.99999999999958, 4.9999999999999645, 0.5000000000000016]` | 3.304505021630365e-11 |
| Recocido con caja original | `[3, 3, 3, 1.1515577539804058]` | 8193.484347201927 |
| Recocido escalado | `[499.96616439630634, 50.0862215818106, 5.000696946854008, 0.49869772112863836]` | 2.9149365393296316 |

La reproducción de la caja original usa **6 401 evaluaciones**. El recocido escalado mejora el ajuste, pero **no llega a residuo <1** en esta realización. No se oculta ese resultado ni se presenta el mejor modelo encontrado como solución exacta. Mínimos cuadrados es la referencia apropiada para este caso lineal sin ruido; las heurísticas no aportan aquí una ventaja numérica demostrada. Este experimento tiene otro costo y otro presupuesto que la comparación de tres algoritmos sobre E.

## Figuras definitivas

Las cinco figuras tienen variantes oscuras y claras con atribución personal, tipografía DejaVu Sans, acentos rojo mineral y etiquetas explícitas de simulación. Se generan **10 PNG a 300 dpi y 10 SVG vectoriales**, sin raster incrustado en los SVG. Los títulos y datos se conservan entre temas. Para conservar la apariencia de texto editable en otro equipo debe estar instalada DejaVu Sans.

| Archivo base | Contenido |
|---|---|
| `01_superficie_costo` | Superficie 3D y referencia del menor costo enumerado en la malla común. |
| `02_contornos_trayectorias` | Estados actuales de local y recocido; mejor superviviente por generación en el genético. Semilla 42 y referencia discreta. |
| `03_convergencia` | Mediana y rango observado por evaluaciones para diez semillas; contadores propios de la semilla 42 en un panel separado. |
| `04_comparacion_algoritmos` | Diez costos finales por método, medianas y número de coincidencias con el mínimo de la malla. |
| `05_inversion_polinomial` | Datos, predicciones, residuos con escala simétrica logarítmica, convergencia y coeficientes; incluye los ajustes que no convergen. |

Las áreas de la Figura 03 son rangos mínimo–máximo observados, no intervalos de confianza. Una trayectoria genética conecta mejores supervivientes y no representa un desplazamiento físico. Las superficies 3D se basan en nodos discretos y sus polígonos de visualización no certifican un óptimo entre nodos.

## Reproducción en Python 3.12 y Windows

Los comandos siguientes se ejecutan desde la raíz del portafolio. Las rutas internas se resuelven respecto a los scripts; también funcionan desde otra carpeta usando rutas completas. `python --version` debe mostrar Python 3.12 para reproducir el entorno comprobado.

**Comprobar la entrega existente, sin regenerar resultados ni figuras:**

```powershell
python --version
python Proyectos/Metodos_Inversos/python/validar.py
```

El validador vuelve a calcular los experimentos **en memoria**, compara sus historiales con los conservados, comprueba los originales y revisa las figuras existentes sin sobrescribirlas. Actualiza únicamente `validacion.json`. Las pruebas numéricas por separado son:

```powershell
python -m unittest discover -s Proyectos/Metodos_Inversos/python -p test_numerica.py -v
```

**Reproducir cálculos y figuras en carpetas nuevas**, conservando la entrega:

```powershell
python Proyectos/Metodos_Inversos/python/ejecutar.py --salida Proyectos/Metodos_Inversos/resultados_reproduccion
python Proyectos/Metodos_Inversos/python/visualizar.py --resultados Proyectos/Metodos_Inversos/resultados_reproduccion --salida Proyectos/Metodos_Inversos/Figuras_reproduccion --sin-mostrar
```

Las carpetas de reproducción deben estar vacías o no existir. Los scripts se niegan a sobrescribir los resultados o figuras de una salida ya ocupada. Para otra reproducción, usa otros nombres de carpeta. `--presupuesto` permite explorar otro presupuesto, pero deja de reproducir el experimento documentado de 6 000 evaluaciones.

Para exportar una copia de las figuras conservadas y después abrir las diez ventanas interactivas:

```powershell
python Proyectos/Metodos_Inversos/python/visualizar.py --salida Proyectos/Metodos_Inversos/Figuras_interactivas
```

Con `--sin-mostrar`, el script selecciona Agg antes de crear figuras y no requiere una ventana gráfica. El validador también usa Agg. No es necesario invocar `runpy` ni configurar `PYTHONPATH` para estos comandos.

Si las dependencias no están disponibles, pueden instalarse en un entorno local del proyecto, sin modificar Python global:

```powershell
python -m venv Proyectos/Metodos_Inversos/.venv
Proyectos/Metodos_Inversos/.venv/Scripts/python.exe -m pip install -r Proyectos/Metodos_Inversos/requirements.txt
```

Después se sustituye `python` en los comandos anteriores por `Proyectos/Metodos_Inversos/.venv/Scripts/python.exe`. No se instaló ni actualizó ninguna biblioteca durante esta entrega. Pillow, utilizado para revisar PNG, forma parte de las dependencias de Matplotlib.

## Validación y límites

Las **19 pruebas** cubren las dos funciones de costo, enumeración exhaustiva de la malla, codificación de sus 3 721 pares con seis y diez bits, índices inválidos, reparación y recodificación, cruce, mutación 0↔1, aceptación de Metropolis, presupuesto real de evaluaciones, elitismo y límites. También verifican la reproducción exacta en este entorno de los 30 historiales comparativos, las reproducciones continuas y los dos historiales polinomiales, además de mínimos cuadrados y los casos que no alcanzan la referencia.

`validacion.json` registra las pruebas, versiones, hashes de los originales, integridad de los resultados y las 20 exportaciones. Se comprobaron textos dentro del lienzo y sin solapamientos, contraste y resolución. La revisión automática de textos se complementó con inspección visual de las figuras. La reproducción numérica exacta está comprobada en el entorno indicado; otras versiones, CPU o bibliotecas pueden introducir diferencias en últimos dígitos o decisiones cercanas a un empate.

La comprobación exhaustiva demuestra el menor valor **solo entre los nodos enumerados**. Los algoritmos usan un inicio local fijo frente a una población genética aleatoria; igualar evaluaciones no elimina esa diferencia de diseño. No se evalúan otros problemas de prueba, ruido, incertidumbre, tiempos de ejecución ni poblaciones alternativas. No se concluye superioridad general de una heurística.

Quedan fuera de esta entrega una ejecución independiente en MATLAB/Octave para contrastar traducciones, completar los componentes no suministrados del genético original y diseñar una inversión con observaciones geofísicas reales. La integración web y la publicación permanecen pendientes por decisión del autor; no se modificó el portafolio principal ni los otros proyectos.
