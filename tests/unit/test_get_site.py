from bs4 import BeautifulSoup
from unittest import TestCase

from ebird.pages.checklists import _get_site


class ParseSiteTests(TestCase):
    """
    Tests for extracting the name of the site from the location.

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
        return _get_site(tag)

    def test_site(self):
        """The name of the site is returned as a string."""
        self.value = 'Site name, Subnational2, Subnational1, CO'
        self.assertEqual('Site name', self.parse())

    def test_with_hotspot_link(self):
        """The name of site is returned even if there is a link to the hotspot."""
        self.value = """
            Site name, Subnational2, Subnational1, CO				
            <span class="btn-map">( <a href="/ebird/hotspot/L1234567">Hotspot</a> )</span>
        """
        self.assertEqual('Site name', self.parse())

    def test_commas(self):
        """Site names can contain extra commas."""
        self.value = 'Site, name, Subnational2, Subnational1, CO'
        self.assertEqual('Site, name', self.parse())

    def test_extra_whitespace(self):
        """Extra whitespace is removed from the name of the site."""
        self.value = 'Site \n name \n, Subnational2, Subnational1, CO'
        self.assertEqual('Site name', self.parse())
