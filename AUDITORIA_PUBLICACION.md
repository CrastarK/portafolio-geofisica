# Auditor?a de publicaci?n ? 9 de noviembre de 2026

Estado: preparado para una subida selectiva y revisi?n final de la lista. No se inicializ? Git en este directorio, ni se hizo commit, push o publicaci?n.

## Alcance y Git

Se inspeccionaron los 196 archivos originales (48,59 MiB), incluidos archivos ocultos, fuentes, documentos, datos, resultados, im?genes y el ?ndice del respaldo ZIP. No existe `.git` en el directorio ni en sus subdirectorios; `git rev-parse` confirma que no pertenece a un repositorio. No hay historial local disponible para revisar. Esto no permite certificar el historial de un repositorio remoto que todav?a no se ha elegido.

No se detectaron claves privadas, tokens con patrones reconocibles, asignaciones de credenciales, rutas personales absolutas, hojas Excel ni archivos de datos privados. El respaldo contiene figuras anteriores y un reporte, y se excluye sin borrarlo. La b?squeda de patrones es preventiva y no garantiza detectar cualquier secreto imaginable; no se realiz? una revisi?n forense del contenido binario de im?genes.

## Lista exacta para subir

`PUBLICACION_ARCHIVOS.json` contiene las listas completas `publicables` (186 archivos) y `excluir` (14 archivos presentes). Conservar las rutas y may?sculas exactamente. La lista incluye este informe y el propio manifiesto; no usar una selecci?n manual que omita las exclusiones.

Se incluyen los tres archivos web principales, `.gitignore`, `.nojekyll` y los tres proyectos: p?ginas de detalle y sus recursos, miniaturas WebP, PNG/SVG originales, fuentes Python/MATLAB, README, datos sint?ticos, resultados num?ricos y validaciones cient?ficas. Se conservan los tests num?ricos porque ayudan a reproducir y verificar los resultados.

Se excluyen nueve archivos de `__pycache__`, los tres `validacion_web.json`, `Proyectos/Metodos_Inversos/comprobacion_windows.json` y `Proyectos/Petrofisica_ELAN/Figuras/archivo_previo.zip`. Los reportes web y de entorno son evidencia local de integraci?n, innecesaria para servir o reproducir el modelo. No se borr? ninguno.

El nuevo `.gitignore` tambi?n previene a?adir entornos, cach?s, temporales, configuraci?n local de editores, archivos de credenciales, hojas de c?lculo y carpetas privadas habituales. No sustituye revisar futuros archivos, y no proteger?a archivos ya registrados en un futuro repositorio.

## Material cient?fico

- Petrofisica_ELAN: matriz y escenarios definidos en c?digo; modelo lineal simplificado de inspiraci?n ELAN. Sin registros reales ni validaci?n del software comercial.
- Registros_Sinteticos_Pozo: generador con semilla y relaciones matem?ticas propias, CSV y metadatos sint?ticos. No hay dependencia del Excel privado ni entradas externas al generador.
- Metodos_Inversos: funciones de prueba y problema polinomial sint?tico. Se conservan los cinco MATLAB acad?micos, sus correcciones documentadas y los experimentos no convergentes. No se presentan como inversi?n geof?sica con observaciones reales.

El archivo m?s grande, `resultados/historiales/polinomio_escalado.csv` de M?todos Inversos, ocupa 9,80 MiB y documenta convergencia; tiene utilidad p?blica y se conserva. No se encontraron archivos de m?s de 10 MiB. Los hashes SHA-256 de los 196 archivos iniciales coinciden despu?s de la auditor?a: p?ginas, c?lculos y figuras permanecen intactos. No se ejecutaron nuevamente los experimentos cient?ficos.

## Pruebas

- Cuatro p?ginas HTML: rutas relativas, fragmentos, nombres y may?sculas correctos.
- Servidor HTTP local simulando `/portfolio/`: 134 recursos ?nicos respondieron 200; incluye las miniaturas de ambos temas.
- Chrome: navegaci?n a los tres proyectos y regreso, men?s y teclado correctos; sin errores JavaScript. Selectores oscuro/claro y enlaces PNG/SVG sincronizados en los tres proyectos.
- Sin desbordamiento horizontal entre 320 y 1365 px en los anchos ensayados; alternativas sin JavaScript disponibles.
- GitHub `https://github.com/CrastarK`: HTTP 200. LinkedIn `https://www.linkedin.com/in/lemuel-fuentes-0aa321261/`: HTTP 999, restricci?n de acceso automatizado; verificar manualmente antes de publicar.
- Sin correo ni WhatsApp no confirmados y sin formulario que simule enviar mensajes.
- Reglas de exclusi?n comprobadas mediante `git check-ignore` en un repositorio temporal externo al portafolio.

## Procedimiento recomendado (no ejecutado)

1. Revisar `PUBLICACION_ARCHIVOS.json`, especialmente `excluir`, y confirmar LinkedIn en un navegador normal. Elegir si se desea agregar una licencia: actualmente no hay una licencia expl?cita de reutilizaci?n.
2. Crear m?s adelante un repositorio p?blico vac?o en la cuenta CrastarK. Para una URL principal de usuario, usar `crastark.github.io`; para un sitio de proyecto puede elegirse otro nombre.
3. Inicializar Git localmente solo cuando se autorice. A?adir exclusivamente los archivos del manifiesto con sus rutas relativas. Revisar `git status --short` y `git diff --cached --stat` antes del primer commit; comprobar que no aparece ninguno de `excluir`. Si se reutiliza un remoto existente, revisar primero su historial completo.
4. Tras autorizar commit y push, subir a `main` y configurar Settings ? Pages ? Deploy from a branch ? main ? /(root). `.nojekyll` permite servir directamente este sitio est?tico.
5. Comprobar la URL publicada, las cuatro p?ginas, im?genes, descargas, temas y perfiles. Python y MATLAB se comparten como fuentes; GitHub Pages no los ejecuta.

Referencia: [Crear un sitio GitHub Pages ? documentaci?n oficial](https://docs.github.com/en/pages/getting-started-with-github-pages/creating-a-github-pages-site).

Archivos a?adidos por esta auditor?a: `.gitignore`, `.nojekyll`, `PUBLICACION_ARCHIVOS.json` y `AUDITORIA_PUBLICACION.md`. Ning?n archivo existente fue modificado o eliminado.
