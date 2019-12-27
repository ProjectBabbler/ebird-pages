from bs4 import BeautifulSoup
from unittest import TestCase

from ebird.pages.checklists import _get_latitude


class GetLatitudeTests(TestCase):
    """
    Tests for extracting the latitude of the location.

    """
    def setUp(self):
        self.template = """
        <div class="rs-body">
            <h5 class="bd obs-loc">	
                <span class="btn-map">( <a href="http://maps.com/?q=12.3456789,0.0&ll=%s,0.0">Map</a> )</span>
            </h5>
        <div>
        """
        self.value = None

    def parse(self):
        self.assertIsNotNone(self.value)
        content = self.template % self.value
        soup = BeautifulSoup(content, "lxml")
        tag = soup.find('div', class_='rs-body')
        return _get_latitude(tag)

    def test_latitude(self):
        """The latitude is returned as a float."""
        self.value = '12.3456789'
        self.assertEqual(12.3456789, self.parse())

    def test_negative(self):
        """Latitudes can be below the Equator are supported."""
        self.value = '-12.3456789'
        self.assertEqual(-12.3456789, self.parse())

    def test_query_parameter_order(self):
        """The latitude is returned even ff the query parameter order changes."""
        self.template = """
        <div class="rs-body">
            <h5 class="bd obs-loc">	
                <span class="btn-map">( <a href="http://maps.com/?ll=%s,0.0&q=-12.3456789,0.0">Map</a> )</span>
            </h5>
        <div>
        """
        self.value = '12.3456789'
        self.assertEqual(12.3456789, self.parse())

    def test_precision_changes(self):
        """The latitude may be presented in any precision."""
        self.value = '10.0'
        self.assertEqual(10.0, self.parse())
