from bs4 import BeautifulSoup
from unittest import TestCase

from ebird.pages.checklists import _get_observers


class FindObserversTests(TestCase):
    """
    Tests for finding the list of observers.

    """
    def setUp(self):
        self.template = """
            <div class="rs-body-spp">
            <dl class="def-list">
                <dt>%s</dt>
                <dd><strong>John Smith</strong></dd>
            </dl>
            </div>
        """
        self.label = None
        self.expected = ['John Smith']

    def parse(self):
        self.assertIsNotNone(self.label)
        content = self.template % self.label
        soup = BeautifulSoup(content, "lxml")
        tag = soup.find('div', class_='rs-body-spp')
        return _get_observers(tag)

    def test_label(self):
        """The observers field can be found."""
        self.label = 'Observers:'
        self.assertEqual(self.expected, self.parse())

    def test_label_multiple_lines(self):
        """The observers label can be split over multiple lines."""
        self.label = '\nObservers:\n'
        self.assertEqual(self.expected, self.parse())

    def test_label_lower_case(self):
        """The observers label can be lower case."""
        self.label = 'observers:'
        self.assertEqual(self.expected, self.parse())

    def test_label_missing_colon(self):
        """The observers label can have the trailing colon missing."""
        self.label = 'Observers'
        self.assertEqual(self.expected, self.parse())

    def test_no_observers(self):
        """An exception is raised if no observers can be found"""
        self.label = 'Distance:'
        self.assertRaises(AttributeError, self.parse)


class ParseObserversTests(TestCase):
    """
    Tests for extracting the list of observers.

    """

    def setUp(self):
        self.template = """
            <div class="rs-body-spp">
            <dl class="def-list">
                <dt>Observers:</dt>
                <dd><strong>%s</strong></dd>
            </dl>
            </div>
        """
        self.value = None

    def parse(self):
        self.assertIsNotNone(self.value)
        content = self.template % self.value
        soup = BeautifulSoup(content, "lxml")
        tag = soup.find('div', class_='rs-body-spp')
        return _get_observers(tag)

    def test_observer(self):
        """The name of the observer who submitted the checklist is returned."""
        self.value = 'John Smith'
        self.assertListEqual(['John Smith'], self.parse())

    def test_multiple_lines(self):
        """The name of the observer can be split over multiple lines."""
        self.value = '\n John \n Smith \n'
        self.assertEqual(['John Smith'], self.parse())

    def test_not_strong(self):
        """The <strong> tag surrounding the observer name(s) may be omitted."""
        self.template = """
            <div class="rs-body-spp">
            <dl class="def-list">
                <dt>Observers:</dt>
                <dd>%s</dd>
            </dl>
            </div>
        """
        self.value = 'John Smith'
        self.assertEqual(['John Smith'], self.parse())
