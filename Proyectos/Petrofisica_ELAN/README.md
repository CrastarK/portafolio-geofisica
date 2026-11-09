# Petrofísica lineal: composición mineral y porosidad

**Autor: Edgar Lemuel Fuentes Solano · EDGAR LEMUEL / GEOPHYSICS**

Este proyecto ilustra la generación de respuestas sintéticas y la recuperación de cuatro fracciones volumétricas mediante un **modelo lineal petrofísico simplificado de inspiración ELAN**. Su objetivo es estudiar la relación entre composición, respuestas de registros y resolución numérica de un sistema lineal. Todos los escenarios son sintéticos: no se utilizan mediciones reales ni se valida un modelo comercial ELAN.

## Formulación: Ax = b

El vector de incógnitas es `x = [Vcal, Vdol, Vcuarzo, phi]ᵀ`: calcita, dolomita, cuarzo y porosidad, expresados como fracciones adimensionales. La cuarta ecuación impone el cierre volumétrico: `Vcal + Vdol + Vcuarzo + phi = 1`.

```text
    [  2.71    2.87    2.65    1.00 ]         [ rho  ]
A = [  0.00    0.02   -0.02    1.00 ]     b = [ phiN ]
    [156     143     180     620    ]         [ dt   ]
    [  1.00    1.00    1.00    1.00 ]         [ 1    ]
```

Las filas representan densidad `rho` en g/cm³, respuesta neutrónica `phiN` en fracción, tiempo de tránsito `dt` en µs/m y cierre volumétrico. Los coeficientes se conservan como parámetros del ejercicio; no constituyen una calibración de herramienta o formación. Para cada composición propuesta se calcula `b = A @ x_real` y después se resuelve el mismo sistema para recuperar `x`.

## Cuatro escenarios sintéticos

| Escenario | Calcita | Dolomita | Cuarzo | Porosidad |
|---|---:|---:|---:|---:|
| 1 · Predominio de calcita | 70 % | 10 % | 5 % | 15 % |
| 2 · Predominio de dolomita | 10 % | 70 % | 5 % | 15 % |
| 3 · Predominio de cuarzo | 10 % | 10 % | 65 % | 15 % |
| 4 · Alta porosidad | 35 % | 15 % | 10 % | 40 % |

Sus respuestas calculadas, redondeadas únicamente para esta tabla, son:

| Escenario | Densidad (g/cm³) | Neutrón (fracción) | Tiempo de tránsito (µs/m) |
|---|---:|---:|---:|
| 1 | 2.4665 | 0.151 | 225.50 |
| 2 | 2.5625 | 0.163 | 217.70 |
| 3 | 2.4305 | 0.139 | 239.90 |
| 4 | 2.0440 | 0.401 | 342.05 |

## Métodos, resultados y limitaciones

Se conservan dos procedimientos: solución directa con `np.linalg.solve(A, b)` e inversión explícita con `np.linalg.inv(A) @ b`. Ambos recuperan las cuatro composiciones con diferencias debidas al redondeo de punto flotante.

En la ejecución de entrega con NumPy 2.2.3, el máximo error absoluto frente a las fracciones propuestas fue `1.3322676295501878e-14` para `solve` y `8.548717289613705e-15` para la inversa. La diferencia máxima absoluta entre métodos fue `8.43769498715119e-15`. Son diferencias de fracción volumétrica, no porcentajes. Estos valores pueden variar en sus últimos dígitos entre plataformas y bibliotecas numéricas; no permiten concluir que un método sea superior a partir de este ejemplo.

La recuperación comprueba la consistencia algebraica de datos generados con la misma matriz. No demuestra capacidad predictiva ni estima incertidumbre física. No se incorporan ruido de medición, calibración, variaciones de propiedades, efectos ambientales, otros minerales o restricciones de positividad en la inversión. No hay validación con datos reales ni validación comercial ELAN.

## Reproducción local

Se necesitan Python, NumPy y Matplotlib. No es necesario modificar el entorno global. Desde la raíz del portafolio, con un entorno que ya contenga estas dependencias:

