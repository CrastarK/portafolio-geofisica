from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt

from helioforge_style import (apply_theme, palette, format_axis, decorate_figure,
                              export_figure, contrast_text, volume_cmap, difference_cmap)
from matplotlib.colors import Normalize, TwoSlopeNorm
from matplotlib.ticker import ScalarFormatter

apply_theme()

# Modelo lineal simplificado de inspiración ELAN.
# x = [Vcal, Vdol, Vcuarzo, phi]
A = np.array([
    [2.71, 2.87, 2.65, 1.00],    # rho
    [0.00, 0.02, -0.02, 1.00],   # phiN
    [156, 143, 180, 620],        # Delta t
    [1.00, 1.00, 1.00, 1.00]     # suma
])

casos = {
    "Caso 1\nCalcita":   [0.70, 0.10, 0.05, 0.15],
    "Caso 2\nDolomita":  [0.10, 0.70, 0.05, 0.15],
    "Caso 3\nCuarzo":    [0.10, 0.10, 0.65, 0.15],
    "Caso 4\nPorosidad": [0.35, 0.15, 0.10, 0.40]
}

componentes = ["Calcita", "Dolomita", "Cuarzo", "Porosidad"]

colores = list(palette().values())

volumenes_metodo1 = []
volumenes_metodo2 = []
registros = []

print("Modelo lineal simplificado de inspiración ELAN: 4 casos / 2 métodos\n")

for nombre, valores in casos.items():
    x_real = np.array(valores, dtype=float)

    if abs(x_real.sum() - 1.0) > 1e-6:
        print(f"⚠️ {nombre}: los volúmenes no suman 1")
        print(f"Suma = {x_real.sum():.4f}\n")

    b = A @ x_real

    rho = b[0]
    phiN = b[1]
    dt = b[2]

    registros.append(b[:3])

    x_m1 = np.linalg.solve(A, b)

    A_inv = np.linalg.inv(A)
    x_m2 = A_inv @ b

    volumenes_metodo1.append(x_m1)
    volumenes_metodo2.append(x_m2)

    print(nombre.replace(chr(10), " "))

    print("\nDatos propuestos:")
    print(f"Vcal     = {x_real[0]:.4f} = {x_real[0]*100:.2f}%")
    print(f"Vdol     = {x_real[1]:.4f} = {x_real[1]*100:.2f}%")
    print(f"Vcuarzo  = {x_real[2]:.4f} = {x_real[2]*100:.2f}%")
    print(f"phi      = {x_real[3]:.4f} = {x_real[3]*100:.2f}%")

    print("\nRegistros calculados:")
    print(f"rho      = {rho:.4f}")
    print(f"phiN     = {phiN:.4f}")
    print(f"dt       = {dt:.4f}")

    print("\nMétodo 1: np.linalg.solve(A,b)")
    print(f"Vcal     = {x_m1[0]:.4f} = {x_m1[0]*100:.2f}%")
    print(f"Vdol     = {x_m1[1]:.4f} = {x_m1[1]*100:.2f}%")
    print(f"Vcuarzo  = {x_m1[2]:.4f} = {x_m1[2]*100:.2f}%")
    print(f"phi      = {x_m1[3]:.4f} = {x_m1[3]*100:.2f}%")
    print(f"Suma     = {x_m1.sum():.4f}")

    print("\nMétodo 2: inversa A^-1 b")
    print(f"Vcal     = {x_m2[0]:.4f} = {x_m2[0]*100:.2f}%")
    print(f"Vdol     = {x_m2[1]:.4f} = {x_m2[1]*100:.2f}%")
    print(f"Vcuarzo  = {x_m2[2]:.4f} = {x_m2[2]*100:.2f}%")
    print(f"phi      = {x_m2[3]:.4f} = {x_m2[3]*100:.2f}%")
    print(f"Suma     = {x_m2.sum():.4f}")

    diferencia = x_m1 - x_m2

    print("\nDiferencia Método 1 - Método 2:")
    print(f"dVcal    = {diferencia[0]:.2e}")
    print(f"dVdol    = {diferencia[1]:.2e}")
    print(f"dVcuarzo = {diferencia[2]:.2e}")
    print(f"dphi     = {diferencia[3]:.2e}")
    print()

volumenes_metodo1 = np.array(volumenes_metodo1)
volumenes_metodo2 = np.array(volumenes_metodo2)
registros = np.array(registros)

nombres_casos = list(casos.keys())
x = np.arange(len(nombres_casos))

# Para las gráficas usamos el Método 1
volumenes = volumenes_metodo1


