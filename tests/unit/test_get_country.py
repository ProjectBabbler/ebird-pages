from bs4 import BeautifulSoup
from unittest import TestCase

from ebird.pages.checklists import _get_country


class ParseCountryTests(TestCase):
    """
    Tests for extracting the country code.

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
        return _get_country(tag)

    def test_country(self):
        """The country code is returned."""
        self.value = 'Site, Subnational2, Subnational1, CO'
        self.assertEqual('CO', self.parse())

    def test_extra_commas(self):
        """The country code is returned even though there are extra commas."""
        self.value = 'Site Name, With Commas, Subnational2, Subnational1, CO'
        self.assertEqual('CO', self.parse())

    def test_whitespace(self):
        """Whitespace trailing the country code is removed."""
        self.value = 'Site, Subnational2, Subnational1, CO \n'
        self.assertEqual('CO', self.parse())

    def test_period(self):
        """Any trailing period is removed from the country code."""
        self.value = 'Site, Subnational2, Subnational1, CO.'
        self.assertEqual('CO', self.parse())
