from pathlib import Path
import hashlib
import json
import xml.etree.ElementTree as ET
import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import to_rgb
from PIL import Image
import generar_datos as generador
import visualizar_registros as visor

CARPETA = Path(__file__).resolve().parent


def contraste(color, fondo):
    def luminancia(valor):
        rgb = np.array(to_rgb(valor))
        rgb = np.where(rgb <= .04045, rgb / 12.92, ((rgb + .055) / 1.055) ** 2.4)
        return float(rgb @ [.2126, .7152, .0722])
    menor, mayor = sorted([luminancia(color), luminancia(fondo)])
    return (mayor + .05) / (menor + .05)


def revisar_textos(fig):
    fig.canvas.draw()
    textos = list(fig.texts)
    for ax in fig.axes:
        textos += list(ax.texts) + [ax.title, ax.xaxis.label, ax.yaxis.label]
        for eje, limites in ((ax.xaxis, ax.get_xlim()), (ax.yaxis, ax.get_ylim())):
            for tick in eje.get_major_ticks():
                if min(limites) <= tick.get_loc() <= max(limites):
                    textos += [tick.label1, tick.label2]
        if ax.get_legend():
            textos += ax.get_legend().get_texts()
    for leyenda in fig.legends:
        textos += leyenda.get_texts() + [leyenda.get_title()]
    cajas = []
    for texto in textos:
        if not texto.get_visible() or not texto.get_text():
            continue
        caja = texto.get_window_extent(fig.canvas.get_renderer())
        assert np.isfinite(caja.extents).all(), texto.get_text()
        assert caja.x0 >= 0 and caja.y0 >= 0, texto.get_text()
        assert caja.x1 <= fig.bbox.width and caja.y1 <= fig.bbox.height, texto.get_text()
        cajas.append((texto.get_text(), caja))
    for i, (texto, caja) in enumerate(cajas):
        for otro, segunda in cajas[i + 1:]:
            ancho = min(caja.x1, segunda.x1) - max(caja.x0, segunda.x0)
            alto = min(caja.y1, segunda.y1) - max(caja.y0, segunda.y0)
            assert ancho <= 1 or alto <= 1, f"Textos superpuestos: {texto} / {otro}"


