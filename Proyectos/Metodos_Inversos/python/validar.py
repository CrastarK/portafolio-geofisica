import argparse
import hashlib
import io
import json
import platform
import sys
import unittest
from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import to_rgb
from PIL import Image
from problemas import CARPETA, hashes_originales
from visualizar import generar_figuras, TEMAS
from test_numerica import PruebasNumericas


def contraste(color, fondo):
    def luminancia(c):
        valores = np.array(to_rgb(c))
        lineal = np.where(valores <= .04045, valores / 12.92, ((valores + .055) / 1.055)**2.4)
        return float(lineal @ [.2126, .7152, .0722])
    menor, mayor = sorted([luminancia(color), luminancia(fondo)])
    return (mayor + .05) / (menor + .05)


def revisar_textos(fig):
    fig.canvas.draw()
    textos = list(fig.texts)
    for ax in fig.axes:
        if not ax.axison:
            for tabla in ax.tables:
                textos += [celda.get_text() for celda in tabla.get_celld().values()]
            continue
        textos += list(ax.texts) + [ax.title, ax.xaxis.label, ax.yaxis.label]
        if hasattr(ax, "zaxis"):
            textos += [ax.zaxis.label]
        for eje, limites in ((ax.xaxis, ax.get_xlim()), (ax.yaxis, ax.get_ylim())):
            for tick in eje.get_major_ticks():
                if min(limites) <= tick.get_loc() <= max(limites):
                    textos += [tick.label1, tick.label2]
        if ax.get_legend():
            textos += ax.get_legend().get_texts()
    for leyenda in fig.legends:
        textos += leyenda.get_texts() + [leyenda.get_title()]
    cajas = []
    vistos = set()
    for texto in textos:
        if id(texto) in vistos or not texto.get_visible() or not texto.get_text():
            continue
        vistos.add(id(texto))
        caja = texto.get_window_extent(fig.canvas.get_renderer())
        if not np.isfinite(caja.extents).all():
            raise AssertionError(f"Texto sin posición finita: {texto.get_text()}")
        if caja.x0 < 0 or caja.y0 < 0 or caja.x1 > fig.bbox.width or caja.y1 > fig.bbox.height:
            raise AssertionError(f"Texto fuera del lienzo: {texto.get_text()}")
        cajas.append((texto.get_text(), caja))
    solapamientos = []
    for i, (texto, caja) in enumerate(cajas):
        for otro, segunda in cajas[i + 1:]:
            ancho = min(caja.x1, segunda.x1) - max(caja.x0, segunda.x0)
            alto = min(caja.y1, segunda.y1) - max(caja.y0, segunda.y0)
            if ancho > 1 and alto > 1:
                solapamientos.append([texto, otro])
    if solapamientos:
        raise AssertionError(f"Textos superpuestos: {solapamientos}")


def hashes_archivos(carpeta):
    return {str(f.relative_to(carpeta)): hashlib.sha256(f.read_bytes()).hexdigest()
            for f in carpeta.rglob("*") if f.is_file()}


def main():
    parser = argparse.ArgumentParser(description="Validar los resultados conservados sin sobrescribirlos.")
    parser.add_argument("--figuras", type=Path, default=CARPETA / "Figuras")
    argumentos = parser.parse_args()
    antes = hashes_archivos(CARPETA / "resultados")
    resumen = json.loads((CARPETA / "resultados/resumen.json").read_text(encoding="utf-8"))
    originales = hashes_originales()
    if originales != resumen["originales_sha256"]:
        raise AssertionError("Cambió un MATLAB original.")
    salida = io.StringIO()
    pruebas = unittest.defaultTestLoader.loadTestsFromTestCase(PruebasNumericas)
    resultado = unittest.TextTestRunner(stream=salida, verbosity=2).run(pruebas)
    print(salida.getvalue())
    if not resultado.wasSuccessful():
        raise SystemExit(1)
    nombres = ["01_superficie_costo", "02_contornos_trayectorias", "03_convergencia",
               "04_comparacion_algoritmos", "05_inversion_polinomial"]
    informes = {}
    archivos = []
    for tema in ("oscuro", "claro"):
        figuras = generar_figuras(tema, guardar=False)
        for nombre, fig in zip(nombres, figuras):
            revisar_textos(fig)
            for extension in ("png", "svg"):
                archivo = argumentos.figuras / tema / f"{nombre}.{extension}"
                if extension == "png":
                    with Image.open(archivo) as imagen:
                        if abs(imagen.info.get("dpi", [0])[0] - 300) > .1:
                            raise AssertionError("PNG sin 300 dpi.")
                        imagen.verify()
                else:
                    arbol = ET.parse(archivo)
                    if arbol.findall(".//{http://www.w3.org/2000/svg}image"):
                        raise AssertionError("SVG con raster incrustado.")
                    texto = "".join(arbol.getroot().itertext())
                    if "EDGAR LEMUEL / GEOPHYSICS" not in texto:
                        raise AssertionError("Falta atribución en SVG.")
                archivos.append(dict(ruta=str(archivo.relative_to(CARPETA)) if archivo.is_relative_to(CARPETA) else str(archivo),
                                     sha256=hashlib.sha256(archivo.read_bytes()).hexdigest()))
        estilo = TEMAS[tema]
        minimo = min(contraste(estilo[c], estilo[f]) for c in ("texto", "secundario", "acento") for f in ("fondo", "panel"))
        contraste_curvas = min(contraste(c, estilo["panel"]) for c in estilo["colores"])
        if minimo < 4.5 or contraste_curvas < 3:
            raise AssertionError("Contraste insuficiente.")
        informes[tema] = dict(png_300_dpi=5, svg_vectoriales_sin_raster=5,
                              textos_dentro_lienzo=True, sin_solapamientos_texto=True,
                              contraste_min_texto=minimo, contraste_min_curvas=contraste_curvas)
        plt.close("all")
    if hashes_archivos(CARPETA / "resultados") != antes or hashes_originales() != originales:
        raise AssertionError("La validación alteró resultados u originales.")
    reporte = dict(pruebas=resultado.testsRun, fallos=0, errores=0,
                   experimentos_reproducidos_en_memoria=30, historiales_conservados=34,
                   resultados_previos_intactos=True, originales_sha256=originales,
                   semillas=resumen["semillas"], evaluaciones_por_metodo=6000,
                   figuras=informes, exportaciones=archivos,
                   matlab_ejecutado=False, alcance="Coherencia numérica en Python; no validación con observaciones reales.",
                   entorno=dict(python=sys.version, plataforma=platform.platform(), numpy=np.__version__, matplotlib=matplotlib.__version__))
    (CARPETA / "validacion.json").write_text(json.dumps(reporte, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("Validados 30 experimentos, el caso polinomial y 20 exportaciones; resultados anteriores intactos.")


if __name__ == "__main__":
    main()
