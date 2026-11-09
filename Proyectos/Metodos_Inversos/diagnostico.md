# Diagnóstico de los originales MATLAB

Autor: Edgar Lemuel Fuentes Solano. Los cinco archivos de `matlab_original/` se conservan sin modificaciones. El análisis es estático y las ejecuciones de esta entrega corresponden a Python 3.12; no se ejecutaron MATLAB ni Octave.

## Funciones de costo

Definiendo

```text
Z1 = 6 (m1/6 - m1³ - m2⁵) exp[-(m1 - 1/2)² - m2²]
Z2 = 2 exp[-(m1 + 1)² - m2²]
B  = (1 - m1)² exp[-2 m1² - (m2 + 1)²]
Z4 = 1/2 sin(3 m1) + cos(5 m2/2)
```

`modelo22.m`, `modelo25.m` y `geneticos1.m` usan `E = Z1 + Z2 - 6 B + Z4 + 10`. `recristalizacion_simulada.m` usa `F = Z1 + Z2 + 6 B + Z4`. Por tanto,

```text
E - F = 10 - 12 B
```

La diferencia no es una constante: cambia el signo de un término y puede cambiar la posición del mínimo. No se asume que una variante sea un error de transcripción. Se conservan ambas en `problemas.costo`, y la comparación de algoritmos utiliza explícitamente E, compartida por tres originales. La suma de 10, por sí sola, no cambia los minimizadores ni los incrementos de costo, pero sí afecta un umbral absoluto de parada.

## Estado de cada archivo

| Original | Método y estado | Exploración, aceptación y parada |
|---|---|---|
| `modelo22.m` | Búsqueda local aleatoria por coordenadas; ciclo completo. | Inicio `[-1.6, 0.6]`, perturbación uniforme ±0.1 por componente, acepta solo si disminuye E. Máximo 500 barridos o costo actual ≤1.9, comprobado al inicio del barrido. |
| `modelo25.m` | Recocido por coordenadas con regla de Metropolis; ciclo completo, con errores de límites y registro. | Inicio `[-1.6, 0.6]`, amplitud ±0.5, ocho ciclos de dos coordenadas por temperatura. `Ti=1e6`, `Tf=1e-7`, 500 niveles o costo actual ≤2. |
| `geneticos1.m` | Preparación de población, cruce y mutación; evolución incompleta. | Malla 61×61, 10 individuos, dos cromosomas de 10 bits, cruce de un punto. No existe ciclo de 120 generaciones, selección de supervivientes ni parada operativa por generaciones. |
| `recristalizacion_simulada.m` | Superficie alternativa y evaluación inicial; no contiene algoritmo de recocido. | Inicio `[0.7, -1.8]`. El archivo termina antes de definir temperatura, propuestas, aceptación o parada. |
| `modelo27.m` | Recocido para un problema inverso polinomial sintético; ciclo completo pero dominio incompatible. | Inicio cero, amplitudes `[10,1,0.1,0.01]`, ocho ciclos de cuatro coordenadas, 200 temperaturas de `1e6` a `1e-6`, parada por costo actual ≤1. |

## Búsqueda local

- La superficie se dibuja en `[-3,3]²`, pero no se imponen esos límites a las propuestas. Dibujar un dominio no restringe el optimizador.
- Las aceptaciones estrictamente descendentes pueden quedar atrapadas en un mínimo local. `TOL=1.9` es un umbral de costo, no una norma del gradiente, una tolerancia entre iteraciones ni evidencia de convergencia global.
- `mp` se mantiene consistente al restablecer la coordenada rechazada. No hay un error automático por reutilizarlo en este archivo.
- Los comentarios que mencionan profundidad y densidad no convierten m1 y m2 en parámetros físicos: el dominio incluye valores negativos y no existen observaciones ni un operador geofísico.

La reproducción Python conserva la falta de límites y las amplitudes. El experimento corregido se distingue expresamente: trabaja sobre la malla común y recorta propuestas al dominio.

## Recocido de modelo25

- Si una propuesta baja de −3, el código la coloca en **+3**. Esto introduce un salto artificial de un extremo al otro. La versión corregida proyecta a −3 mediante `clip`; la reproducción conserva el salto.
- `DP` solo se define en la rama que no mejora el costo. El gráfico puede usar un valor anterior, o una variable sin inicializar si todavía no se ha entrado en esa rama. Los historiales Python de reproducción no pretenden reproducir ese gráfico defectuoso.
- La temperatura inicial es muy grande respecto a las variaciones típicas de E: muchas propuestas peores tienen aceptación cercana a uno. No es un error aritmético, pero condiciona la exploración.
- La parada usa el **estado actual**, no el mejor conservado. `mopt/Eopt` y el estado final son conceptos distintos. El umbral se revisa al principio del siguiente nivel, no después de cada propuesta.
- `Tf` se alcanza al completar la última actualización de temperatura; las últimas propuestas se realizan a una temperatura ligeramente superior. La reproducción mantiene esa convención.
- La exponencial puede subdesbordar a cero a baja temperatura; esa probabilidad nula no implica por sí sola un fallo. El recocido discreto corregido compara logaritmos para evitar evaluar la exponencial.

