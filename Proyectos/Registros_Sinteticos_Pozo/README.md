# Registros sintéticos de pozo

**Edgar Lemuel Fuentes Solano · EDGAR LEMUEL / GEOPHYSICS**

Dataset propio y reproducible para explorar respuestas de registros geofísicos y producir figuras científicas para un portafolio. Contiene **1 201 muestras entre 1 000 y 1 300 m**, con paso de **0.25 m**, siete curvas y cuatro variables de referencia.

Todos los valores se generan matemáticamente. No se utiliza el Excel privado, archivos de otros proyectos, registros de campo ni datasets externos. El proyecto está preparado para compartir su código y sus datos sintéticos; todavía no se ha publicado.

## Objetivo y alcance

Representar cambios cualitativamente plausibles entre lutita, arena limpia, arena porosa, una arena con respuesta tipo hidrocarburo impuesta y un intervalo compacto. Las curvas comparten propiedades latentes, transiciones suaves y variabilidad correlacionada en profundidad. Esto produce asociaciones coherentes dentro del modelo, sin afirmar que reproduzcan una formación o herramienta reales.

La zona HC es un escenario diseñado, no un descubrimiento ni una interpretación obtenida del dataset. La porosidad, arcillosidad, saturación y facies de referencia son conocidas porque fueron impuestas por el generador.

## Archivos

```text
Registros_Sinteticos_Pozo/
├── generar_datos.py
├── visualizar_registros.py
├── validar_proyecto.py
├── README.md
├── datos/
│   ├── pozo_sintetico.csv
│   └── metadatos.json
├── Figuras/
│   ├── oscuro/
│   │   ├── 01_registros_pozo.png
│   │   ├── 01_registros_pozo.svg
│   │   ├── 02_relaciones_petrofisicas.png
│   │   └── 02_relaciones_petrofisicas.svg
│   └── claro/
│       └── Los mismos cuatro nombres y formatos
└── validacion.json
```

## Variables del CSV

El archivo usa coma como separador, punto decimal, encabezado y codificación UTF-8. No tiene índice de filas adicional. Los valores se guardan con seis decimales, salvo profundidad con dos y código de facies entero.

| Variable | Unidad | Significado en esta simulación |
|---|---|---|
| DEPTH | m | Profundidad medida a lo largo de un pozo idealizado, sin trayectoria desviada. |
| GR | API | Respuesta gamma sintética asociada al índice de arcillosidad. |
| SP | mV | Potencial espontáneo idealizado, referido a una línea base arbitraria. |
| CALI | in | Diámetro de pozo simulado; barrena de referencia de 8.5 in. |
| RHOB | g/cm³ | Densidad volumétrica obtenida de una mezcla simplificada de matriz y fluido. |
| NPHI | fracción | Respuesta neutrónica aparente sintética; no porosidad efectiva medida. |
| DT | µs/ft | Tiempo de tránsito compresional idealizado. **No está en µs/m**. |
| RT | Ω·m | Resistividad sintética de formación; no lectura de una herramienta LLD específica. |
| VSH_TRUE | fracción | Índice impuesto de arcillosidad, usado como peso de mezcla en la matriz. |
| PHI_TRUE | fracción | Porosidad impuesta por el generador. |
| SW_TRUE | fracción | Saturación de agua impuesta en el espacio poroso. |
| LITH_CODE | categoría | Etiqueta impuesta del intervalo, no clasificación inferida de los registros. |

Las variables `*_TRUE` y `LITH_CODE` son referencias de simulación. No deben tratarse como registros independientes ni usarse inadvertidamente como predictores si se plantea un ejercicio de estimación de esas mismas propiedades.

## Intervalos y supuestos

Los parámetros de esta tabla son valores base elegidos para el ejercicio. Después se añaden transiciones y heterogeneidad; por eso no equivalen a las medias exactas del CSV.

| Profundidad (m) | Código | Escenario | VSH base | PHI base | SW base |
|---|---:|---|---:|---:|---:|
| 1000–1060 | 1 | Lutita | 0.78 | 0.10 | 1.00 |
| 1060–1115 | 2 | Arena limpia | 0.04 | 0.16 | 1.00 |
| 1115–1170 | 3 | Arena porosa | 0.08 | 0.28 | 1.00 |
| 1170–1210 | 4 | Respuesta HC simulada | 0.02 | 0.24 | 0.25 |
| 1210–1260 | 5 | Intervalo compacto | 0.06 | 0.065 | 1.00 |
| 1260–1300 | 1 | Lutita | 0.70 | 0.12 | 1.00 |

