from bs4 import BeautifulSoup
from unittest import TestCase

from ebird.pages.checklists import _get_complete


class ParseCompleteTests(TestCase):
    """
    Tests for extracting whether the checklist contains all species seen.

    """
    def setUp(self):
        self.template = """
            <div class="rs-body">
                <div class="all-spp-ans">
                    <h5>%s</h5>
                </div>
            </div>
        """
        self.value = None

    def parse(self):
        self.assertIsNotNone(self.value)
        content = self.template % self.value
        soup = BeautifulSoup(content, "lxml")
        tag = soup.find('div', class_='rs-body')
        return _get_complete(tag)

    def test_yes(self):
        """If all species were recorded, True is returned."""
        self.value = 'Yes'
        self.assertEqual(True, self.parse())

    def test_no(self):
        """If not all species were recorded, False is returned."""
        self.value = 'No'
        self.assertEqual(False, self.parse())

    def test_whitespace(self):
        """Whitespace surrounding all species recorded is removed."""
        self.value = '\nYes\n'
        self.assertEqual(True, self.parse())

    def test_lower_case(self):
        """All species removed can be in lower case"""
        self.value = 'yes'
        self.assertEqual(True, self.parse())
