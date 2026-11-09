import argparse
import csv
import json
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import patheffects
from problemas import CARPETA

NOMBRES = {"local": "Búsqueda local", "recocido": "Recocido simulado", "genetico": "Genético binario"}
TEMAS = {
    "oscuro": dict(fondo="#0A0C0F", panel="#14191E", texto="#E7EBEF", secundario="#BDC5CE",
                   borde="#687683", acento="#D48383", colores=["#84C6C8", "#D8B979", "#B4A2D2"]),
    "claro": dict(fondo="#FAFBFC", panel="#F1F3F5", texto="#202830", secundario="#48545F",
                  borde="#78838C", acento="#8B1E2D", colores=["#1C626B", "#825C1D", "#6F4A8B"]),
}


def aplicar_tema(tema):
    estilo = TEMAS[tema]
    plt.rcParams.update({
        "font.family": "DejaVu Sans", "font.size": 10,
        "figure.facecolor": estilo["fondo"], "axes.facecolor": estilo["panel"],
        "text.color": estilo["texto"], "axes.labelcolor": estilo["texto"],
        "xtick.color": estilo["secundario"], "ytick.color": estilo["secundario"],
        "axes.edgecolor": estilo["borde"], "axes.linewidth": .6,
        "grid.color": estilo["borde"], "grid.alpha": .2, "grid.linewidth": .5,
        "legend.frameon": False, "legend.labelcolor": estilo["texto"],
        "svg.fonttype": "none", "figure.dpi": 120,
    })
    return estilo


def rotular(fig, numero, titulo, subtitulo, estilo):
    fig.text(.075, .945, "EDGAR LEMUEL / GEOPHYSICS", color=estilo["acento"], fontsize=9, weight="bold")
    fig.text(.075, .885, f"{numero:02d} / {titulo}", fontsize=18, weight="bold")
    fig.text(.075, .832, subtitulo, color=estilo["secundario"], fontsize=10)
    fig.text(.075, .025, "Edgar Lemuel Fuentes Solano | Experimentos numéricos sintéticos",
             color=estilo["secundario"], fontsize=9)


def exportar(fig, tema, nombre, salida=None):
    carpeta = (CARPETA / "Figuras" if salida is None else Path(salida)) / tema
    carpeta.mkdir(parents=True, exist_ok=True)
    for extension in ("png", "svg"):
        if (carpeta / f"{nombre}.{extension}").exists():
            raise FileExistsError("La figura ya existe; elige otra carpeta con --salida.")
        fig.savefig(carpeta / f"{nombre}.{extension}", dpi=300, bbox_inches="tight",
                    pad_inches=.22, facecolor=fig.get_facecolor())


def historial(metodo, semilla, carpeta=None):
    carpeta = CARPETA / "resultados" if carpeta is None else carpeta
    return np.genfromtxt(carpeta / "historiales" / f"{metodo}_{semilla}.csv",
                         delimiter=",", names=True)


def figura_superficie(superficies, resumen, estilo):
    fig = plt.figure(figsize=(12, 8))
    ax = fig.add_subplot(111, projection="3d")
    fig.subplots_adjust(left=.07, right=.85, bottom=.13, top=.77)
    rotular(fig, 1, "Superficie de costo compartida", "Función de prueba E(m₁, m₂) · No representa errores de observaciones geofísicas", estilo)
    superficie = ax.plot_surface(superficies["m1"], superficies["m2"], superficies["costo"],
                                cmap="cividis", rcount=61, ccount=61, linewidth=0, rasterized=False)
    referencia = resumen["referencia_malla_61"]
    ax.scatter(*referencia["modelo"], referencia["costo"], marker="*", s=100,
               c=estilo["acento"], edgecolors=estilo["texto"], linewidths=.7)
    ax.set(xlabel="m₁ (adimensional)", ylabel="m₂ (adimensional)", zlabel="Costo E")
    ax.view_init(elev=28, azim=-125)
    for eje in (ax.xaxis, ax.yaxis, ax.zaxis):
        eje.pane.set_facecolor(estilo["panel"])
        eje.pane.set_edgecolor(estilo["borde"])
        eje.line.set_color(estilo["borde"])
    cbar = fig.colorbar(superficie, ax=ax, shrink=.65, pad=.10, label="Costo E")
    cbar.solids.set_rasterized(False)
    fig.text(.075, .083, f"Estrella: menor costo enumerado en la malla 61 × 61: {referencia['costo']:.8f}.",
             color=estilo["secundario"], fontsize=9)
    return fig