def main():
    ruta = CARPETA / "datos" / "pozo_sintetico.csv"
    datos = np.genfromtxt(ruta, delimiter=",", names=True, encoding="utf-8")
    metadatos = json.loads((ruta.parent / "metadatos.json").read_text(encoding="utf-8"))
    visor.validar_datos(datos)
    referencia = generador.generar_pozo(metadatos["semilla"])
    repeticion = generador.generar_pozo(metadatos["semilla"])
    otra_semilla = generador.generar_pozo(metadatos["semilla"] + 1)
    assert not np.array_equal(referencia["GR"], otra_semilla["GR"])
    for nombre in referencia:
        np.testing.assert_array_equal(referencia[nombre], repeticion[nombre])
        np.testing.assert_allclose(datos[nombre], referencia[nombre], rtol=0, atol=5.01e-7)
    assert len(datos) == metadatos["muestras"] == 1201
    np.testing.assert_array_equal(np.diff(datos["DEPTH"]), .25)
    assert datos["DEPTH"][0] == 1000 and datos["DEPTH"][-1] == 1300
    for nombre in ("VSH_TRUE", "PHI_TRUE", "SW_TRUE"):
        assert np.all((datos[nombre] > 0) & (datos[nombre] <= 1)), nombre
    assert np.all(datos["GR"] >= 0) and np.all(datos["RHOB"] > 0) and np.all(datos["DT"] > 0)
    for techo, base, codigo, *_ in generador.INTERVALOS:
        mascara = (datos["DEPTH"] >= techo) & (datos["DEPTH"] < base)
        assert np.all(datos["LITH_CODE"][mascara] == codigo)
    medianas = {int(c): {n: float(np.median(datos[n][datos["LITH_CODE"] == c]))
                        for n in ("GR", "CALI", "RHOB", "NPHI", "DT", "RT", "PHI_TRUE")}
                for c in np.unique(datos["LITH_CODE"])}
    assert medianas[1]["GR"] > medianas[2]["GR"]
    assert medianas[1]["CALI"] > medianas[2]["CALI"]
    assert medianas[3]["PHI_TRUE"] > medianas[2]["PHI_TRUE"] > medianas[5]["PHI_TRUE"]
    assert medianas[4]["RT"] > medianas[3]["RT"] and medianas[5]["RT"] > medianas[3]["RT"]
    assert medianas[4]["NPHI"] < medianas[3]["NPHI"]

    resultados = {}
    for tema in ("oscuro", "claro"):
        figuras = [visor.figura_registros(datos, metadatos, tema), visor.figura_relaciones(datos, metadatos, tema)]
        registros, relaciones = figuras
        for ax, nombre in zip(registros.axes[1:], ("GR", "SP", "CALI", "RHOB", "NPHI", "DT", "RT")):
            np.testing.assert_array_equal(ax.lines[0].get_xdata(), datos[nombre])
            np.testing.assert_array_equal(ax.lines[0].get_ydata(), datos["DEPTH"])
            assert min(ax.get_xlim()) <= datos[nombre].min() <= datos[nombre].max() <= max(ax.get_xlim()), nombre
        assert registros.axes[0].yaxis_inverted() and registros.axes[-1].get_xscale() == "log"
        for ax in relaciones.axes:
            assert sum(len(c.get_offsets()) for c in ax.collections) == len(datos)
        for fig in figuras:
            revisar_textos(fig)
        estilo = visor.TEMAS[tema]
        minimo = min(contraste(estilo[c], estilo[f]) for c in ("texto", "secundario", "acento") for f in ("fondo", "panel"))
        assert minimo >= 4.5
        assert contraste(estilo["curva"], estilo["panel"]) >= 3
        archivos = sorted((CARPETA / "Figuras" / tema).glob("*"))
        assert len(archivos) == 4
        for archivo in archivos:
            if archivo.suffix == ".png":
                with Image.open(archivo) as imagen:
                    assert abs(imagen.info["dpi"][0] - 300) < .1
                    imagen.verify()
            else:
                arbol = ET.parse(archivo)
                assert not arbol.findall(".//{http://www.w3.org/2000/svg}image")
                assert "Datos 100 % sintéticos" in "".join(arbol.getroot().itertext())
        resultados[tema] = dict(archivos=4, png_300_dpi=2, svg_sin_raster=2,
                                contraste_min_texto=minimo, sin_recortes_de_curvas=True,
                                sin_textos_cortados_o_superpuestos=True)
        plt.close("all")
    reporte = {
        "alcance": "Coherencia interna y exportación de una simulación propia; no validación con datos reales.",
        "semilla": metadatos["semilla"], "muestras": len(datos), "columnas": list(datos.dtype.names),
        "sin_nulos": True, "profundidad_regular": True, "generacion_reproducible": True,
        "tolerancia_csv": 5.01e-7, "variacion_con_otra_semilla": True,
        "respuestas_relativas_impuestas_comprobadas": True, "medianas_por_codigo": medianas,
        "rangos_generados": {n: [float(datos[n].min()), float(datos[n].max())] for n in datos.dtype.names},
        "sha256_csv": hashlib.sha256(ruta.read_bytes()).hexdigest(), "figuras": resultados,
        "versiones": dict(numpy=np.__version__, matplotlib=matplotlib.__version__),
    }
    (CARPETA / "validacion.json").write_text(json.dumps(reporte, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("Comprobados: 1 201 muestras reproducibles, cinco facies y ocho exportaciones PNG/SVG.")


if __name__ == "__main__":
    main()
