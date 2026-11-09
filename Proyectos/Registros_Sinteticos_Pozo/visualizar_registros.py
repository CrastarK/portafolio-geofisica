from pathlib import Path
import argparse
import json
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.ticker import MultipleLocator, LogLocator, NullFormatter

CARPETA = Path(__file__).resolve().parent
FACIES = {
    1: ("Lutita", "#A797B7"), 2: ("Arena limpia", "#D5BC7D"),
    3: ("Arena porosa", "#78B8B0"), 4: ("Respuesta HC simulada", "#D48383"),
    5: ("Intervalo compacto", "#85A8C8"),
}
FACIES_CLARAS = {1: "#735982", 2: "#846722", 3: "#246F68", 4: "#9A3444", 5: "#35658B"}
TEMAS = {
    "oscuro": dict(fondo="#0A0C0F", panel="#14191E", texto="#E7EBEF", secundario="#BDC5CE",
                   rejilla="#52616E", curva="#91CDD0", acento="#D48383", borde="#77838C"),
    "claro": dict(fondo="#FAFBFC", panel="#F1F3F5", texto="#202830", secundario="#48545F",
                  rejilla="#BAC3CA", curva="#225D67", acento="#8B1E2D", borde="#78838C"),
}


def aplicar_tema(tema):
    estilo = TEMAS[tema]
    plt.rcParams.update({
        "font.family": "DejaVu Sans", "font.size": 10,
        "figure.facecolor": estilo["fondo"], "axes.facecolor": estilo["panel"],
        "text.color": estilo["texto"], "axes.labelcolor": estilo["texto"],
        "xtick.color": estilo["secundario"], "ytick.color": estilo["secundario"],
        "axes.edgecolor": estilo["borde"], "axes.linewidth": .6,
        "grid.color": estilo["rejilla"], "grid.alpha": .28, "grid.linewidth": .45,
        "legend.frameon": False, "legend.labelcolor": estilo["texto"],
        "svg.fonttype": "none", "figure.dpi": 120, "savefig.dpi": 300,
    })
    return estilo


def rotular(fig, titulo, subtitulo, estilo, semilla):
    fig.text(.065, .958, "EDGAR LEMUEL / GEOPHYSICS", fontsize=10, weight="bold", color=estilo["acento"])
    fig.text(.065, .913, titulo, fontsize=21, weight="bold")
    fig.text(.065, .872, subtitulo, fontsize=10, color=estilo["secundario"])
    fig.text(.065, .023, f"Edgar Lemuel Fuentes Solano | Datos 100 % sintéticos | Semilla {semilla}",
             fontsize=9, color=estilo["secundario"])


def exportar(fig, tema, nombre):
    carpeta = CARPETA / "Figuras" / tema
    carpeta.mkdir(parents=True, exist_ok=True)
    for extension in ("png", "svg"):
        fig.savefig(carpeta / f"{nombre}.{extension}", dpi=300, bbox_inches="tight",
                    pad_inches=.22, facecolor=fig.get_facecolor())


def validar_datos(datos):
    requeridas = ("DEPTH", "GR", "SP", "CALI", "RHOB", "NPHI", "DT", "RT",
                  "VSH_TRUE", "PHI_TRUE", "SW_TRUE", "LITH_CODE")
    if datos.dtype.names != requeridas or datos.size < 2:
        raise ValueError("El CSV no tiene las columnas o las muestras esperadas.")
    if not all(np.isfinite(datos[nombre]).all() for nombre in requeridas):
        raise ValueError("Hay valores ausentes o no finitos.")
    if not np.all(np.diff(datos["DEPTH"]) > 0) or np.any(datos["RT"] <= 0):
        raise ValueError("La profundidad debe crecer y RT debe ser positiva.")
    if not np.isin(datos["LITH_CODE"], list(FACIES)).all():
        raise ValueError("Código de facies desconocido.")