def figura_trayectorias(superficies, resumen, estilo, carpeta=None):
    fig, ejes = plt.subplots(1, 3, figsize=(15, 7.5), sharex=True, sharey=True)
    fig.subplots_adjust(left=.075, right=.97, bottom=.21, top=.735, wspace=.18)
    rotular(fig, 2, "Contornos y trayectorias", "Semilla 42 · Estados actuales completos; el recocido puede aceptar aumentos de costo", estilo)
    for ax, (metodo, nombre), color in zip(ejes, NOMBRES.items(), estilo["colores"]):
        h = historial(metodo, 42, carpeta)
        ax.contour(superficies["m1"], superficies["m2"], superficies["costo"], levels=20,
                   colors=estilo["borde"], linewidths=.55, alpha=.55)
        linea, = ax.plot(h["actual_m1"], h["actual_m2"], color=color, lw=.8, alpha=.85)
        linea.set_path_effects([patheffects.withStroke(linewidth=1.8, foreground=estilo["panel"])])
        ax.scatter(h["actual_m1"][0], h["actual_m2"][0], c=color, marker="o", s=40,
                   edgecolors=estilo["texto"], zorder=5, label="Inicial")
        ax.scatter(h["mejor_m1"][-1], h["mejor_m2"][-1], c=color, marker="*", s=110,
                   edgecolors=estilo["texto"], zorder=6, label="Mejor conservado")
        ax.scatter(*resumen["referencia_malla_61"]["modelo"], marker="+", c=estilo["acento"], s=90,
                   zorder=7, label="Referencia de malla")
        ax.set(title=nombre, xlabel="m₁", xlim=(-3, 3), ylim=(-3, 3), aspect="equal")
    ejes[0].set_ylabel("m₂")
    handles, labels = ejes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", bbox_to_anchor=(.52, .088), ncol=3, fontsize=9)
    fig.text(.075, .065, "Genético: trayectoria del mejor superviviente por generación; no representa un desplazamiento físico.",
             color=estilo["secundario"], fontsize=9)
    return fig


def figura_convergencia(resumen, estilo, carpeta=None):
    fig, ejes = plt.subplots(1, 2, figsize=(14, 8))
    fig.subplots_adjust(left=.075, right=.97, bottom=.22, top=.735, wspace=.24)
    rotular(fig, 3, "Convergencia y esfuerzo numérico", "Diez semillas · Mediana y rango observado, sin interpretación como intervalo de confianza", estilo)
    presupuesto = resumen["presupuesto_por_algoritmo"]
    evaluaciones = np.unique(np.rint(np.geomspace(40, presupuesto, 200)).astype(int))
    for (metodo, nombre), color in zip(NOMBRES.items(), estilo["colores"]):
        curvas = []
        for semilla in resumen["semillas"]:
            h = historial(metodo, semilla, carpeta)
            indice = np.searchsorted(h["evaluaciones"], evaluaciones, side="right") - 1
            curvas.append(h["mejor_costo"][indice])
        curvas = np.array(curvas)
        ejes[0].fill_between(evaluaciones, curvas.min(axis=0), curvas.max(axis=0), color=color, alpha=.10)
        ejes[0].plot(evaluaciones, np.median(curvas, axis=0), c=color, lw=1.7, label=nombre)
        h = historial(metodo, 42, carpeta)
        ejes[1].plot(h["iteracion"], h["mejor_costo"], c=color, lw=1.5, label=nombre)
    for ax in ejes:
        ax.axhline(resumen["referencia_malla_61"]["costo"], c=estilo["acento"], ls="--", lw=1)
        ax.set_ylabel("Mejor costo conservado")
        ax.grid()
        ax.spines[["top", "right"]].set_visible(False)
    ejes[0].set(title="Comparación por evaluaciones", xlabel="Evaluaciones acumuladas", xscale="log")
    ejes[1].set(title="Contadores propios · semilla 42", xlabel="Barrido / nivel térmico / generación")
    ejes[0].legend(fontsize=9)
    fig.text(.075, .12, "Los contadores del panel derecho no tienen el mismo costo computacional. La comparación justa usa evaluaciones.",
             fontsize=9, color=estilo["secundario"])
    fig.text(.075, .08, "Línea discontinua: referencia exhaustiva de la malla 61 × 61. Todos los métodos conservan el mejor modelo.",
             fontsize=9, color=estilo["secundario"])
    return fig


