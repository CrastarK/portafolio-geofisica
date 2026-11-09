import numpy as np
from problemas import costo


def codificar(indices, n=61, bits=6):
    indices = np.asarray(indices)
    if not isinstance(bits, (int, np.integer)) or not isinstance(n, (int, np.integer)):
        raise ValueError("n y bits deben ser enteros.")
    if bits < 1 or bits > 30 or n < 2 or n > 2**bits - 1:
        raise ValueError("La codificación de índices 1..n no cabe en los bits indicados.")
    if indices.ndim != 2 or indices.shape[1] != 2 or not np.issubdtype(indices.dtype, np.integer):
        raise ValueError("Se espera una matriz entera de índices con dos columnas.")
    if np.any(indices < 0) or np.any(indices >= n):
        raise ValueError("Índice fuera del dominio 0..n-1.")
    # Mantener el valor binario 1..n del diseño MATLAB; restar uno al decodificar.
    pesos = np.arange(bits - 1, -1, -1)
    return (((indices + 1)[..., None] >> pesos) & 1).reshape(-1, 2 * bits).astype(np.uint8)


def decodificar(poblacion, bits=6):
    poblacion = np.asarray(poblacion)
    if not isinstance(bits, (int, np.integer)) or bits < 1 or bits > 30 or poblacion.ndim != 2 or poblacion.shape[1] != 2 * bits:
        raise ValueError("Longitud de cromosoma incorrecta.")
    if not np.isin(poblacion, [0, 1]).all():
        raise ValueError("Los genes deben ser bits numéricos 0 o 1.")
    pesos = 2 ** np.arange(bits - 1, -1, -1)
    return poblacion.reshape(-1, 2, bits).astype(np.int64) @ pesos - 1


def reparar(poblacion, rng, n=61, bits=6):
    indices = decodificar(poblacion, bits)
    invalidos = (indices < 0) | (indices >= n)
    indices[invalidos] = rng.integers(0, n, size=invalidos.sum())
    return codificar(indices, n, bits), int(invalidos.sum())


def mutar(poblacion, probabilidad, rng):
    poblacion = np.asarray(poblacion)
    if not 0 <= probabilidad <= 1:
        raise ValueError("Probabilidad de mutación fuera de [0,1].")
    if not np.isin(poblacion, [0, 1]).all():
        raise ValueError("Se necesitan bits numéricos.")
    return np.bitwise_xor(np.asarray(poblacion, dtype=np.uint8),
                          (rng.random(poblacion.shape) < probabilidad).astype(np.uint8))


def cruzar(padre, madre, punto):
    if len(padre) != len(madre) or not 1 <= punto < len(padre):
        raise ValueError("Cruce fuera de los genes interiores.")
    return (np.r_[padre[:punto], madre[punto:]], np.r_[madre[:punto], padre[punto:]])


def aceptar(delta, temperatura, uniforme):
    if not np.isfinite(delta):
        raise ValueError("La diferencia de costo debe ser finita.")
    if temperatura <= 0 or not np.isfinite(temperatura):
        raise ValueError("La temperatura debe ser positiva y finita.")
    if not 0 <= uniforme < 1:
        raise ValueError("El uniforme debe estar en [0,1).")
    return delta <= 0 or uniforme == 0 or np.log(uniforme) < -delta / temperatura


def _resultado(metodo, semilla, historial, **extra):
    historial = np.asarray(historial, dtype=float)
    dimension = (historial.shape[1] - 4) // 2
    return dict(metodo=metodo, semilla=int(semilla), historial=historial,
                modelo=historial[-1, 4 + dimension:].copy(), mejor_costo=float(historial[-1, 3]),
                evaluaciones=int(historial[-1, 1]), **extra)


def explorar_malla(metodo, semilla=42, presupuesto=6000, n=61):
    if not isinstance(presupuesto, (int, np.integer)) or not isinstance(n, (int, np.integer)):
        raise ValueError("El presupuesto y n deben ser enteros.")
    if metodo not in ("local", "recocido") or presupuesto < 1 or n < 2:
        raise ValueError("Método, presupuesto o malla inválidos.")
    rng = np.random.default_rng(semilla)
    eje = np.linspace(-3, 3, n)
    indice = np.rint((np.array([-1.6, .6]) + 3) * (n - 1) / 6).astype(int)
    modelo = eje[indice]
    actual = float(costo(*modelo))
    mejor, optimo = actual, modelo.copy()
    historial = [[0, 1, actual, mejor, *modelo, *optimo]]
    propuestas_nivel = 16 if metodo == "recocido" else 2
    niveles = max(1, int(np.ceil((presupuesto - 1) / propuestas_nivel)))
    aceptadas = 0
    for evaluacion in range(2, presupuesto + 1):
        coordenada = (evaluacion - 2) % 2
        amplitud = 5 if metodo == "recocido" else 1
        paso = int(rng.integers(1, amplitud + 1)) * rng.choice([-1, 1])
        candidato = indice.copy()
        candidato[coordenada] = np.clip(candidato[coordenada] + paso, 0, n - 1)
        propuesto = float(costo(*eje[candidato]))
        nivel = (evaluacion - 2) // propuestas_nivel
        temperatura = 10 * (1e-5 / 10) ** (nivel / max(1, niveles - 1))
        admitido = propuesto < actual if metodo == "local" else aceptar(propuesto - actual, temperatura, rng.random())
        if admitido:
            indice, actual = candidato, propuesto
            aceptadas += 1
        modelo = eje[indice]
        if actual < mejor:
            mejor, optimo = actual, modelo.copy()
        historial.append([nivel + 1, evaluacion, actual, mejor, *modelo, *optimo])
    return _resultado(metodo, semilla, historial, aceptadas=aceptadas,
                      parada="presupuesto", dominio="malla")


