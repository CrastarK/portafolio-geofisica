import argparse
import csv
import json
import platform
from pathlib import Path
import numpy as np
import matplotlib
from problemas import CARPETA, costo, malla, problema_polinomial, hashes_originales
from algoritmos import explorar_malla, genetico, recocido_continuo
from reproduccion_original import reproducir_superficie, reproducir_polinomio, inicializar_genetico_original

SEMILLAS = [7, 19, 42, 73, 101, 137, 211, 307, 401, 503]


def guardar_historial(ruta, resultado):
    dimension = len(resultado["modelo"])
    columnas = ["iteracion", "evaluaciones", "costo_actual", "mejor_costo"]
    columnas += [f"actual_m{i + 1}" for i in range(dimension)]
    columnas += [f"mejor_m{i + 1}" for i in range(dimension)]
    np.savetxt(ruta, resultado["historial"], delimiter=",", header=",".join(columnas),
               comments="", fmt="%.17g")


def estudiar_polinomio(semilla=42):
    x, g, verdadero, datos = problema_polinomial()
    estimado, _, rango, singulares = np.linalg.lstsq(g, datos, rcond=None)
    original = reproducir_polinomio(semilla)
    norma_d = np.linalg.norm(datos)
    norma_columnas = np.linalg.norm(g, axis=0)
    a = g / norma_columnas
    y = datos / norma_d
    escalado = recocido_continuo(lambda q: np.linalg.norm(y - a @ q), np.zeros(4),
                                 [.12] * 4, [[-2, 2]] * 4, semilla=semilla,
                                 itermax=1000, ciclos=12, ti=.1, tf=1e-8, tolerancia=None)
    modelo_escalado = escalado["modelo"] * norma_d / norma_columnas
    return dict(x=x, g=g, datos=datos, verdadero=verdadero, minimos_cuadrados=estimado,
                rango=int(rango), singulares=singulares, condicion=float(np.linalg.cond(g)),
                condicion_escalada=float(np.linalg.cond(a)), original=original,
                escalado=escalado, modelo_escalado=modelo_escalado,
                norma_d=float(norma_d), norma_columnas=norma_columnas)


