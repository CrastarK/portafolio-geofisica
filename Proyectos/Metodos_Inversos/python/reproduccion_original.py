import numpy as np
from problemas import costo, problema_polinomial
from algoritmos import codificar, _resultado, recocido_continuo


def limite_modelo25(valor):
    return 3. if valor < -3 or valor > 3 else valor


def reproducir_superficie(archivo, semilla=42):
    if archivo not in ("modelo22", "modelo25"):
        raise ValueError("Solo se reproducen aquí los ciclos completos de modelo22 y modelo25.")
    rng = np.random.default_rng(semilla)
    modelo = np.array([-1.6, .6])
    actual = float(costo(*modelo))
    mejor, optimo = actual, modelo.copy()
    historial = [[0, 1, actual, mejor, *modelo, *optimo]]
    recocido = archivo == "modelo25"
    ciclos, amplitud, tolerancia = (8, .5, 2.) if recocido else (1, .1, 1.9)
    evaluaciones = 1
    for k in range(500):
        if actual <= tolerancia:
            break
        temperatura = 1e6 * (1e-7 / 1e6) ** (k / 500)
        for _ in range(ciclos):
            for c in range(2):
                candidato = modelo.copy()
                candidato[c] += rng.uniform(-amplitud, amplitud)
                if recocido:
                    candidato[c] = limite_modelo25(candidato[c])
                propuesto = float(costo(*candidato))
                admitido = propuesto < actual
                if recocido and not admitido:
                    admitido = rng.random() < np.exp(-(propuesto - actual) / temperatura)
                if admitido:
                    modelo, actual = candidato, propuesto
                if actual < mejor:
                    mejor, optimo = actual, modelo.copy()
                evaluaciones += 1
                historial.append([k + 1, evaluaciones, actual, mejor, *modelo, *optimo])
    return _resultado(archivo + "_reproduccion_python", semilla, historial,
                      parada="tolerancia_actual" if actual <= tolerancia else "itermax",
                      alcance="Traducción de operaciones; no ejecución MATLAB ni identidad de secuencias aleatorias.")


def inicializar_genetico_original(semilla=42):
    rng = np.random.default_rng(semilla)
    indices = rng.integers(0, 61, size=(10, 2))
    poblacion = codificar(indices, n=61, bits=10)
    eje = np.linspace(-3, 3, 61)
    return poblacion, indices, costo(eje[indices[:, 0]], eje[indices[:, 1]])


def mutacion_original(poblacion, semilla=42):
    rng = np.random.default_rng(semilla)
    salida = poblacion.copy()
    for bloque in range(2):
        for fila in range(len(salida)):
            if rng.random() < .5:
                salida[fila, bloque * 10 + rng.integers(0, 10)] = 0
    return salida


def evolucion_genetica_original():
    raise NotImplementedError("geneticos1.m no suministra vale(parejas), usa mil y no implementa el ciclo generacional ni supervivientes.")


def reproducir_polinomio(semilla=42):
    _, g, _, datos = problema_polinomial()
    return recocido_continuo(lambda m: np.linalg.norm(datos - g @ m),
                            np.zeros(4), [10, 1, .1, .01], [[-3, 3]] * 4,
                            semilla=semilla, itermax=200, ciclos=8,
                            ti=1e6, tf=1e-6, tolerancia=1)
