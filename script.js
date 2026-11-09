(() => {
    'use strict';

    document.documentElement.classList.add('js');
    const header = document.querySelector('.site-header');
    const menu = document.querySelector('.site-nav');
    const toggle = document.querySelector('.site-nav__toggle');
    const mobile = window.matchMedia('(max-width: 900px)');
    const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');

    const updateHeader = () => {
        if (header) document.body.style.setProperty('--header-height', `${Math.ceil(header.getBoundingClientRect().height)}px`);
    };
    const closeMenu = () => {
        menu?.classList.remove('is-open');
        toggle?.setAttribute('aria-expanded', 'false');
        toggle?.setAttribute('aria-label', 'Abrir menú de navegación');
        updateHeader();
    };

    toggle?.addEventListener('click', () => {
        const open = toggle.getAttribute('aria-expanded') !== 'true';
        menu?.classList.toggle('is-open', open);
        toggle.setAttribute('aria-expanded', String(open));
        toggle.setAttribute('aria-label', open ? 'Cerrar menú de navegación' : 'Abrir menú de navegación');
        updateHeader();
    });
    document.addEventListener('keydown', (event) => {
        if (event.key === 'Escape' && menu?.classList.contains('is-open')) {
            closeMenu();
            toggle?.focus();
        }
    });
    document.addEventListener('click', (event) => {
        if (!event.target.closest('.site-header')) closeMenu();
        const link = event.target.closest('a[href^="#"]');
        if (!link) return;
        const target = document.getElementById(link.hash.slice(1));
        if (!target) return;
        event.preventDefault();
        closeMenu();
        requestAnimationFrame(() => {
            updateHeader();
            if (!target.hasAttribute('tabindex')) target.tabIndex = -1;
            target.scrollIntoView({ behavior: reducedMotion.matches ? 'instant' : 'smooth', block: 'start' });
            target.focus({ preventScroll: true });
            if (location.hash !== link.hash) history.pushState(null, '', link.hash);
        });
    });
    mobile.addEventListener('change', () => { if (!mobile.matches) closeMenu(); });
    if ('ResizeObserver' in window && header) new ResizeObserver(updateHeader).observe(header);
    window.addEventListener('resize', updateHeader);
    updateHeader();

    const navLinks = [...document.querySelectorAll('.site-nav__link')];
    if ('IntersectionObserver' in window) {
        const observer = new IntersectionObserver((entries) => {
            const visible = entries.filter(e => e.isIntersecting).sort((a, b) => b.intersectionRatio - a.intersectionRatio)[0];
            if (!visible) return;
            navLinks.forEach(link => {
                const active = link.hash === `#${visible.target.id}`;
                link.classList.toggle('is-active', active);
                if (active) link.setAttribute('aria-current', 'location');
                else link.removeAttribute('aria-current');
            });
        }, { rootMargin: '-15% 0px -55% 0px', threshold: [0, .2, .5] });
        document.querySelectorAll('section[id]').forEach(section => observer.observe(section));
    }

})();
