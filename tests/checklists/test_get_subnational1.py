from bs4 import BeautifulSoup
from unittest import TestCase

from ebird.pages.checklists import _get_subnational1


class GetSubnational1Tests(TestCase):
    """
    Tests for extracting the region (subnational1) from the checklist location.

    """
    def setUp(self):
        self.template = """
        <div class="rs-body">
            <h5 class="bd obs-loc">%s</h5>
        <div>
        """
        self.value = None

    def parse(self):
        self.assertIsNotNone(self.value)
        content = self.template % self.value
        soup = BeautifulSoup(content, "lxml")
        tag = soup.find('div', class_='rs-body')
        return _get_subnational1(tag)

    def test_region(self):
        """The name of the region is returned as a string."""
        self.value = 'Site, Subnational2, Subnational1, CO'
        self.assertEqual('Subnational1', self.parse())

    def test_with_hotspot_link(self):
        """The name of region is returned even if there is a link to the hotspot."""
        self.value = """
            Site, Subnational2, Subnational1, CO				
            <span class="btn-map">( <a href="/ebird/hotspot/L1234567">Hotspot</a> )</span>
        """
        self.assertEqual('Subnational1', self.parse())

    def test_commas(self):
        """Region is returned although sites have extra commas."""
        self.value = 'Site name, with comma, Subnational2, Subnational1, CO'
        self.assertEqual('Subnational1', self.parse())

    def test_extra_whitespace(self):
        """Extra whitespace is removed from the region."""
        self.value = 'Site, Subnational2,\n Subnational1 \n, CO'
        self.assertEqual('Subnational1', self.parse())
