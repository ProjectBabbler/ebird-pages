from bs4 import BeautifulSoup
from unittest import TestCase

from ebird.pages.checklists import _get_longitude


class GetLongitudeTests(TestCase):
    """
    Tests for extracting the longitude of the location.

    """

    def setUp(self):
        self.template = """
        <div class="rs-body">
            <h5 class="bd obs-loc">	
                <span class="btn-map">( <a href="http://maps.com/?q=0.0,12.3456789&ll=0.0,%s">Map</a> )</span>
            </h5>
        <div>
        """
        self.value = None

    def parse(self):
        self.assertIsNotNone(self.value)
        content = self.template % self.value
        soup = BeautifulSoup(content, "lxml")
        tag = soup.find('div', class_='rs-body')
        return _get_longitude(tag)

    def test_longitude(self):
        """The longitude is returned as a float."""
        self.value = '12.3456789'
        self.assertEqual(12.3456789, self.parse())

    def test_negative(self):
        """Longitudes can be west of the prime meridian."""
        self.value = '-12.3456789'
        self.assertEqual(-12.3456789, self.parse())

    def test_query_parameter_order(self):
        """The longitude is returned even if the query parameter order changes."""
        self.template = """
        <div class="rs-body">
            <h5 class="bd obs-loc">	
                <span class="btn-map">( <a href="http://maps.com/?ll=0.0,%s&q=0.0,12.3456789">Map</a> )</span>
            </h5>
        <div>
        """
        self.value = '12.3456789'
        self.assertEqual(12.3456789, self.parse())

    def test_precision_changes(self):
        """Longitude may be expressed with any level of precision."""
        self.value = '10.0'
        self.assertEqual(10.0, self.parse())
