/* El selector cambia únicamente las vistas y los enlaces de las figuras. */
(() => {
    'use strict';

    const selector = document.getElementById('tema-figuras');
    const gallery = document.getElementById('galeria-figuras');
    const status = document.getElementById('estado-figuras');
    if (!selector || !gallery || !status) return;

    const setTheme = (theme) => {
        if (theme !== 'oscuro' && theme !== 'claro') return;
        gallery.querySelectorAll('[data-figure]').forEach((figure) => {
            const name = figure.dataset.figure;
            const image = figure.querySelector('img');
            image.srcset = `web/${theme}/${name}-640.webp 640w, web/${theme}/${name}-1280.webp 1280w`;
            image.src = `web/${theme}/${name}-1280.webp`;
            figure.querySelectorAll('[data-format]').forEach((link) => {
                link.href = `Figuras/${theme}/${name}.${link.dataset.format}`;
            });
        });
        gallery.dataset.theme = theme;
        status.textContent = `Figuras en tema ${theme}. El contenido numérico es idéntico en ambos temas.`;
    };

    selector.addEventListener('change', (event) => {
        if (event.target.matches('input[name="tema-figuras"]')) setTheme(event.target.value);
    });
    // Sin JavaScript se mantienen las cuatro vistas oscuras y los enlaces alternativos.
    setTheme(selector.querySelector('input:checked').value);
    selector.hidden = false;
})();
