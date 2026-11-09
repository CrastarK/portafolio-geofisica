import csv
import json
import unittest
from unittest.mock import patch
import numpy as np
import algoritmos as alg
from problemas import CARPETA, costo, malla, problema_polinomial, hashes_originales
from ejecutar import SEMILLAS, estudiar_polinomio
from reproduccion_original import (limite_modelo25, mutacion_original,
                                   evolucion_genetica_original, inicializar_genetico_original,
                                   reproducir_superficie)


class PruebasNumericas(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.resumen = json.loads((CARPETA / "resultados/resumen.json").read_text(encoding="utf-8"))

    def test_originales_intactos(self):
        self.assertEqual(hashes_originales(), self.resumen["originales_sha256"])
        self.assertEqual(len(hashes_originales()), 5)

    def test_funcion_compartida(self):
        self.assertAlmostEqual(float(costo(0., 0.)), 11 - 4 / np.e, places=13)
        x = np.array([-.4, -1.6, 2.1])
        y = np.array([-1., .6, -.7])
        np.testing.assert_allclose(costo(x, y), [costo(a, b) for a, b in zip(x, y)], atol=1e-13)
        with self.assertRaises(ValueError):
            costo(0, 0, "inexistente")

    def test_diferencia_entre_superficies(self):
        x, y = np.meshgrid(np.linspace(-3, 3, 13), np.linspace(-3, 3, 13))
        b = (1 - x)**2 * np.exp(-2 * x**2 - (y + 1)**2)
        diferencia = costo(x, y) - costo(x, y, "recristalizacion")
        np.testing.assert_allclose(diferencia, 10 - 12 * b, atol=1e-13)
        self.assertGreater(np.ptp(diferencia), 1)

    def test_referencia_exhaustiva(self):
        referencia = malla()
        self.assertEqual(referencia["evaluaciones"], 3721)
        np.testing.assert_allclose(referencia["modelo"], [-.4, -1.], atol=1e-14)
        self.assertEqual(referencia["costo"], float(referencia["valores"].min()))
        for j, y in enumerate(referencia["eje"]):
            for i, x in enumerate(referencia["eje"]):
                self.assertAlmostEqual(float(costo(x, y)), referencia["valores"][j, i], places=12)
        self.assertLess(malla(301)["costo"], referencia["costo"])

    def test_codificacion_todos_los_indices(self):
        x, y = np.meshgrid(np.arange(61), np.arange(61))
        indices = np.column_stack([x.ravel(), y.ravel()])
        for bits in (6, 10):
            poblacion = alg.codificar(indices, bits=bits)
            np.testing.assert_array_equal(alg.decodificar(poblacion, bits), indices)
            self.assertEqual(poblacion.shape, (3721, 2 * bits))

    def test_indices_invalidos(self):
        for indices in (np.array([[-1, 2]]), np.array([[61, 0]]), np.array([[1.5, 2]]), np.array([1, 2])):
            with self.subTest(indices=indices), self.assertRaises(ValueError):
                alg.codificar(indices)
        for bits in (0, 5, 31, 6.5):
            with self.subTest(bits=bits), self.assertRaises(ValueError):
                alg.codificar(np.array([[0, 0]]), bits=bits)
        with self.assertRaises(ValueError):
            alg.decodificar(np.full((2, 12), 2))

    def test_reparacion_y_recodificacion(self):
        for n, bits in ((61, 6), (61, 10), (17, 6)):
            poblacion = np.vstack([np.zeros((12, 2 * bits), dtype=np.uint8), np.ones((12, 2 * bits), dtype=np.uint8)])
            reparada, cantidad = alg.reparar(poblacion, np.random.default_rng(5), n, bits)
            indices = alg.decodificar(reparada, bits)
            self.assertEqual(cantidad, 48)
            self.assertTrue(((indices >= 0) & (indices < n)).all())
            np.testing.assert_array_equal(alg.codificar(indices, n, bits), reparada)

    def test_mutacion_invierte_ambos_bits(self):
        poblacion = np.array([[0, 1, 0, 1], [1, 0, 1, 0]], dtype=np.uint8)
        np.testing.assert_array_equal(alg.mutar(poblacion, 1, np.random.default_rng(5)), 1 - poblacion)
        np.testing.assert_array_equal(alg.mutar(poblacion, 0, np.random.default_rng(5)), poblacion)
        with self.assertRaises(ValueError):
            alg.mutar(poblacion, -1, np.random.default_rng(5))

    def test_cruce_un_punto(self):
        padre, madre = np.zeros(12, dtype=np.uint8), np.ones(12, dtype=np.uint8)
        for corte in range(1, 12):
            hijo, hija = alg.cruzar(padre, madre, corte)
            np.testing.assert_array_equal(hijo, np.r_[padre[:corte], madre[corte:]])
            np.testing.assert_array_equal(hija, 1 - hijo)
        for corte in (0, 12):
            with self.assertRaises(ValueError):
                alg.cruzar(padre, madre, corte)

    def test_metropolis_estable(self):
        self.assertTrue(alg.aceptar(-1, 1, .99))
        self.assertTrue(alg.aceptar(0, 1, .99))
        self.assertTrue(alg.aceptar(1, 1, .1))
        self.assertFalse(alg.aceptar(1, 1, .9))
        self.assertFalse(alg.aceptar(1e6, 1e-9, .1))
        for delta, t, u in ((np.nan, 1, .5), (0, 0, .5), (0, np.inf, .5), (0, 1, 1)):
            with self.assertRaises(ValueError):
                alg.aceptar(delta, t, u)

    def test_presupuesto_real_incluye_duplicados(self):
        funcion = alg.costo
        for metodo in ("local", "recocido", "genetico"):
            contador = [0]

            def contar(x, y):
                contador[0] += np.asarray(x).size
                return funcion(x, y)

            with patch.object(alg, "costo", contar):
                resultado = alg.genetico(7, presupuesto=101) if metodo == "genetico" else alg.explorar_malla(metodo, 7, presupuesto=101)
            self.assertEqual(contador[0], 101)
            self.assertEqual(resultado["evaluaciones"], 101)

    def test_elitismo_y_limites(self):
        for bits in (6, 10):
            r = alg.genetico(19, presupuesto=501, bits=bits)
            self.assertTrue((np.diff(r["historial"][:, 3]) <= 0).all())
            self.assertTrue((np.abs(r["historial"][:, 4:]) <= 3).all())
            self.assertEqual(r["evaluaciones"], 501)
        with self.assertRaises(ValueError):
            alg.genetico(individuos=3)

    def test_reproducibilidad_30_experimentos_conservados(self):
        self.assertEqual(SEMILLAS, self.resumen["semillas"])
        self.assertEqual(self.resumen["presupuesto_por_algoritmo"], 6000)
        for semilla in SEMILLAS:
            for metodo in ("local", "recocido", "genetico"):
                with self.subTest(semilla=semilla, metodo=metodo):
                    r = alg.genetico(semilla) if metodo == "genetico" else alg.explorar_malla(metodo, semilla)
                    guardado = np.loadtxt(CARPETA / "resultados/historiales" / f"{metodo}_{semilla}.csv", delimiter=",", skiprows=1)
                    np.testing.assert_array_equal(r["historial"], guardado)
                    self.assertEqual(r["evaluaciones"], 6000)
                    self.assertTrue((np.diff(guardado[:, 3]) <= 0).all())
                    self.assertTrue((np.abs(guardado[:, 4:]) <= 3).all())
                    np.testing.assert_allclose(costo(guardado[:, 4], guardado[:, 5]), guardado[:, 2], rtol=0, atol=1e-12)
                    np.testing.assert_allclose(costo(guardado[:, 6], guardado[:, 7]), guardado[:, 3], rtol=0, atol=1e-12)
                    coordenadas = (guardado[:, 4:] + 3) * 10
                    np.testing.assert_allclose(coordenadas, np.rint(coordenadas), rtol=0, atol=1e-12)

    def test_resumen_y_fallos_no_ocultos(self):
        with (CARPETA / "resultados/comparacion.csv").open(encoding="utf-8") as archivo:
            filas = list(csv.DictReader(archivo))
        self.assertEqual(len(filas), 30)
        referencia = malla()["costo"]
        for metodo in ("local", "recocido", "genetico"):
            grupo = [f for f in filas if f["metodo"] == metodo]
            aciertos = sum(float(f["costo"]) <= referencia + 1e-12 for f in grupo)
            self.assertEqual(aciertos, self.resumen["resultados"][metodo]["aciertos_malla"])
            self.assertEqual(set(int(f["evaluaciones"]) for f in grupo), {6000})
            self.assertEqual(float(np.median([float(f["costo"]) for f in grupo])), self.resumen["resultados"][metodo]["costo_mediano"])
            self.assertTrue(all(float(f["brecha_malla"]) >= -1e-12 for f in grupo))
        self.assertEqual([self.resumen["resultados"][m]["aciertos_malla"] for m in ("local", "recocido", "genetico")], [0, 5, 9])

    def test_reproducciones_continuas(self):
        for archivo in ("modelo22", "modelo25"):
            r = reproducir_superficie(archivo)
            guardado = np.loadtxt(CARPETA / "resultados/historiales" / f"{archivo}_reproduccion_python.csv", delimiter=",", skiprows=1)
            np.testing.assert_array_equal(r["historial"], guardado)
        self.assertEqual(limite_modelo25(-3.2), 3)
        self.assertEqual(np.clip(-3.2, -3, 3), -3)

    def test_genetico_original_incompleto_explicito(self):
        poblacion, indices, valores = inicializar_genetico_original()
        self.assertEqual(poblacion.shape, (10, 20))
        np.testing.assert_array_equal(alg.decodificar(poblacion, 10), indices)
        self.assertTrue(np.isfinite(valores).all())
        ceros = np.zeros((10, 20), dtype=np.uint8)
        np.testing.assert_array_equal(mutacion_original(ceros), ceros)
        with self.assertRaisesRegex(NotImplementedError, "vale"):
            evolucion_genetica_original()

    def test_polinomio_y_minimos_cuadrados(self):
        x, g, verdadero, datos = problema_polinomial()
        self.assertEqual(g.shape, (201, 4))
        self.assertEqual(x[100], 0)
        np.testing.assert_array_equal(datos, g @ verdadero)
        modelo, _, rango, _ = np.linalg.lstsq(g, datos, rcond=None)
        self.assertEqual(rango, 4)
        np.testing.assert_allclose(modelo, verdadero, rtol=0, atol=1e-9)
        self.assertLess(np.linalg.norm(datos - g @ modelo), 1e-8)
        self.assertGreater(np.max(verdadero), 3)
        self.assertEqual(abs(datos[100] - 3), 497)

    def test_reproducibilidad_polinomio(self):
        r = estudiar_polinomio()
        guardado = np.load(CARPETA / "resultados/polinomio.npz")
        for nombre, valor in (("x", r["x"]), ("g", r["g"]), ("datos", r["datos"]),
                              ("minimos_cuadrados", r["minimos_cuadrados"]),
                              ("original", r["original"]["modelo"]), ("escalado", r["modelo_escalado"])):
            np.testing.assert_array_equal(valor, guardado[nombre])
        for nombre, resultado in (("polinomio_limites_originales", r["original"]), ("polinomio_escalado", r["escalado"])):
            h = np.loadtxt(CARPETA / "resultados/historiales" / f"{nombre}.csv", delimiter=",", skiprows=1)
            np.testing.assert_array_equal(h, resultado["historial"])
            self.assertTrue((np.diff(h[:, 3]) <= 0).all())
        self.assertTrue((np.abs(r["original"]["modelo"]) <= 3).all())
        self.assertTrue((np.abs(r["escalado"]["modelo"]) <= 2).all())
        self.assertGreater(r["original"]["mejor_costo"], 497)
        error = np.linalg.norm(r["datos"] - r["g"] @ r["modelo_escalado"])
        self.assertAlmostEqual(error, self.resumen["polinomio"]["error_escalado"], places=12)
        self.assertGreater(error, 1)
        self.assertEqual(r["escalado"]["evaluaciones"], 48001)
        self.assertEqual(r["original"]["evaluaciones"], 6401)

    def test_parametros_continuos_invalidos(self):
        funcion = lambda m: float(m @ m)
        with self.assertRaises(ValueError):
            alg.recocido_continuo(funcion, [0, 0], [1, np.nan], [[-3, 3]] * 2)
        with self.assertRaises(ValueError):
            alg.recocido_continuo(lambda m: np.nan, [0], [1], [[-3, 3]])
        with self.assertRaises(ValueError):
            alg.recocido_continuo(funcion, [4], [1], [[-3, 3]])


if __name__ == "__main__":
    unittest.main()
