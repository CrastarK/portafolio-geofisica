from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, to_rgb

BACKGROUND = "#0A0C0F"
PANEL = "#14191E"
ACCENT = "#8B1E2D"
TEXT = "#E7EBEF"
MUTED = "#BDC5CE"

THEMES = {
    "oscuro": dict(background=BACKGROUND, panel=PANEL, text=TEXT, muted=MUTED,
                   edge="#64707C", grid="#73808C", header="#D17B88"),
    "claro": dict(background="#FAFBFC", panel="#F1F3F5", text="#202830",
                  muted="#48545F", edge="#78838C", grid="#87929C", header=ACCENT),
}


def palette(theme="oscuro"):
    if theme == "claro":
        return dict(Calcita="#28685D", Dolomita="#806019",
                    Cuarzo="#695687", Porosidad="#286587")
    if theme != "oscuro":
        raise ValueError(f"Tema desconocido: {theme}")
    return dict(Calcita="#80B4A8", Dolomita="#D4B77B",
                Cuarzo="#AEA4CB", Porosidad="#78ACD1")


def apply_theme(theme="oscuro"):
    colors = THEMES[theme]
    plt.rcParams.update({
        "figure.facecolor": colors["background"], "axes.facecolor": colors["panel"],
        "savefig.facecolor": colors["background"], "savefig.dpi": 300,
        "font.family": "DejaVu Sans", "font.size": 11,
        "text.color": colors["text"], "axes.labelcolor": colors["text"],
        "xtick.color": colors["muted"], "ytick.color": colors["muted"],
        "axes.edgecolor": colors["edge"], "axes.linewidth": .6,
        "axes.titleweight": "bold", "axes.titlesize": 12,
        "grid.color": colors["grid"], "grid.alpha": .18 if theme == "oscuro" else .25,
        "grid.linewidth": .5, "legend.frameon": False,
        "legend.fontsize": 10, "legend.labelcolor": colors["text"], "figure.dpi": 120,
        "svg.fonttype": "none",
    })
    return colors.copy()


def format_axis(ax, grid=True):
    ax.set_axisbelow(True)
    ax.grid(grid, axis="y")
    ax.spines[["top", "right"]].set_visible(False)
    ax.tick_params(width=.6, length=3, pad=7)


def contrast_text(color):
    # Luminancia sRGB para elegir el texto con mayor contraste.
    rgb = np.array(to_rgb(color))
    linear = np.where(rgb <= .04045, rgb / 12.92, ((rgb + .055) / 1.055) ** 2.4)
    luminance = float(linear @ np.array([.2126, .7152, .0722]))
    return "#000000" if (luminance + .05) / .05 >= 1.05 / (luminance + .05) else "#FFFFFF"


def volume_cmap():
    return LinearSegmentedColormap.from_list("scientific_volume", ["#14191E", ACCENT, "#D8AE91", "#F1E6D7"])


def difference_cmap(theme="oscuro"):
    if theme == "claro":
        return LinearSegmentedColormap.from_list("scientific_difference_light", ["#286587", "#F1F3F5", ACCENT])
    return LinearSegmentedColormap.from_list("scientific_difference_dark", ["#78ACD1", PANEL, "#DFA095"])


def decorate_figure(fig, title, subtitle):
    colors = next(c for c in THEMES.values() if to_rgb(c["background"]) == to_rgb(fig.get_facecolor()))
    fig.text(.08, .94, "EDGAR LEMUEL / GEOPHYSICS", color=colors["header"], fontsize=9, weight="bold")
    fig.text(.08, .885, title, fontsize=17, weight="bold")
    fig.text(.08, .837, subtitle, fontsize=10, color=colors["muted"])
    fig.text(.08, .035, "Edgar Lemuel Fuentes Solano | Datos sintéticos", fontsize=9, color=colors["muted"])
    # Topografía decorativa fuera de los datos.
    ax = fig.add_axes([.77, .915, .19, .065], zorder=-1)
    t = np.linspace(0, 1, 180)
    for offset in np.linspace(0, 1, 6):
        ax.plot(t, .09 * np.sin(t * 9 + offset) + offset, color=ACCENT, alpha=.25, lw=.5)
    ax.set_axis_off()


def export_figure(fig, directory, name):
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    for extension in ("png", "svg"):
        fig.savefig(directory / f"{name}.{extension}", dpi=300,
                    bbox_inches="tight", pad_inches=.2, facecolor=fig.get_facecolor())