Los intervalos incluyen su techo y excluyen su base; el último incluye 1300 m. Las etiquetas son abruptas, mientras que las propiedades se mezclan suavemente alrededor de los contactos. Los puntos de transición pueden tener respuestas intermedias aunque su etiqueta pertenezca a uno de los intervalos.

## Metodología

Se utiliza `np.random.default_rng(42)`. La semilla y la versión de NumPy quedan registradas en `datos/metadatos.json`.

1. Crear una malla regular de profundidad y pesos entre intervalos mediante transiciones de tangente hiperbólica, con parámetro de escala de 0.65 m.
2. Mezclar los valores base de arcillosidad, porosidad y saturación. Incorporar heterogeneidad mediante ruido normal suavizado con kernels gaussianos. Las escalas principales son 5 y 1.5 muestras, equivalentes a 1.25 y 0.375 m; son parámetros de suavizado, no longitudes de correlación estimadas de campo.
3. Limitar las referencias impuestas a `0.005 ≤ VSH ≤ 0.95`, `0.035 ≤ PHI ≤ 0.36` y `0.15 ≤ SW ≤ 1`. Estos límites pertenecen al generador, no son criterios universales de interpretación.
4. Calcular las respuestas con las relaciones siguientes y añadir pequeñas perturbaciones de cada curva.

Con `v = VSH_TRUE`, `phi = PHI_TRUE`, `sw = SW_TRUE` y `z = DEPTH`:

```text
rho_matriz = 2.65 (1 - v) + 2.72 v
rho_fluido = 1.05 sw + 0.25 (1 - sw)
RHOB = (1 - phi) rho_matriz + phi rho_fluido + ruido

NPHI = phi [sw + 0.25 (1 - sw)] + 0.25 v + ruido
GR = 20 + 130 v + ruido
SP = -65 (1 - v) min(phi / 0.24, 1) + 4 (z - 1000) / 300 + ruido

dt_matriz = 55.5 (1 - v) + 75 v
dt_fluido = 189 sw + 310 (1 - sw)
DT = (1 - phi) dt_matriz + phi dt_fluido + ruido

RT_arena = 0.08 / (phi² sw²)
RT = 1 / [(1 - v) / RT_arena + v / 2]
RT_final = RT exp(ruido_correlacionado × 0.06)
```

Los valores de densidad están en g/cm³ y los de tiempo en µs/ft. La densidad de fluido de 0.25 y el menor factor neutrónico del componente no acuoso son elecciones para crear una respuesta tipo gas. El tiempo de tránsito usa un promedio temporal didáctico; no resuelve la propagación de ondas en un medio poroso.

La resistividad parte de una relación tipo Archie con `a = 1`, `Rw = 0.08 Ω·m`, `m = 2` y `n = 2`, y añade una conducción arcillosa en paralelo con `Rsh = 2 Ω·m`. Esta mezcla es una aproximación propia del ejercicio, sin calibración de una formación. La perturbación multiplicativa mantiene RT positiva.

`CALI = 8.5 + 0.95 v + ruido`, con dos ensanchamientos gaussianos centrados en 1028 y 1282 m. Sus amplitudes son 0.8 y 0.65 in y sus escalas son 4 y 5 m. El ruido representa textura y variabilidad instrumental idealizadas, no incertidumbre cuantificada. Los coeficientes completos y las amplitudes se encuentran en `generar_datos.py`.

## Figuras

**01 · Registros en profundidad.** Columna de facies y siete pistas alineadas. La profundidad aumenta hacia abajo; NPHI aumenta hacia la izquierda; RT usa escala logarítmica. CALI incluye una referencia de barrena de 8.5 in. RHOB y NPHI se muestran en pistas separadas para conservar sus unidades y evitar una superposición que sugiera calibración comercial.

**02 · Relaciones petrofísicas.** Densidad frente a respuesta neutrónica, porosidad impuesta frente a resistividad y porosidad impuesta frente a tiempo de tránsito. Se representan las 1 201 muestras en cada panel, coloreadas por facies impuesta. Los contactos suavizados explican los puntos intermedios entre agrupaciones.

Ambas figuras se exportan en tema oscuro y claro, con DejaVu Sans, paneles discretos y atribución personal. Hay **cuatro PNG a 300 dpi y cuatro SVG vectoriales**, sin imágenes raster incrustadas en los SVG. El tema claro oscurece los colores de los puntos para mejorar su contraste. Los SVG conservan texto editable y requieren DejaVu Sans para mantener la misma apariencia en otro equipo.