def figura_comparacion(filas, resumen, estilo):
    fig, ejes = plt.subplots(1, 2, figsize=(13, 8))
    fig.subplots_adjust(left=.075, right=.97, bottom=.22, top=.735, wspace=.28)
    rotular(fig, 4, "Comparación de algoritmos", f"{resumen['presupuesto_por_algoritmo']:,} evaluaciones por ejecución · Diez semillas fijas · Dominio discreto compartido", estilo)
    for i, ((metodo, nombre), color) in enumerate(zip(NOMBRES.items(), estilo["colores"])):
        valores = [float(f["costo"]) for f in filas if f["metodo"] == metodo]
        ejes[0].scatter(np.linspace(i - .12, i + .12, len(valores)), valores, c=color, s=27, alpha=.8)
        ejes[0].plot([i - .24, i + .24], [np.median(valores)] * 2, c=color, lw=2.4)
        aciertos = resumen["resultados"][metodo]["aciertos_malla"]
        ejes[1].bar(i, aciertos, color=color, width=.55)
        ejes[1].text(i, aciertos + .25, f"{aciertos}/10", ha="center", fontsize=11)
    etiquetas = ["Local", "Recocido", "Genético"]
    ejes[0].set(ylabel="Mejor costo final", title="Puntos: ejecuciones · Trazo: mediana")
    ejes[0].axhline(resumen["referencia_malla_61"]["costo"], c=estilo["acento"], ls="--", lw=1)
    ejes[1].set(ylabel="Ejecuciones que alcanzan la referencia", ylim=(0, 11.3), title="Coincidencia con el mínimo de la malla")
    for ax in ejes:
        ax.set_xticks(range(3), etiquetas)
        ax.grid(axis="y")
        ax.set_axisbelow(True)
        ax.spines[["top", "right"]].set_visible(False)
    fig.text(.075, .12, "Acierto: diferencia de costo ≤ 10⁻¹² respecto a la referencia discreta. No prueba optimalidad global continua.",
             color=estilo["secundario"], fontsize=9)
    fig.text(.075, .08, "La búsqueda local y el recocido comparten inicio; el genético inicia con 40 individuos aleatorios, contados en el presupuesto.",
             color=estilo["secundario"], fontsize=9)
    return fig


