from bs4 import BeautifulSoup
from unittest import TestCase

from ebird.pages.checklists import _get_protocol


class FindProtocolTests(TestCase):
    """
    Tests for finding the protocol used to compile the checklist.

    """
    def setUp(self):
        self.template = """
            <div class="rs-body-spp">
            <dl class="def-list">
                <dt>%s</dt>
                <dd>Stationary</dd>
            </dl>
            </div>
        """
        self.label = None
        self.expected = 'Stationary'

    def parse(self):
        self.assertIsNotNone(self.label)
        content = self.template % self.label
        soup = BeautifulSoup(content, "lxml")
        tag = soup.find('div', class_='rs-body-spp')
        return _get_protocol(tag)

    def test_label(self):
        """The protocol field can be found."""
        self.label = 'Protocol:'
        self.assertEqual(self.expected, self.parse())

    def test_label_multiple_lines(self):
        """The protocol label can be split over multiple lines."""
        self.label = '\nProtocol:\n'
        self.assertEqual(self.expected, self.parse())

    def test_label_lower_case(self):
        """The protocol label can be lower case."""
        self.label = 'protocol:'
        self.assertEqual(self.expected, self.parse())

    def test_label_missing_colon(self):
        """The protocol label can have the trailing colon missing."""
        self.label = 'Protocol'
        self.assertEqual(self.expected, self.parse())


class ParseProtocolTests(TestCase):
    """
    Tests for extracting the protocol used in the checklist.

    """
    def setUp(self):
        self.template = """
            <div class="rs-body-spp">
            <dl class="def-list">
                <dt>Protocol:</dt>
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
        return _get_protocol(tag)

    def test_protocol(self):
        """The protocol is returned as a string."""
        self.value = 'Stationary'
        self.assertEqual('Stationary', self.parse())

    def test_value_multiple_lines(self):
        """The protocol may be split over multiple lines."""
        self.value = '\n Stationary \n'
        self.assertEqual('Stationary', self.parse())

    def test_value_lower_case(self):
        """The protocol may be lower case."""
        self.value = 'stationary'
        self.assertEqual('Stationary', self.parse())