def generar_figuras(tema):
    estilo = apply_theme(tema)
    colores = list(palette(tema).values())
    carpeta_figuras = Path(__file__).resolve().parent / "Figuras" / tema

    # Composición recuperada con solve.
    fig, ax = plt.subplots(figsize=(11, 7))
    fig.subplots_adjust(left=.10, right=.97, bottom=.25, top=.77)
    decorate_figure(fig, "01 / COMPOSICIÓN VOLUMÉTRICA", "Fracciones recuperadas · solución directa Ax = b")
    bottom = np.zeros(len(casos))
    for i, comp in enumerate(componentes):
        valores = volumenes_metodo1[:, i] * 100
        ax.bar(x, valores, bottom=bottom, color=colores[i], width=.62,
               edgecolor=estilo["panel"], linewidth=1, label=comp)
        for j, v in enumerate(valores):
            ax.text(j, bottom[j] + v / 2, f"{v:.0f}%", ha="center", va="center",
                    color=contrast_text(colores[i]), fontsize=10, fontweight="bold")
        bottom += valores
    format_axis(ax)
    ax.set(ylabel="Fracción volumétrica (%)", ylim=(0, 100), xticks=x,
           xticklabels=nombres_casos)
    ax.legend(loc="upper center", bbox_to_anchor=(.5, -.19), ncol=4)
    export_figure(fig, carpeta_figuras, "01_composicion_volumetrica")

    # Registros en escalas independientes.
    fig, axes = plt.subplots(3, 1, figsize=(11, 9), sharex=True)
    fig.subplots_adjust(left=.13, right=.94, bottom=.14, top=.76, hspace=.50)
    decorate_figure(fig, "02 / RESPUESTAS SINTÉTICAS", "Modelo lineal petrofísico simplificado de inspiración ELAN · b = Ax")
    respuestas = [
        ("Densidad", r"$\rho$ (g/cm³)", colores[0], 4),
        ("Neutrón", r"$\phi_N$ (fracción)", colores[1], 3),
        ("Tiempo de tránsito", r"$\Delta t$ (µs/m)", colores[3], 2),
    ]
    for i, (titulo, unidad, color, decimales) in enumerate(respuestas):
        ax = axes[i]
        format_axis(ax)
        ax.plot(x, registros[:, i], color=color, marker="o", markersize=6, linewidth=1.6)
        ax.set_ylabel(unidad)
        ax.set_title(titulo, loc="left", fontsize=11, pad=9)
        ax.margins(x=.10, y=.45)
        for j, valor in enumerate(registros[:, i]):
            ax.annotate(f"{valor:.{decimales}f}", (j, valor), xytext=(0, 9),
                        textcoords="offset points", ha="center", fontsize=9)
    axes[-1].set_xticks(x, nombres_casos)
    export_figure(fig, carpeta_figuras, "02_respuestas_sinteticas")

    # Fracciones en una escala fija de 0 a 100 %.
    fig, ax = plt.subplots(figsize=(11, 7))
    fig.subplots_adjust(left=.14, right=.88, bottom=.19, top=.77)
    decorate_figure(fig, "03 / MATRIZ DE FRACCIONES", "Composición volumétrica recuperada · solución directa")
    cmap = volume_cmap()
    norm = Normalize(vmin=0, vmax=100)
    im = ax.pcolormesh(np.arange(len(casos) + 1) - .5,
                       np.arange(len(componentes) + 1) - .5, volumenes.T * 100,
                       shading="flat", cmap=cmap, norm=norm, rasterized=False)
    ax.set_ylim(len(componentes) - .5, -.5)
    ax.set(xticks=x, xticklabels=nombres_casos, yticks=np.arange(4), yticklabels=componentes)
    format_axis(ax, grid=False)
    for i in range(4):
        for j in range(len(casos)):
            valor = volumenes[j, i] * 100
            ax.text(j, i, f"{valor:.0f}%", ha="center", va="center", fontweight="bold",
                    color=contrast_text(cmap(norm(valor))))
    cbar = fig.colorbar(im, ax=ax, pad=.035, fraction=.045, label="Fracción volumétrica (%)")
    cbar.solids.set_rasterized(False)
    export_figure(fig, carpeta_figuras, "03_mapa_fracciones")

    # Diferencias de redondeo entre métodos.
    diferencias = volumenes_metodo1 - volumenes_metodo2
    fig, ax = plt.subplots(figsize=(11, 7.5))
    fig.subplots_adjust(left=.14, right=.88, bottom=.32, top=.77)
    decorate_figure(fig, "04 / COMPARACIÓN NUMÉRICA", "np.linalg.solve(A, b) − np.linalg.inv(A) @ b")
    limite = max(float(np.max(np.abs(diferencias))), np.finfo(float).eps)
    norm = TwoSlopeNorm(vmin=-limite, vcenter=0, vmax=limite)
    cmap = difference_cmap(tema)
    im = ax.pcolormesh(np.arange(len(casos) + 1) - .5,
                       np.arange(len(componentes) + 1) - .5, diferencias.T,
                       shading="flat", cmap=cmap, norm=norm, rasterized=False)
    ax.set_ylim(len(componentes) - .5, -.5)
    format_axis(ax, grid=False)
    ax.set(xticks=x, xticklabels=nombres_casos, yticks=np.arange(4), yticklabels=componentes)
    for i in range(4):
        for j in range(len(casos)):
            valor = diferencias[j, i]
            ax.text(j, i, f"{valor:.2e}", ha="center", va="center", fontsize=10,
                    color=contrast_text(cmap(norm(valor))))
    cbar = fig.colorbar(im, ax=ax, pad=.035, fraction=.045)
    cbar.solids.set_rasterized(False)
    formatter = ScalarFormatter(useMathText=True)
    formatter.set_powerlimits((0, 0))
    cbar.formatter = formatter
    cbar.update_ticks()
    cbar.set_label("Diferencia de fracción volumétrica")
    fig.text(.14, .15,
             f"Máximo |Δ| = {np.max(np.abs(diferencias)):.2e} · magnitudes del orden de 10⁻¹⁵ o menores.\n"
             "Diferencias compatibles con redondeo en aritmética de punto flotante;\n"
             "no representan incertidumbre física ni validación de un modelo comercial ELAN.",
             fontsize=10, color=estilo["muted"], linespacing=1.6)
    export_figure(fig, carpeta_figuras, "04_comparacion_numerica")


for tema in ("oscuro", "claro"):
    generar_figuras(tema)

plt.show()
