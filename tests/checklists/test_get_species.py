from bs4 import BeautifulSoup
from unittest import TestCase

from ebird.pages.checklists import _get_species


class GetSpeciesTests(TestCase):
    """
    Tests for extracting the species from each entry in the list.

    """
    def setUp(self):
        self.template = """
            <tr class="spp-entry">
                <td><h5 class="se-name">%s</h5></td>
            </tr>
        """
        self.value = None

    def parse(self):
        self.assertIsNotNone(self.value)
        content = self.template % self.value
        soup = BeautifulSoup(content, "lxml")
        tag = soup.find('tr', class_='spp-entry')
        return _get_species(tag)

    def test_species(self):
        """The name of the species is returned as a string."""
        self.value = 'Barn Swallow'
        self.assertEqual('Barn Swallow', self.parse())

    def test_multiple_lines(self):
        """The species name can be split over multiple lines."""
        self.value = '\n Barn \n Swallow \n'
        self.assertEqual('Barn Swallow', self.parse())

    def test_subspecies(self):
        """The species name can have a subspecies designator."""
        self.value = 'Barn Swallow (White-bellied)'
        self.assertEqual('Barn Swallow (White-bellied)', self.parse())