def figura_registros(datos, metadatos, tema):
    estilo = aplicar_tema(tema)
    fig, ejes = plt.subplots(1, 8, figsize=(18, 11), sharey=True,
                             gridspec_kw={"width_ratios": [.48, 1, 1, 1, 1, 1, 1, 1]})
    fig.subplots_adjust(left=.065, right=.975, bottom=.135, top=.775, wspace=.17)
    rotular(fig, "Registros geofísicos de un pozo sintético",
            "1 000–1 300 m · Muestreo 0.25 m · Facies impuestas y respuestas idealizadas", estilo, metadatos["semilla"])
    profundidad = datos["DEPTH"]
    ejes[0].set(xlim=(0, 1), ylabel="Profundidad (m)")
    ejes[0].set_xticks([])
    ejes[0].set_title("Facies", fontsize=9, pad=12)
    for intervalo in metadatos["intervalos"]:
        techo, base, codigo = intervalo["techo_m"], intervalo["base_m"], intervalo["codigo"]
        color = FACIES[codigo][1]
        ejes[0].axhspan(techo, base, color=color, linewidth=0)
        nombre = "HC simulado" if codigo == 4 else FACIES[codigo][0]
        ejes[0].text(.5, (techo + base) / 2, nombre, rotation=90, ha="center", va="center",
                     color="#0A0C0F", fontsize=8)
    curvas = [
        ("GR", "API", (0, 160)), ("SP", "mV", (-90, 20)),
        ("CALI", "in", (8, 11)), ("RHOB", "g/cm³", (1.85, 2.85)),
        ("NPHI", "fracción", (.45, -.05)), ("DT", "µs/ft", (50, 130)),
        ("RT", "Ω·m", (.2, 200)),
    ]
    for ax, (nombre, unidad, limites) in zip(ejes[1:], curvas):
        ax.plot(datos[nombre], profundidad, color=estilo["curva"], lw=.9)
        ax.set_xlim(*limites)
        ax.set_xlabel(f"{nombre}\n({unidad})", labelpad=10, weight="bold")
        ax.xaxis.tick_top()
        ax.xaxis.set_label_position("top")
        ax.tick_params(axis="x", labelsize=8, width=.6)
        ax.tick_params(axis="y", left=False, labelleft=False)
        ax.grid(which="major")
        if nombre == "RT":
            ax.set_xscale("log")
            ax.xaxis.set_major_locator(LogLocator(base=10, numticks=4))
            ax.xaxis.set_minor_formatter(NullFormatter())
        for intervalo in metadatos["intervalos"][1:]:
            ax.axhline(intervalo["techo_m"], color=estilo["borde"], lw=.5, alpha=.55)
    ejes[3].axvline(8.5, color=estilo["acento"], ls="--", lw=1, label="Barrena 8.5 in")
    ejes[3].legend(loc="lower right", fontsize=7, borderaxespad=.2)
    ejes[0].set_ylim(profundidad[-1], profundidad[0])
    ejes[0].yaxis.set_major_locator(MultipleLocator(50))
    ejes[0].yaxis.set_minor_locator(MultipleLocator(10))
    fig.text(.065, .079, "NPHI aumenta hacia la izquierda. RT usa escala logarítmica. DT se expresa en µs/ft.",
             fontsize=9, color=estilo["secundario"])
    fig.text(.065, .052, "La respuesta HC fue impuesta: una resistividad alta también puede aparecer en el intervalo compacto.",
             fontsize=9, color=estilo["secundario"])
    exportar(fig, tema, "01_registros_pozo")
    return fig


def figura_relaciones(datos, metadatos, tema):
    estilo = aplicar_tema(tema)
    fig, ejes = plt.subplots(1, 3, figsize=(16, 8))
    fig.subplots_adjust(left=.065, right=.975, bottom=.25, top=.76, wspace=.30)
    rotular(fig, "Relaciones petrofísicas sintéticas",
            "Todos los puntos del CSV · Las asociaciones proceden de las ecuaciones del generador", estilo, metadatos["semilla"])
    relaciones = [
        ("RHOB", "NPHI", "Densidad (g/cm³)", "Neutrón (fracción)", "Densidad y respuesta neutrónica"),
        ("PHI_TRUE", "RT", "Porosidad impuesta (fracción)", "Resistividad (Ω·m)", "Porosidad y resistividad"),
        ("PHI_TRUE", "DT", "Porosidad impuesta (fracción)", "Tiempo de tránsito (µs/ft)", "Porosidad y tiempo de tránsito"),
    ]
    facies = {codigo: (nombre, FACIES_CLARAS[codigo] if tema == "claro" else color)
              for codigo, (nombre, color) in FACIES.items()}
    for ax, (x, y, etiqueta_x, etiqueta_y, titulo) in zip(ejes, relaciones):
        for codigo, (nombre, color) in facies.items():
            mascara = datos["LITH_CODE"] == codigo
            ax.scatter(datos[x][mascara], datos[y][mascara], s=10, c=color, alpha=.8,
                       linewidths=.35, edgecolors="#26313A", rasterized=False)
        ax.set(xlabel=etiqueta_x, ylabel=etiqueta_y)
        ax.set_title(titulo, loc="left", fontsize=10, weight="bold", pad=12)
        ax.grid(alpha=.22)
        ax.set_axisbelow(True)
        ax.spines[["top", "right"]].set_visible(False)
    ejes[1].set_yscale("log")
    leyenda = [Patch(facecolor=color, edgecolor="#26313A", label=nombre) for nombre, color in facies.values()]
    fig.legend(handles=leyenda, loc="lower center", bbox_to_anchor=(.52, .105), ncol=5,
               title="Facies impuestas en el modelo", fontsize=9, title_fontsize=9)
    fig.text(.065, .065, "Las variables *_TRUE son referencias del generador, no estimaciones a partir de registros.",
             color=estilo["secundario"], fontsize=9)
    exportar(fig, tema, "02_relaciones_petrofisicas")
    return fig


def main():
    parser = argparse.ArgumentParser(description="Visualizar exclusivamente el CSV sintético de este proyecto.")
    parser.add_argument("--tema", choices=("ambos", "oscuro", "claro"), default="ambos")
    parser.add_argument("--sin-mostrar", action="store_true")
    argumentos = parser.parse_args()
    ruta = CARPETA / "datos" / "pozo_sintetico.csv"
    if not ruta.exists():
        parser.error("Primero ejecuta generar_datos.py.")
    datos = np.genfromtxt(ruta, delimiter=",", names=True, encoding="utf-8")
    metadatos = json.loads((ruta.parent / "metadatos.json").read_text(encoding="utf-8"))
    validar_datos(datos)
    temas = ("oscuro", "claro") if argumentos.tema == "ambos" else (argumentos.tema,)
    for tema in temas:
        figura_registros(datos, metadatos, tema)
        figura_relaciones(datos, metadatos, tema)
    print(f"Exportadas {len(temas) * 4} figuras PNG/SVG en {CARPETA / 'Figuras'}")
    if argumentos.sin_mostrar:
        plt.close("all")
    else:
        plt.show()


if __name__ == "__main__":
    main()
