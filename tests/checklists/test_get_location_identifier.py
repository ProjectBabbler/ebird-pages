from bs4 import BeautifulSoup
from unittest import TestCase

from ebird.pages.checklists import _get_location_identifier


class GetLocationIdentifierTests(TestCase):
    """
    Tests for extracting the unique identifier of the location.

    """
    def setUp(self):
        self.template = """
        <div class="rs-body">
            <h5 class="bd obs-loc">%s</h5>
        <div>
        """
        self.tag = None

    def parse(self):
        self.assertIsNotNone(self.tag)
        content = self.template % self.tag
        soup = BeautifulSoup(content, "lxml")
        tag = soup.find('div', class_='rs-body')
        return _get_location_identifier(tag)

    def test_identifier(self):
        """If the location is a hotspot the uniwue identifier is returned."""
        self.tag = '<span class="btn-map">( <a href="/ebird/hotspot/L1234567">Hotspot</a> )</span>'
        self.assertEqual('L1234567', self.parse())

    def test_optional(self):
        """The identifier is None if the location is not a hotspot."""
        self.tag = ''
        self.assertEqual(None, self.parse())

    def test_extra_whitespace(self):
        """If the hotspot link text can contains whitespace."""
        self.tag = '<span class="btn-map">( <a href="/ebird/hotspot/L1234567">\n Hotspot \n</a> )</span>'
        self.assertEqual('L1234567', self.parse())

    def test_lower_case(self):
        """The hotspot link text can be lower case."""
        self.tag = '<span class="btn-map">( <a href="/ebird/hotspot/L1234567">hotspot</a> )</span>'
        self.assertEqual('L1234567', self.parse())
