$( document ).ready(function() {
    // submenu
    $('.dropdown-menu a.dropdown-toggle').on('click', function(e) {
        if (!$(this).next().hasClass('show')) {
            $(this).parents('.dropdown-menu').first().find('.show').removeClass("show");
        }
        var $subMenu = $(this).next(".dropdown-menu");
        $subMenu.toggleClass('show');

        $(this).parents('li.nav-item.dropdown.show').on('hidden.bs.dropdown', function(e) {
            $('.dropdown-submenu .show').removeClass("show");
        });

        return false;
    });

    // light/dark scheme toggle script
    const colorSchemeButton = document.getElementById('aw-switch-colorScheme');
    const colorScheme = document.querySelector('meta[name="color-scheme"]');
    const colorSchemeVar = 'color-scheme';
    const colorSchemeLight = 'light';
    const colorSchemeDark = 'dark';
    const colorSchemeDefault = 'none';

    function getColorSchema(preference) {
        if (preference !== colorSchemeDefault) {
            return preference;
        } else if (matchMedia('(prefers-color-scheme: light)').matches) {
            return colorSchemeLight;
        } else {
            return colorSchemeDark;
        }
    }

    function setColorSchema(mode) {
        document.body.className = mode;
        colorScheme.content = mode;
        localStorage.setItem(colorSchemeVar, mode);
    }

    function switchColorScheme(mode) {
        if (mode === colorSchemeLight) {
            return colorSchemeDark;
        } else {
            return colorSchemeLight;
        }
    }

    let userPreference = localStorage.getItem(colorSchemeVar) || colorSchemeDefault;
    setColorSchema(getColorSchema(userPreference));

    if (colorSchemeButton != null) {
        colorSchemeButton.onclick = function() {
            userPreference = switchColorScheme(userPreference);
            setColorSchema(userPreference);
        };
    }
});
