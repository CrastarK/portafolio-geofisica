from pathlib import Path
import hashlib
import numpy as np

CARPETA = Path(__file__).resolve().parents[1]


def costo(m1, m2, variante="comun"):
    m1, m2 = np.asarray(m1), np.asarray(m2)
    z1 = 6 * (m1 / 6 - m1**3 - m2**5) * np.exp(-(m1 - .5)**2 - m2**2)
    z2 = 2 * np.exp(-(m1 + 1)**2 - m2**2)
    b = (1 - m1)**2 * np.exp(-2 * m1**2 - (m2 + 1)**2)
    z4 = .5 * np.sin(3 * m1) + np.cos(2.5 * m2)
    if variante == "comun":
        return z1 + z2 - 6 * b + z4 + 10
    if variante == "recristalizacion":
        return z1 + z2 + 6 * b + z4
    raise ValueError("Variante de costo desconocida.")


def malla(n=61, variante="comun"):
    if not isinstance(n, int) or n < 2:
        raise ValueError("Se necesitan al menos dos nodos por eje.")
    eje = np.linspace(-3, 3, n)
    m1, m2 = np.meshgrid(eje, eje)
    valores = costo(m1, m2, variante)
    fila, columna = np.unravel_index(np.argmin(valores), valores.shape)
    return dict(eje=eje, m1=m1, m2=m2, valores=valores,
                indice=[int(columna), int(fila)],
                modelo=[float(eje[columna]), float(eje[fila])],
                costo=float(valores[fila, columna]), evaluaciones=n * n)


def problema_polinomial():
    x = np.linspace(-10, 10, 201)
    g = np.column_stack([x**k for k in range(4)])
    verdadero = np.array([500., 50., 5., .5])
    return x, g, verdadero, g @ verdadero


def hashes_originales():
    return {f.name: hashlib.sha256(f.read_bytes()).hexdigest()
            for f in sorted((CARPETA / "matlab_original").glob("*.m"))}
