from bs4 import BeautifulSoup
from unittest import TestCase

from ebird.pages.checklists import _get_location


class GetLocationTests(TestCase):
    """
    Tests for extracting the fields describing checklist location.

    """

    def setUp(self):
        self.content = None

    def get_keys(self):
        self.assertIsNotNone(self.content)
        soup = BeautifulSoup(self.content, "lxml")
        tag = soup.find('div', class_='rs-body')
        return sorted(_get_location(tag).keys())

    def test_correct_keys(self):
        """The location dict has the correct keys."""
        self.content = """
        <div class="rs-body">
            <h5 class="bd obs-loc">	
                Site, Subnational2, Subnational1, CO				
                <span class="btn-map">( <a href="http://maps.com/?q=1.0,2.0&ll=1.0,2.0">Map</a> )</span>
                <span class="btn-map">( <a href="/ebird/hotspot/L1234567">Hotspot</a> )</span>
            </h5>
        <div>
        """
        expected = ['country', 'identifier', 'lat', 'lon', 'name', 'subnational1', 'subnational2']
        self.assertListEqual(expected, self.get_keys())

    def test_optional_identifier(self):
        """The identifier is left out if the location is not a hotspot."""
        self.content = """
        <div class="rs-body">
            <h5 class="bd obs-loc">	
                Site, Subnational2, Subnational1, CO				
                <span class="btn-map">( <a href="http://maps.com/?&q=1.0,2.0&ll=1.0,2.0">Map</a> )</span>
            </h5>
        <div>
        """
        expected = ['country', 'lat', 'lon', 'name', 'subnational1', 'subnational2']
        self.assertListEqual(expected, self.get_keys())
