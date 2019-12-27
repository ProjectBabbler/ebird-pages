from bs4 import BeautifulSoup
from unittest import TestCase

from ebird.pages.checklists import _get_entry


class GetEntryTests(TestCase):
    """
    Tests for each entry found in the checklist.

    """
    def setUp(self):
        self.content = None
        
    def parse(self):
        self.assertIsNotNone(self.content)
        soup = BeautifulSoup(self.content, "lxml")
        tag = soup.find('tr', class_='spp-entry')
        return _get_entry(tag)

    def test_correct_keys(self):
        """An entry contains the species and number seen."""
        self.content = """
            <tr class="spp-entry">
                <th><h5 class="se-count">3</h5></th>
                <td>
                    <h5 class="se-name">European Serin</h5>
                </td>
            </tr>
        """
        expected = ['count', 'species']
        self.assertListEqual(expected, sorted(self.parse().keys()))
