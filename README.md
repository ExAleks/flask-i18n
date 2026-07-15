# flask-i18n

Lightweight i18n module for Flask with JSON translations, session-based language switcher, and Jinja2 integration.

## Features

- JSON-based translations (nested keys with dot notation)
- Session-based language persistence
- GET parameter language switcher (`?lang=en`)
- Automatic Jinja2 `t()` function injection
- Zero dependencies beyond Flask

## Install

Just copy the `i18n/` folder into your project.

## Usage

```python
from flask import Flask
from i18n import I18n
from i18n.flask_integration import I18nExtension

app = Flask(__name__)
app.secret_key = 'your-secret'

i18n = I18n(default='ru')
i18n.load_dir('i18n/translations')
I18nExtension(i18n)(app)
```

### In templates

```html
<h1>{{ t('nav.home') }}</h1>
<p>{{ t('auth.welcome', name=user.name) }}</p>
```

### In Python

```python
i18n.t('nav.home')  # -> "Главная"
i18n.t('auth.greeting', name='Alex')  # -> "Привет, Alex!"
```

### Language switcher

Add to your navbar:

```html
{% for lang in langs %}
  {% if lang != current_lang %}
    <a href="?lang={{ lang }}">{{ lang|upper }}</a>
  {% endif %}
{% endfor %}
```

### Translation files

```
i18n/translations/ru.json
i18n/translations/en.json
```

Format:

```json
{
    "_lang": "ru",
    "nav": {
        "home": "Главная",
        "about": "О нас"
    },
    "auth": {
        "welcome": "Привет, {name}!"
    }
}
```

## License

MIT