def main():
    parser = argparse.ArgumentParser(description="Comparación reproducible de algoritmos académicos migrados.")
    parser.add_argument("--presupuesto", type=int, default=6000)
    parser.add_argument("--salida", type=Path, default=CARPETA / "resultados")
    argumentos = parser.parse_args()
    if argumentos.presupuesto < 40:
        parser.error("El presupuesto debe ser >=40 para la población inicial.")
    carpeta = argumentos.salida.resolve()
    if carpeta.exists() and (not carpeta.is_dir() or any(carpeta.iterdir())):
        parser.error("La carpeta de salida ya contiene archivos. Usa --salida con una carpeta nueva; no se sobrescriben resultados.")
    historiales = carpeta / "historiales"
    historiales.mkdir(parents=True, exist_ok=True)
    referencia = malla()
    fina = malla(301)
    variante = malla(variante="recristalizacion")
    np.savez(carpeta / "superficies.npz", m1=referencia["m1"], m2=referencia["m2"],
             costo=referencia["valores"], alternativa=costo(referencia["m1"], referencia["m2"], "recristalizacion"))
    filas = []
    for semilla in SEMILLAS:
        for metodo in ("local", "recocido", "genetico"):
            resultado = genetico(semilla, argumentos.presupuesto) if metodo == "genetico" else explorar_malla(metodo, semilla, argumentos.presupuesto)
            guardar_historial(historiales / f"{metodo}_{semilla}.csv", resultado)
            brecha = resultado["mejor_costo"] - referencia["costo"]
            historia = resultado["historial"]
            alcanzado = np.flatnonzero(historia[:, 3] <= referencia["costo"] + 1e-12)
            filas.append(dict(metodo=metodo, semilla=semilla, m1=resultado["modelo"][0],
                              m2=resultado["modelo"][1], costo=resultado["mejor_costo"],
                              brecha_malla=brecha, distancia_malla=float(np.linalg.norm(resultado["modelo"] - referencia["modelo"])),
                              evaluaciones=resultado["evaluaciones"], iteraciones=int(historia[-1, 0]),
                              alcanza_referencia=bool(len(alcanzado)),
                              evaluaciones_primera_referencia=int(historia[alcanzado[0], 1]) if len(alcanzado) else "",
                              reparaciones=resultado.get("reparaciones", 0)))
    with (carpeta / "comparacion.csv").open("w", newline="", encoding="utf-8") as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=list(filas[0]), lineterminator="\n")
        escritor.writeheader()
        escritor.writerows(filas)
    replicas = {}
    for nombre in ("modelo22", "modelo25"):
        resultado = reproducir_superficie(nombre)
        guardar_historial(historiales / f"{nombre}_reproduccion_python.csv", resultado)
        replicas[nombre] = dict(modelo=resultado["modelo"].tolist(), costo=resultado["mejor_costo"],
                                evaluaciones=resultado["evaluaciones"], parada=resultado["parada"])
    poblacion, indices, valores = inicializar_genetico_original()
    np.savez(carpeta / "genetico_inicial_original.npz", poblacion=poblacion, indices_python=indices, costos=valores)
    polinomio = estudiar_polinomio()
    guardar_historial(historiales / "polinomio_limites_originales.csv", polinomio["original"])
    guardar_historial(historiales / "polinomio_escalado.csv", polinomio["escalado"])
    np.savez(carpeta / "polinomio.npz", x=polinomio["x"], g=polinomio["g"], datos=polinomio["datos"],
             verdadero=polinomio["verdadero"], minimos_cuadrados=polinomio["minimos_cuadrados"],
             original=polinomio["original"]["modelo"], escalado=polinomio["modelo_escalado"])

    def referencia_json(r):
        return {k: r[k] for k in ("modelo", "costo", "evaluaciones")}

    resumen = {
        "ejecucion": "Python/NumPy exclusivamente; MATLAB y Octave no ejecutados.",
        "originales_sha256": hashes_originales(), "semillas": SEMILLAS,
        "presupuesto_por_algoritmo": argumentos.presupuesto,
        "comparacion": "Misma función E y malla 61x61; cada candidato evaluado cuenta, incluidos duplicados. Sin parada por costo.",
        "referencia_malla_61": referencia_json(referencia),
        "referencia_fina_301_no_comparable_como_error_del_AG": referencia_json(fina),
        "variante_recristalizacion_malla61": referencia_json(variante),
        "resultados": {metodo: dict(costo_mediano=float(np.median([f["costo"] for f in filas if f["metodo"] == metodo])),
                                    brecha_mediana=float(np.median([f["brecha_malla"] for f in filas if f["metodo"] == metodo])),
                                    aciertos_malla=sum(f["alcanza_referencia"] for f in filas if f["metodo"] == metodo))
                       for metodo in ("local", "recocido", "genetico")},
        "reproducciones_python_no_MATLAB": replicas,
        "polinomio": dict(verdadero=polinomio["verdadero"].tolist(),
                          minimos_cuadrados=polinomio["minimos_cuadrados"].tolist(),
                          modelo_limites_originales=polinomio["original"]["modelo"].tolist(),
                          modelo_recocido_escalado=polinomio["modelo_escalado"].tolist(),
                          error_ls=float(np.linalg.norm(polinomio["datos"] - polinomio["g"] @ polinomio["minimos_cuadrados"])),
                          error_original=polinomio["original"]["mejor_costo"],
                          error_escalado=float(np.linalg.norm(polinomio["datos"] - polinomio["g"] @ polinomio["modelo_escalado"])),
                          condicion=polinomio["condicion"], condicion_escalada=polinomio["condicion_escalada"],
                          rango=polinomio["rango"], evaluaciones_escalado=polinomio["escalado"]["evaluaciones"],
                          escalado="A_j=G_j/||G_j||, y=d/||d||, q_j=m_j||G_j||/||d||; q en [-2,2]. No usa m_true para proponer ni aceptar.",
                          cota_inferior_error_caja_original=497.,
                          nota="La cota 497 usa únicamente x=0 y |m0|<=3; no es el mínimo de la caja."),
        "versiones": dict(python=platform.python_version(), numpy=np.__version__, matplotlib=matplotlib.__version__),
    }
    (carpeta / "resumen.json").write_text(json.dumps(resumen, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(resumen["resultados"], ensure_ascii=False, indent=2))
    print("Error polinomial LS / caja original / recocido escalado:", resumen["polinomio"]["error_ls"],
          resumen["polinomio"]["error_original"], resumen["polinomio"]["error_escalado"])


if __name__ == "__main__":
    main()
