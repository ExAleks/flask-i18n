import json
import os
import tempfile
import unittest

from flask import Flask, render_template_string

from __init__ import I18n
from flask_integration import I18nExtension

BASE = os.path.dirname(os.path.abspath(__file__))
TRANSLATIONS = os.path.join(BASE, "translations")


def load_i18n(default="ru"):
    i18n = I18n(default=default)
    i18n.load_dir(TRANSLATIONS)
    return i18n


class I18nTests(unittest.TestCase):
    def test_loads_every_translation_file(self):
        self.assertEqual(sorted(load_i18n().langs()), ["en", "ru"])

    def test_translates_nested_key(self):
        i18n = load_i18n(default="en")
        i18n.set_lang("en")
        self.assertEqual(i18n.t("nav.dashboard"), "Dashboard")

    def test_switches_language(self):
        i18n = load_i18n()
        i18n.set_lang("en")
        self.assertEqual(i18n.t("nav.dashboard"), "Dashboard")
        i18n.set_lang("ru")
        self.assertNotEqual(i18n.t("nav.dashboard"), "Dashboard")

    def test_unknown_language_falls_back_to_default(self):
        i18n = load_i18n()
        expected = i18n.t("nav.dashboard")
        i18n.set_lang("zz")
        self.assertEqual(i18n.t("nav.dashboard"), expected)

    def test_missing_key_returns_key(self):
        self.assertEqual(load_i18n().t("does.not.exist"), "does.not.exist")

    def test_falls_back_to_default_language(self):
        with tempfile.TemporaryDirectory() as tmp:
            with open(os.path.join(tmp, "en.json"), "w", encoding="utf-8") as f:
                json.dump({"_lang": "en", "only": {"en": "english"}}, f)
            with open(os.path.join(tmp, "ru.json"), "w", encoding="utf-8") as f:
                json.dump({"_lang": "ru", "only": {"ru": "russian"}}, f)
            i18n = I18n(default="en")
            i18n.load_dir(tmp)
            i18n.set_lang("ru")
            self.assertEqual(i18n.t("only.ru"), "russian")
            self.assertEqual(i18n.t("only.en"), "english")

    def test_formats_parameters(self):
        with tempfile.TemporaryDirectory() as tmp:
            with open(os.path.join(tmp, "ru.json"), "w", encoding="utf-8") as f:
                json.dump({"_lang": "ru", "hello": "Привет, {name}!"}, f)
            i18n = I18n(default="ru")
            i18n.load_dir(tmp)
            self.assertEqual(i18n.t("hello", name="мир"), "Привет, мир!")

    def test_missing_parameter_returns_raw_value(self):
        with tempfile.TemporaryDirectory() as tmp:
            with open(os.path.join(tmp, "ru.json"), "w", encoding="utf-8") as f:
                json.dump({"_lang": "ru", "hello": "Привет, {name}!"}, f)
            i18n = I18n(default="ru")
            i18n.load_dir(tmp)
            self.assertEqual(i18n.t("hello"), "Привет, {name}!")

    def test_load_dir_on_missing_directory_is_a_noop(self):
        i18n = I18n(default="ru")
        i18n.load_dir(os.path.join(BASE, "no-such-dir"))
        self.assertEqual(i18n.langs(), [])


class FlaskExtensionTests(unittest.TestCase):
    def make_app(self):
        app = Flask(__name__)
        app.secret_key = "test"
        i18n = load_i18n(default="en")
        I18nExtension(i18n)(app)

        @app.route("/")
        def index():
            return render_template_string("{{ t('nav.dashboard') }}")

        return app

    def test_translates_in_template(self):
        client = self.make_app().test_client()
        self.assertEqual(client.get("/").get_data(as_text=True), "Dashboard")

    def test_switches_language_via_query_string(self):
        client = self.make_app().test_client()
        self.assertEqual(client.get("/?lang=en").get_data(as_text=True), "Dashboard")
        russian = client.get("/?lang=ru").get_data(as_text=True)
        self.assertNotEqual(russian, "Dashboard")
        self.assertEqual(client.get("/").get_data(as_text=True), russian)

    def test_ignores_unknown_language(self):
        client = self.make_app().test_client()
        client.get("/?lang=zz")
        self.assertEqual(client.get("/").get_data(as_text=True), "Dashboard")


if __name__ == "__main__":
    unittest.main()
