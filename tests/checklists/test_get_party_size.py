from bs4 import BeautifulSoup
from unittest import TestCase

from ebird.pages.checklists import _get_party_size


class FindPartySizeTests(TestCase):
    """
    Tests for finding the number of observers.

    """
    def setUp(self):
        self.template = """
            <div class="rs-body-spp">
            <dl class="def-list">
                <dt>%s</dt>
                <dd>3</dd>
            </dl>
            </div>
        """
        self.label = None
        self.expected = 3

    def parse(self):
        self.assertIsNotNone(self.label)
        content = self.template % self.label
        soup = BeautifulSoup(content, "lxml")
        tag = soup.find('div', class_='rs-body-spp')
        return _get_party_size(tag)

    def test_label(self):
        """The party size field can be found."""
        self.label = 'Party Size:'
        self.assertEqual(self.expected, self.parse())

    def test_label_multiple_lines(self):
        """The area label can be split over multiple lines."""
        self.label = '\nParty Size:\n'
        self.assertEqual(self.expected, self.parse())

    def test_label_lower_case(self):
        """The area label can be lower case."""
        self.label = 'party size:'
        self.assertEqual(self.expected, self.parse())

    def test_label_missing_colon(self):
        """The area label can have the trailing colon missing."""
        self.label = 'Party Size'
        self.assertEqual(self.expected, self.parse())


class ParsePartySizeTests(TestCase):
    """
    Tests for extracting the area covered in the checklist.

    """

    def setUp(self):
        self.template = """
            <div class="rs-body-spp">
            <dl class="def-list">
                <dt>Party Size:</dt>
                <dd>%s</dd>
            </dl>
            </div>
        """
        self.value = None

    def parse(self):
        self.assertIsNotNone(self.value)
        content = self.template % self.value
        soup = BeautifulSoup(content, "lxml")
        tag = soup.find('div', class_='rs-body-spp')
        return _get_party_size(tag)

    def test_integer(self):
        """The number of observers is returned as an integer."""
        self.value = '3'
        self.assertEqual(3, self.parse())

    def test_multiple_lines(self):
        """The number of observers can be split over multiple lines."""
        self.value = '\n 3 \n'
        self.assertEqual(3, self.parse())