def figura_polinomio(datos, resumen, estilo, carpeta=None):
    fig, ejes = plt.subplots(2, 2, figsize=(14, 10))
    fig.subplots_adjust(left=.075, right=.97, bottom=.14, top=.765, wspace=.25, hspace=.45)
    rotular(fig, 5, "Inversión polinomial sintética", "modelo27.m · Modelo lineal en los coeficientes · Datos sin ruido, sin observaciones geofísicas", estilo)
    x, g, d = datos["x"], datos["g"], datos["datos"]
    ax = ejes[0, 0]
    ax.plot(x, d, c=estilo["texto"], lw=2, label="Datos sintéticos")
    for nombre, etiqueta, color in zip(("minimos_cuadrados", "original", "escalado"),
                                      ("Mínimos cuadrados", "Caja original [-3,3]", "Recocido escalado"), estilo["colores"]):
        ax.plot(x, g @ datos[nombre], c=color, lw=1.2, ls="--" if nombre == "minimos_cuadrados" else "-", label=etiqueta)
        ejes[0, 1].plot(x, d - g @ datos[nombre], c=color, lw=1.1, label=etiqueta)
    ax.set(title="Datos y predicciones", xlabel="x (adimensional)", ylabel="d(x) (adimensional)")
    ax.legend(fontsize=8)
    ejes[0, 1].set(title="Residuos en unidades originales", xlabel="x", ylabel="d − Gm", yscale="symlog")
    for nombre, etiqueta, color in (("polinomio_limites_originales", "Caja original", estilo["colores"][1]),
                                    ("polinomio_escalado", "Variables escaladas", estilo["colores"][2])):
        raiz = CARPETA / "resultados" if carpeta is None else carpeta
        h = np.genfromtxt(raiz / "historiales" / f"{nombre}.csv", delimiter=",", names=True)
        valores = h["mejor_costo"] * (np.linalg.norm(d) if nombre.endswith("escalado") else 1)
        ejes[1, 0].plot(h["evaluaciones"], valores, c=color, label=etiqueta, lw=1.3)
    ejes[1, 0].axhline(1, c=estilo["acento"], ls="--", lw=.9, label="Tolerancia original: 1")
    ejes[1, 0].set(title="Mejor residuo conservado", xlabel="Evaluaciones", ylabel="Norma L₂ original", yscale="log")
    ejes[1, 0].legend(fontsize=8)
    tabla = [[f"m{i}"] + [f"{datos[n][i]:.6g}" for n in ("verdadero", "minimos_cuadrados", "original", "escalado")]
             for i in range(4)]
    ejes[1, 1].axis("off")
    ejes[1, 1].set_title("Coeficientes recuperados", loc="left", fontsize=11)
    objeto = ejes[1, 1].table(cellText=tabla, colLabels=["", "Verdadero", "LS", "Caja ±3", "SA escalado"],
                             loc="center", cellLoc="center", colWidths=[.11, .20, .20, .23, .26])
    objeto.auto_set_font_size(False)
    objeto.set_fontsize(9)
    objeto.scale(1, 1.7)
    for (fila, columna), celda in objeto.get_celld().items():
        celda.set_facecolor(estilo["panel"])
        celda.set_edgecolor(estilo["borde"])
        celda.get_text().set_color(estilo["texto"])
    for ax in ejes.flat:
        if ax.axison:
            ax.grid()
            ax.spines[["top", "right"]].set_visible(False)
    pol = resumen["polinomio"]
    fig.text(.075, .082, f"Residuos L₂: LS = {pol['error_ls']:.3e} | Caja original = {pol['error_original']:.3e} | SA escalado = {pol['error_escalado']:.3e}.",
             color=estilo["secundario"], fontsize=9)
    estado = "alcanza" if pol["error_escalado"] < 1 else "no alcanza"
    fig.text(.075, .055, f"El recocido escalado {estado} residuo < 1 en esta ejecución. LS es la referencia para este problema lineal sin ruido.",
             color=estilo["secundario"], fontsize=9)
    return fig


def generar_figuras(tema, resultados=None, salida=None, guardar=True):
    estilo = aplicar_tema(tema)
    carpeta = CARPETA / "resultados" if resultados is None else Path(resultados)
    resumen = json.loads((carpeta / "resumen.json").read_text(encoding="utf-8"))
    superficies = np.load(carpeta / "superficies.npz")
    with (carpeta / "comparacion.csv").open(encoding="utf-8") as archivo:
        filas = list(csv.DictReader(archivo))
    polinomio = np.load(carpeta / "polinomio.npz")
    figuras = [figura_superficie(superficies, resumen, estilo),
               figura_trayectorias(superficies, resumen, estilo, carpeta),
               figura_convergencia(resumen, estilo, carpeta), figura_comparacion(filas, resumen, estilo),
               figura_polinomio(polinomio, resumen, estilo, carpeta)]
    nombres = ["01_superficie_costo", "02_contornos_trayectorias", "03_convergencia",
               "04_comparacion_algoritmos", "05_inversion_polinomial"]
    if guardar:
        for fig, nombre in zip(figuras, nombres):
            exportar(fig, tema, nombre, salida)
    return figuras


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Figuras científicas del proyecto de métodos inversos.")
    parser.add_argument("--sin-mostrar", action="store_true")
    parser.add_argument("--resultados", type=Path, default=CARPETA / "resultados")
    parser.add_argument("--salida", type=Path, default=CARPETA / "Figuras")
    argumentos = parser.parse_args()
    if argumentos.sin_mostrar:
        plt.switch_backend("Agg")
    if any(argumentos.salida.rglob("*.png")) or any(argumentos.salida.rglob("*.svg")):
        parser.error("Ya hay figuras en la salida; usa --salida con una carpeta nueva.")
    for tema in ("oscuro", "claro"):
        generar_figuras(tema, argumentos.resultados, argumentos.salida)
    if argumentos.sin_mostrar:
        plt.close("all")
    else:
        plt.show()
