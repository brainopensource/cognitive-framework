import unittest

import app


class GreenfieldApi(unittest.TestCase):
    def test_it_exposes_a_health_route(self):
        self.assertIn("/health", app.routes())

    def test_the_index_page_is_html(self):
        page = app.render_index()
        self.assertIn("<!doctype html>", page.lower())
