"""Contrato de datos y navegación real de Streamlit con las tablas publicadas."""
import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dashboard.data import filter_segments, previous_same_cycle, read_tables
from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]


class DataContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = read_tables()

    def test_published_profile_boundaries(self):
        segments = self.data["segments"].set_index(["sexo_codigo", "edad"])
        # La excepción femenina de 18 años y los límites diferentes por sexo deben preservarse.
        for key, profile in [((1, 18), 1), ((0, 18), 2), ((0, 36), 3),
                             ((0, 37), 2), ((0, 93), 4), ((1, 90), 4)]:
            self.assertEqual(segments.loc[key, "perfil"], profile)

    def test_filters_can_be_empty_without_inventing_totals(self):
        d = self.data["segments"]
        self.assertTrue(filter_segments(d, [], ["Hombres"], (18, 99)).empty)
        self.assertTrue(filter_segments(d, [4], ["Mujeres"], (18, 30)).empty)
        selected = filter_segments(d, [3], ["Hombres"], (20, 36))
        self.assertEqual(len(selected), 17)

    def test_cycle_comparison(self):
        self.assertEqual(previous_same_cycle(2024), 2018)
        self.assertEqual(previous_same_cycle(2021), 2015)
        self.assertIsNone(previous_same_cycle(2012))

    def test_territory_is_2024_and_share_is_not_turnout(self):
        t = self.data["territory"]
        self.assertEqual(set(t.anio), {2024})
        self.assertEqual(len(t[(t.corte == "region_x_tipo") & (t.perfil == 1)]), 9)
        current = self.data["history"].query('anio == 2024').set_index('perfil')
        self.assertAlmostEqual(current.pct_lista_2024.sum(), 100)
        self.assertEqual(current.loc[1, "pct_lista_2024"], 41.0)
        self.assertEqual(current.loc[1, "participacion_pct"], 70.6)


class NavigationTests(unittest.TestCase):
    def test_pages_filters_and_empty_states(self):
        app = AppTest.from_file(str(ROOT / "app.py"), default_timeout=40).run()
        self.assertFalse(app.exception, str(app.exception))
        self.assertIn("La participación", app.title[0].value)
        for page in ["Sexo y edad", "Evolución", "Territorio", "Metodología"]:
            app.sidebar.radio(key="section").set_value(page).run()
            self.assertFalse(app.exception, f"{page}: {app.exception}")
        app.sidebar.radio(key="section").set_value("Sexo y edad").run()
        app.multiselect(key="sexes").set_value([]).run()
        self.assertFalse(app.exception, str(app.exception))
        self.assertTrue(app.info)
        app.multiselect(key="sexes").set_value(["Mujeres"]).run()
        app.slider(key="ages").set_value((90, 99)).run()
        self.assertFalse(app.exception, str(app.exception))
        app.sidebar.radio(key="section").set_value("Territorio").run()
        app.radio(key="territorial_cut").set_value("Región y tipo de sección").run()
        app.multiselect(key="groups_region_x_tipo").set_value([]).run()
        self.assertTrue(app.info)
        self.assertFalse(app.exception, str(app.exception))
        app.sidebar.radio(key="section").set_value("Panorama").run()
        app.sidebar.multiselect(key="profiles").set_value([]).run()
        self.assertTrue(app.info)
        app.sidebar.radio(key="theme").set_value("Oscuro").run()
        self.assertFalse(app.exception, str(app.exception))


if __name__ == "__main__":
    unittest.main()