def genetico(semilla=42, presupuesto=6000, n=61, bits=6, individuos=40, probabilidad=None):
    if not all(isinstance(v, (int, np.integer)) for v in (presupuesto, individuos, n, bits)):
        raise ValueError("Población, presupuesto, n y bits deben ser enteros.")
    if individuos < 4 or individuos % 2 or presupuesto < individuos:
        raise ValueError("Se requiere población par >=4 y presupuesto suficiente.")
    rng = np.random.default_rng(semilla)
    eje = np.linspace(-3, 3, n)
    poblacion = codificar(rng.integers(0, n, size=(individuos, 2)), n, bits)
    probabilidad = 1 / (2 * bits) if probabilidad is None else probabilidad
    if not 0 <= probabilidad <= 1:
        raise ValueError("Probabilidad inválida.")

    def evaluar(bits_poblacion):
        indices = decodificar(bits_poblacion, bits)
        if np.any(indices < 0) or np.any(indices >= n):
            raise ValueError("Índices inválidos antes de evaluar.")
        modelos = eje[indices]
        return costo(modelos[:, 0], modelos[:, 1]), modelos

    valores, modelos = evaluar(poblacion)
    mejor = int(np.argmin(valores))
    historial = [[0, individuos, valores[mejor], valores[mejor], *modelos[mejor], *modelos[mejor]]]
    evaluaciones, generacion, reparaciones = individuos, 0, 0
    while evaluaciones < presupuesto:
        hijos = []
        cantidad = min(individuos, presupuesto - evaluaciones)
        while len(hijos) < cantidad:
            padres = []
            for _ in range(2):
                torneo = rng.integers(0, individuos, size=3)
                padres.append(poblacion[torneo[np.argmin(valores[torneo])]])
            hijos.extend(cruzar(*padres, int(rng.integers(1, 2 * bits))))
        hijos = mutar(np.array(hijos[:cantidad]), probabilidad, rng)
        hijos, reparados = reparar(hijos, rng, n, bits)
        reparaciones += reparados
        costos_hijos, _ = evaluar(hijos)
        combinada = np.vstack([poblacion, hijos])
        costos = np.r_[valores, costos_hijos]
        supervivientes = np.argsort(costos, kind="stable")[:individuos]
        poblacion, valores = combinada[supervivientes], costos[supervivientes]
        # Reutilizar evaluaciones; padres e hijos compiten con elitismo.
        modelos = eje[decodificar(poblacion, bits)]
        evaluaciones += cantidad
        generacion += 1
        historial.append([generacion, evaluaciones, valores[0], valores[0], *modelos[0], *modelos[0]])
    return _resultado("genetico", semilla, historial, reparaciones=reparaciones,
                      bits=bits, individuos=individuos, mutacion=probabilidad,
                      parada="presupuesto", dominio="malla")


def recocido_continuo(funcion, inicial, amplitud, limites, semilla=42,
                      itermax=200, ciclos=8, ti=1e6, tf=1e-6, tolerancia=1):
    if not all(isinstance(v, (int, np.integer)) for v in (itermax, ciclos)):
        raise ValueError("Iteraciones y ciclos deben ser enteros.")
    if itermax < 1 or ciclos < 1 or not np.isfinite([ti, tf]).all() or ti <= 0 or tf <= 0:
        raise ValueError("Parámetros de recocido inválidos.")
    rng = np.random.default_rng(semilla)
    modelo = np.array(inicial, dtype=float)
    amplitud = np.asarray(amplitud, dtype=float)
    limites = np.asarray(limites, dtype=float)
    if modelo.ndim != 1 or not np.isfinite(modelo).all():
        raise ValueError("El modelo inicial debe ser un vector finito.")
    if limites.shape != (len(modelo), 2) or not np.isfinite(limites).all() or np.any(limites[:, 0] >= limites[:, 1]):
        raise ValueError("Límites inválidos.")
    if amplitud.shape != modelo.shape or not np.isfinite(amplitud).all() or np.any(amplitud <= 0):
        raise ValueError("Amplitudes inválidas.")
    if np.any(modelo < limites[:, 0]) or np.any(modelo > limites[:, 1]):
        raise ValueError("Modelo inicial fuera de límites.")
    actual = float(funcion(modelo))
    if not np.isfinite(actual):
        raise ValueError("Costo inicial no finito.")
    mejor, optimo = actual, modelo.copy()
    historial = [[0, 1, actual, mejor, *modelo, *optimo]]
    evaluaciones, probabilidades = 1, []
    for k in range(itermax):
        if tolerancia is not None and actual <= tolerancia:
            break
        temperatura = ti * (tf / ti) ** (k / itermax)
        for _ in range(ciclos):
            for c in range(len(modelo)):
                candidato = modelo.copy()
                candidato[c] += rng.uniform(-amplitud[c], amplitud[c])
                candidato = np.clip(candidato, limites[:, 0], limites[:, 1])
                propuesto = float(funcion(candidato))
                if not np.isfinite(propuesto):
                    raise ValueError("Costo propuesto no finito.")
                delta = propuesto - actual
                probabilidad = float(np.exp(-max(0., delta) / temperatura))
                probabilidades.append(probabilidad)
                if delta < 0 or rng.random() < probabilidad:
                    modelo, actual = candidato, propuesto
                if actual < mejor:
                    mejor, optimo = actual, modelo.copy()
                evaluaciones += 1
                historial.append([k + 1, evaluaciones, actual, mejor, *modelo, *optimo])
    return _resultado("recocido_continuo", semilla, historial,
                      probabilidades=np.array(probabilidades),
                      parada="tolerancia" if tolerancia is not None and actual <= tolerancia else "itermax")
