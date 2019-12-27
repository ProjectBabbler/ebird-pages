from bs4 import BeautifulSoup
from unittest import TestCase

from ebird.pages.checklists import _get_count


class GetEntryCountTests(TestCase):
    """
    Tests for extracting the count for each species seen.

    """
    def setUp(self):
        self.template = """
            <tr class="spp-entry">
                <th><h5 class="se-count">%s</h5></th>
            </tr>
        """
        self.value = None

    def parse(self):
        self.assertIsNotNone(self.value)
        content = self.template % self.value
        soup = BeautifulSoup(content, "lxml")
        tag = soup.find('tr', class_='spp-entry')
        return _get_count(tag)

    def test_integer(self):
        """The count for a species is returned as an integer."""
        self.value = '3'
        self.assertEqual(3, self.parse())

    def test_present(self):
        """If species was not counted then None is returned."""
        self.value = 'X'
        self.assertEqual(None, self.parse())

    def test_whitespace(self):
        """Count is returned even if there is surrounding whitespace."""
        self.value = '\n3\n'
        self.assertEqual(3, self.parse())

    def test_present_lower_case(self):
        """The character used to indicate only presence can be lower case."""
        self.value = 'x'
        self.assertEqual(None, self.parse())