## Algoritmo genético

| Hallazgo | Consecuencia | Tratamiento en Python |
|---|---|---|
| Ambos casos de la mutación escriben `'0'`. | Solo borra unos; nunca produce `0→1`. | `mutacion_original` conserva el defecto para demostrarlo; `mutar` usa XOR y permite ambos cambios. |
| `mil` en `m1total=[mil;m1h]`. | No corresponde a `mi1`, definido antes; con `clear all`, `mil` queda sin definir en el código entregado. | No se intenta completar silenciosamente la reproducción; el genético corregido usa índices separados. |
| `vale(parejas)` no está entre los archivos suministrados. | No puede verificarse su implementación ni completarse la ejecución con estas fuentes. | Se informa explícitamente. La selección por torneo es una extensión documentada, no una supuesta traducción de `vale`. |
| El límite de `m2h` compara con `np1` en lugar de `np2`. | Error latente en dominios de distinta longitud; queda oculto porque ambos tienen 61 nodos. | El experimento usa un n común y valida cada coordenada antes de evaluar. |
| Se reparan enteros inválidos, sin recodificar los cromosomas. | El genotipo puede dejar de representar el índice reparado si se añade un ciclo. | Reparación aleatoria uniforme seguida de recodificación. |
| `generaciones=120` se declara, pero no controla ningún bucle. | Solo se desarrolla un paso parcial de reproducción. | Bucle generacional con límite de evaluaciones explícito. |
| No se evalúa ni selecciona la población concatenada al terminar. | No hay conservación verificable de los mejores individuos ni convergencia. | Evaluación de hijos, reutilización de costos de padres y selección elitista de supervivientes. |
| Se reutilizan `mi1/mi2` para valores físicos al final. | Se mezclan índices y parámetros; una evolución añadida requeriría revisar todas las conversiones. | Índices 0..60, valores binarios 1..61 y coordenadas físicas se mantienen separados. |
| 10 bits por parámetro para 61 índices. | Mucha capacidad binaria no utilizada; los valores 0 y 62..1023 no son índices válidos. | La inicialización de reproducción conserva 10 bits; la versión moderna usa 6 por defecto y permite probar 10. |

La interpretación de `parejas=10` es diez individuos y cinco cruces, no diez pares. `dec2bin` genera caracteres y no bits numéricos: aplicar `~` a sus códigos de carácter no sustituye una inversión binaria correcta.

La reproducción completa del genético original permanece deliberadamente no ejecutable: `evolucion_genetica_original()` explica los componentes ausentes mediante `NotImplementedError`. No es una función pendiente del genético corregido, que sí está implementado y probado. No se inventa una evolución MATLAB que el archivo no contiene.

## Inversión polinomial de modelo27

```text
x = -10:0.1:10
G = [1, x, x², x³]
m_true = [500, 50, 5, 0.5]ᵀ
d = G m_true
E(m) = ||d - Gm||₂
```

Aunque el polinomio es cúbico en x, es **lineal en sus cuatro coeficientes**. Su costo es la norma L₂ del residuo, no su cuadrado y no la superficie E de dos parámetros.

El recorte de todos los coeficientes a `[-3,3]` excluye los valores verdaderos 500, 50 y 5. En x=0, el dato es 500 y cualquier modelo de esa caja produce un valor entre −3 y 3. Por tanto, el residuo total L₂ es al menos **497**; la tolerancia 1 resulta imposible en ese dominio. Esta es una cota inferior, no el mínimo de la caja. La amplitud 10 del primer coeficiente produce recortes frecuentes.

La comparación conserva una reproducción con la caja original. Añade dos referencias separadas:

1. Mínimos cuadrados con `np.linalg.lstsq(G,d,rcond=None)`. No se forman las ecuaciones normales ni se usa una inversa explícita.
2. Recocido escalado con `A_j=G_j/||G_j||₂`, `y=d/||d||₂` y `q_j=m_j||G_j||₂/||d||₂`. La nueva caja es `q∈[-2,2]⁴`; incluye la solución de este caso, sin usar `m_true` para proponer o aceptar. La amplitud, temperatura y presupuesto son nuevos, no una reproducción de MATLAB.

La norma normalizada es la norma original dividida por `||d||₂`. Esto conserva sus minimizadores sin restricciones, pero cambia la escala de temperaturas y tolerancias, además de la geometría de las propuestas. El historial escalado se convierte a unidades originales al graficarlo. El experimento usa presupuesto fijo, sin parada por tolerancia: su residuo final de aproximadamente 2.915 sigue siendo mayor que 1.

## Alcance de la recuperación

Se distinguen tres niveles: archivos MATLAB originales intactos, reproducciones de sus operaciones ejecutadas en Python y algoritmos corregidos/extensiones. Una misma semilla en NumPy y MATLAB no implica las mismas secuencias aleatorias ni igualdad de trayectorias. Los cambios propuestos no se aplicaron sobre los `.m`.

La superficie de prueba no contiene datos observados. El polinomio sí tiene un operador directo y un problema inverso, pero sus datos son sintéticos y no geofísicos. Ninguno de los experimentos valida una inversión sobre observaciones reales.
