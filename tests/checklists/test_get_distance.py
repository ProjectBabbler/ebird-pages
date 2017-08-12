from bs4 import BeautifulSoup
from unittest import TestCase

from ebird.pages.checklists import _get_distance


class FindDistanceTests(TestCase):
    """
    Tests for finding the distance covered in the checklist.

    """
    def setUp(self):
        self.template = """
            <div class="rs-body-spp">
            <dl class="def-list">
                <dt>%s</dt>
                <dd>1.0 kilometer(s)</dd>
            </dl>
            </div>
        """
        self.label = None
        self.expected = (1.0, 'km')

    def parse(self):
        self.assertIsNotNone(self.label)
        content = self.template % self.label
        soup = BeautifulSoup(content, "lxml")
        tag = soup.find('div', class_='rs-body-spp')
        return _get_distance(tag)

    def test_label(self):
        """The distance field can be found."""
        self.label = 'Distance:'
        self.assertEqual(self.expected, self.parse())

    def test_label_multiple_lines(self):
        """The distance label can be split over multiple lines."""
        self.label = '\nDistance:\n'
        self.assertEqual(self.expected, self.parse())

    def test_label_lower_case(self):
        """The distance label can be lower case."""
        self.label = 'distance:'
        self.assertEqual(self.expected, self.parse())

    def test_label_missing_colon(self):
        """The distance label can have the trailing colon missing."""
        self.label = 'Distance'
        self.assertEqual(self.expected, self.parse())

    def test_distance_optional(self):
        """If the distance is missing a tuple containing None is returned."""
        self.label = 'Area:'
        self.assertEqual((None, None), self.parse())


class ParseDistanceTests(TestCase):
    """
    Tests for extracting the value distance covered in the checklist.

    """

    def setUp(self):
        self.template = """
            <div class="rs-body-spp">
            <dl class="def-list">
                <dt>Distance:</dt>
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
        return _get_distance(tag)

    def test_kilometers(self):
        """The distance may be measured in kilometers."""
        self.value = '1.1 kilometer(s)'
        self.assertEqual((1.1, 'km'), self.parse())

    def test_miles(self):
        """The distance may be measured in miles."""
        self.value = '1.1 mile(s)'
        self.assertEqual((1.1, 'mi'), self.parse())

    def test_integer(self):
        """The distance is returned as a floating point number."""
        self.value = '1 kilometer(s)'
        self.assertEqual((1.0, 'km'), self.parse())

    def test_multiple_lines(self):
        """The distance can be split over multiple lines."""
        self.value = '\n 1.1 \n kilometer(s) \n'
        self.assertEqual((1.1, 'km'), self.parse())

    def test_text(self):
        """An exception is raised if the distance is not a number."""
        self.value = 'four kilometer(s)'
        self.assertRaises(ValueError, self.parse)

    def test_units_capitalized(self):
        """The distance units can be capitalized."""
        self.value = '1.1 Kilometer(s)'
        self.assertEqual((1.1, 'km'), self.parse())

    def test_units_abbreviated(self):
        """For a distance in kilometers, the units can be abbreviated to km."""
        self.value = '1.1 km(s)'
        self.assertEqual((1.1, 'km'), self.parse())

    def test_units_unknown(self):
        """An exception is raised if the distance units is not supported."""
        self.value = '1.1 furlongs'
        self.assertRaises(KeyError, self.parse)