```powershell
python Proyectos/Petrofisica_ELAN/Petrofisica_ELAN.py
```

El programa imprime las composiciones y ambas soluciones, exporta las figuras de los dos temas y conserva `plt.show()` para abrir ocho ventanas con un backend interactivo. Las rutas de salida se resuelven respecto al archivo Python, independientemente del directorio desde el que se ejecute. Las ejecuciones posteriores regeneran los 16 archivos finales.

Para exportar sin ventanas en PowerShell, limitar el backend al proceso:

```powershell
python -c "import matplotlib, runpy; matplotlib.use('Agg'); runpy.run_path('Proyectos/Petrofisica_ELAN/Petrofisica_ELAN.py', run_name='__main__')"
```

Con Agg, `plt.show()` puede emitir un aviso de backend no interactivo después de exportar; esto no indica un fallo en los archivos.

## Figuras y temas

Cada figura conserva el encabezado `EDGAR LEMUEL / GEOPHYSICS` y el pie `Edgar Lemuel Fuentes Solano | Datos sintéticos`. Las curvas topográficas se limitan al margen superior, fuera de los datos.

| Archivo base | Contenido |
|---|---|
| `01_composicion_volumetrica` | Barras apiladas de las fracciones recuperadas con `solve`, en porcentaje; leyenda mineral y etiquetas internas. |
| `02_respuestas_sinteticas` | Tres paneles alineados con escalas y unidades independientes para densidad, neutrón y tiempo de tránsito. Las líneas unen escenarios discretos como guía visual. |
| `03_mapa_fracciones` | Mapa de calor de composición con escala fija de 0 a 100 %, barra de colores y anotaciones con contraste adaptativo. |
| `04_comparacion_numerica` | Diferencia `solve − inversa`, en fracción volumétrica; escala divergente simétrica centrada en cero, notación científica y explicación del redondeo. |

**Scientific Dark** usa fondo negro profundo, paneles grafito y colores minerales claros. **Scientific Light** usa fondo casi blanco, paneles gris claro y colores minerales más oscuros. Ambos mantienen contenido, posiciones, unidades, límites y anotaciones numéricas. El mapa porcentual conserva la misma escala de colores en ambos temas; el mapa de diferencias adapta su centro al fondo de cada tema. Los acentos son rojo mineral y la tipografía es DejaVu Sans.

```text
Figuras/
├── oscuro/                   # 4 PNG a 300 dpi + 4 SVG vectoriales
├── claro/                    # Los mismos 8 nombres y formatos
├── validacion.json           # Evidencia de la comprobación de entrega
└── archivo_previo.zip        # Exportaciones e informe anteriores, preservados
```

Las carpetas `oscuro/` y `claro/` contienen exactamente **16 archivos finales**. Los SVG conservan texto editable; para mantener su apariencia al abrirlos se recomienda disponer de DejaVu Sans. El módulo `helioforge_style.py` conserva su nombre de archivo por compatibilidad y ofrece `apply_theme("oscuro"/"claro")`, `palette`, `format_axis`, `decorate_figure`, `contrast_text` y `export_figure` para reutilizar el estilo personal.

## Comprobación de entrega

`Figuras/validacion.json` registra la igualdad exacta con los resultados anteriores, el bloque de cálculo sin cambios, las dos soluciones, las versiones de NumPy y Matplotlib, las 16 exportaciones y las comprobaciones de contraste y distribución. La ejecución de entrega verificó PNG a 300 dpi, SVG válidos, textos dentro del lienzo, ausencia de solapamientos y anotaciones idénticas entre temas. El contraste mínimo comprobado para texto fue 5.07:1 en oscuro y 5.14:1 en claro. Se revisaron también las imágenes generadas.

Las exportaciones anteriores se mantuvieron intactas hasta verificar las nuevas; después se preservaron en `archivo_previo.zip`. El informe documenta la entrega comprobada, no se actualiza automáticamente al ejecutar nuevamente el modelo. Estas comprobaciones validan la conservación numérica y la presentación del ejercicio, no un modelo petrofísico frente a mediciones reales.
