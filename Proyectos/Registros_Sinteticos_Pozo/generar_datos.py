from pathlib import Path
import argparse
import csv
import json
import numpy as np

CARPETA = Path(__file__).resolve().parent
SEMILLA = 42
INTERVALOS = [
    # techo, base, código, nombre, arcillosidad, porosidad, saturación de agua
    (1000, 1060, 1, "Lutita", .78, .10, 1.00),
    (1060, 1115, 2, "Arena limpia", .04, .16, 1.00),
    (1115, 1170, 3, "Arena porosa", .08, .28, 1.00),
    (1170, 1210, 4, "Respuesta HC simulada", .02, .24, .25),
    (1210, 1260, 5, "Intervalo compacto", .06, .065, 1.00),
    (1260, 1300, 1, "Lutita", .70, .12, 1.00),
]
UNIDADES = {
    "DEPTH": "m", "GR": "API", "SP": "mV", "CALI": "in",
    "RHOB": "g/cm3", "NPHI": "fraccion", "DT": "us/ft", "RT": "ohm.m",
    "VSH_TRUE": "fraccion", "PHI_TRUE": "fraccion", "SW_TRUE": "fraccion",
    "LITH_CODE": "categoria impuesta",
}


def ruido_correlacionado(rng, cantidad, sigma):
    radio = int(np.ceil(4 * sigma))
    x = np.arange(-radio, radio + 1)
    kernel = np.exp(-.5 * (x / sigma) ** 2)
    kernel /= kernel.sum()
    ruido = rng.normal(size=cantidad)
    ruido = np.convolve(np.pad(ruido, radio, mode="reflect"), kernel, mode="valid")
    return (ruido - ruido.mean()) / ruido.std()


def generar_pozo(semilla=SEMILLA):
    rng = np.random.default_rng(semilla)
    profundidad = np.arange(1000, 1300.25, .25)
    limites = np.array([intervalo[1] for intervalo in INTERVALOS[:-1]])
    transiciones = .5 * (1 + np.tanh((profundidad[:, None] - limites) / .65))
    pesos = np.column_stack([1 - transiciones[:, 0],
                             transiciones[:, :-1] - transiciones[:, 1:],
                             transiciones[:, -1]])
    parametros = np.array([intervalo[4:] for intervalo in INTERVALOS])
    vsh, phi, sw = (pesos @ parametros).T
    cantidad = len(profundidad)
    geologia = ruido_correlacionado(rng, cantidad, 5)
    laminacion = ruido_correlacionado(rng, cantidad, 1.5)
    vsh = np.clip(vsh + .025 * geologia + .012 * laminacion, .005, .95)
    phi = np.clip(phi - .008 * geologia + .006 * laminacion, .035, .36)
    sw = np.clip(sw + .02 * (1 - sw) * laminacion, .15, 1)

    rho_matriz = 2.65 * (1 - vsh) + 2.72 * vsh
    rho_fluido = 1.05 * sw + .25 * (1 - sw)
    gr = 20 + 130 * vsh + 2.5 * ruido_correlacionado(rng, cantidad, 1)
    sp = -65 * (1 - vsh) * np.minimum(phi / .24, 1)
    sp += 4 * (profundidad - 1000) / 300 + 1.5 * ruido_correlacionado(rng, cantidad, 2)
    cali = 8.5 + .95 * vsh + .06 * ruido_correlacionado(rng, cantidad, 2)
    cali += .8 * np.exp(-.5 * ((profundidad - 1028) / 4) ** 2)
    cali += .65 * np.exp(-.5 * ((profundidad - 1282) / 5) ** 2)
    rhob = (1 - phi) * rho_matriz + phi * rho_fluido + rng.normal(0, .008, cantidad)
    nphi = phi * (sw + .25 * (1 - sw)) + .25 * vsh + rng.normal(0, .004, cantidad)
    dt_matriz = 55.5 * (1 - vsh) + 75 * vsh
    dt_fluido = 189 * sw + 310 * (1 - sw)
    dt = (1 - phi) * dt_matriz + phi * dt_fluido + rng.normal(0, .6, cantidad)

    # Archie idealizado y conducción arcillosa en paralelo.
    rt_arena = .08 / (phi ** 2 * sw ** 2)
    rt = 1 / ((1 - vsh) / rt_arena + vsh / 2)
    rt *= np.exp(.06 * ruido_correlacionado(rng, cantidad, 2))
    indices = np.searchsorted(limites, profundidad, side="right")
    codigos = np.array([intervalo[2] for intervalo in INTERVALOS])[indices]
    return dict(DEPTH=profundidad, GR=gr, SP=sp, CALI=cali, RHOB=rhob,
                NPHI=nphi, DT=dt, RT=rt, VSH_TRUE=vsh, PHI_TRUE=phi,
                SW_TRUE=sw, LITH_CODE=codigos)


def guardar_datos(datos, semilla):
    carpeta = CARPETA / "datos"
    carpeta.mkdir(exist_ok=True)
    ruta = carpeta / "pozo_sintetico.csv"
    with ruta.open("w", newline="", encoding="utf-8") as archivo:
        escritor = csv.writer(archivo, lineterminator="\n")
        escritor.writerow(datos.keys())
        for fila in zip(*datos.values()):
            escritor.writerow([f"{fila[0]:.2f}"] + [f"{v:.6f}" for v in fila[1:-1]] + [int(fila[-1])])
    metadatos = {
        "autor": "Edgar Lemuel Fuentes Solano",
        "origen": "Generación matemática propia; sin archivos de entrada ni datos privados.",
        "naturaleza": "Datos íntegramente sintéticos, no mediciones ni interpretación de un pozo real.",
        "semilla": semilla, "numpy": np.__version__, "muestras": len(datos["DEPTH"]),
        "paso_m": .25, "unidades": UNIDADES,
        "intervalos": [dict(techo_m=i[0], base_m=i[1], codigo=i[2], nombre=i[3],
                            vsh_base=i[4], phi_base=i[5], sw_base=i[6]) for i in INTERVALOS],
        "convencion_intervalos": "[techo, base), salvo el último que incluye 1300 m; etiquetas abruptas y propiedades suavizadas.",
        "referencias_impuestas": ["VSH_TRUE", "PHI_TRUE", "SW_TRUE", "LITH_CODE"],
        "modelo": "Relaciones idealizadas y ruido correlacionado; no simulación de una herramienta comercial.",
    }
    (carpeta / "metadatos.json").write_text(json.dumps(metadatos, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return ruta


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generar un pozo completamente sintético.")
    parser.add_argument("--semilla", type=int, default=SEMILLA)
    argumentos = parser.parse_args()
    datos = generar_pozo(argumentos.semilla)
    print(guardar_datos(datos, argumentos.semilla))