## Reproducción

Se necesitan Python, NumPy y Matplotlib. La validación utiliza también Pillow, dependencia de Matplotlib ya disponible en el entorno de entrega. No se necesita Excel, pandas, conexión a internet ni acceso a otro proyecto.

Desde la raíz del portafolio, con un entorno que ya tenga estas dependencias:

```powershell
python Proyectos/Registros_Sinteticos_Pozo/generar_datos.py
python Proyectos/Registros_Sinteticos_Pozo/visualizar_registros.py
python Proyectos/Registros_Sinteticos_Pozo/validar_proyecto.py
```

Las rutas de salida se resuelven respecto a los scripts. También se pueden ejecutar desde otra carpeta usando su ruta completa. No modifican el entorno Python global.

Para exportar sin abrir ventanas:

```powershell
python Proyectos/Registros_Sinteticos_Pozo/visualizar_registros.py --sin-mostrar
```

El argumento `--tema oscuro` o `--tema claro` exporta solo una variante; por defecto se generan ambas. Sin `--sin-mostrar`, se conserva `plt.show()` para uso local con un backend interactivo. Para un equipo sin pantalla, el proceso puede ejecutarse con backend Agg:

```powershell
python -c "import matplotlib, runpy, sys; matplotlib.use('Agg'); sys.argv=['visualizar_registros.py','--sin-mostrar']; runpy.run_path('Proyectos/Registros_Sinteticos_Pozo/visualizar_registros.py', run_name='__main__')"
```

Para explorar otra realización, `generar_datos.py --semilla 43` regenera el CSV y sus metadatos en las mismas rutas. Luego deben ejecutarse visualización y validación para actualizar todas las salidas. `--semilla 42` restaura la realización de entrega. Las ejecuciones sobrescriben únicamente las salidas de este proyecto.

## Comprobaciones

`validar_proyecto.py` comprueba el esquema del CSV, 1 201 muestras, profundidad regular, ausencia de nulos, valores finitos, RT positiva, referencias acotadas, códigos de intervalo y reproducibilidad con la misma semilla. También verifica que cambiar la semilla cambia la realización, y contrasta el CSV con el generador considerando el redondeo a seis decimales.

La revisión verifica las respuestas relativas diseñadas: GR y CALI mayores en lutita que en arena limpia, porosidad mayor en arena porosa, respuesta neutrónica reducida en la zona HC y RT elevada tanto en la zona HC como en el intervalo compacto respecto a la arena porosa. Estos controles comprueban el diseño, no validan una interpretación geológica.

Se revisan las ocho exportaciones, la resolución PNG, la ausencia de raster incrustado en SVG, los márgenes de texto, los solapamientos, la presencia de todos los datos en las figuras y el contraste de texto y curvas. Los resultados y los rangos efectivamente generados quedan en `validacion.json`. En la entrega se utilizaron NumPy 2.2.3 y Matplotlib 3.10.1.

## Limitaciones

- No existe un pozo real asociado, ubicación, campaña, fecha de adquisición o herramienta de registro.
- No se modelan invasión, salinidad variable, temperatura, anisotropía, trayectorias, resolución radial ni acoplamiento completo entre pozo y herramientas.
- La respuesta de lutita y el promedio sónico son simplificaciones; no sustituyen modelos petrofísicos calibrados.
- Los perfiles contienen textura y ruido diseñados, sin reproducir una distribución estadística demostrada con datos de campo. Las ecuaciones simples producen agrupaciones más separadas que muchas situaciones reales.
- Una RT elevada no identifica por sí sola hidrocarburos. El intervalo compacto ilustra esa ambigüedad; SP y NPHI también dependen de supuestos impuestos.
- No se estima incertidumbre ni se demuestra rendimiento de un algoritmo de interpretación o clasificación. Las etiquetas son información del simulador.

## Contexto técnico público

Se consultaron únicamente descripciones generales de métodos, sin descargar datos. El [USGS resume el uso de gamma, caliper y potencial espontáneo](https://www.usgs.gov/centers/new-york-water-science-center/science/borehole-geophysics), y la [EPA describe la relación entre resistividad, porosidad y agua de formación](https://www.epa.gov/environmental-geophysics/borehole-resistivity). Estas fuentes aportan contexto; no avalan los coeficientes, intervalos ni resultados particulares de esta simulación.
