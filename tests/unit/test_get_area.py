from bs4 import BeautifulSoup
from unittest import TestCase

from ebird.pages.checklists import _get_area


class FindAreaTests(TestCase):
    """
    Tests for finding the area covered in the checklist.

    """
    def setUp(self):
        self.template = """
            <div class="rs-body-spp">
            <dl class="def-list">
                <dt>%s</dt>
                <dd>16 hectares</dd>
            </dl>
            </div>
        """
        self.label = None
        self.expected = (16, 'ha')

    def parse(self):
        self.assertIsNotNone(self.label)
        content = self.template % self.label
        soup = BeautifulSoup(content, "lxml")
        tag = soup.find('div', class_='rs-body-spp')
        return _get_area(tag)

    def test_label(self):
        """The area field can be found."""
        self.label = 'Area:'
        self.assertEqual(self.expected, self.parse())

    def test_label_multiple_lines(self):
        """The area label can be split over multiple lines."""
        self.label = '\nArea:\n'
        self.assertEqual(self.expected, self.parse())

    def test_label_lower_case(self):
        """The area label can be lower case."""
        self.label = 'area:'
        self.assertEqual(self.expected, self.parse())

    def test_label_missing_colon(self):
        """The area label can have the trailing colon missing."""
        self.label = 'Area'
        self.assertEqual(self.expected, self.parse())

    def test_area_optional(self):
        """If the area is missing a tuple containing None is returned."""
        self.label = 'Distance:'
        self.assertEqual((None, None), self.parse())


class ParseAreaTests(TestCase):
    """
    Tests for extracting the area covered in the checklist.

    """
    def setUp(self):
        self.template = """
            <div class="rs-body-spp">
            <dl class="def-list">
                <dt>Area:</dt>
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
        return _get_area(tag)

    def test_hectares(self):
        """The area may be measured in hectares."""
        self.value = '1.1 hectares'
        self.assertEqual((1.1, 'ha'), self.parse())

    def test_acres(self):
        """The area may be measured in acres."""
        self.value = '1.1 acres'
        self.assertEqual((1.1, 'acre'), self.parse())

    def test_integer(self):
        """The area is returned as a floating point number."""
        self.value = '1 hectares'
        self.assertEqual((1.0, 'ha'), self.parse())

    def test_multiple_lines(self):
        """The area can be split over multiple lines."""
        self.value = '\n 1.1 \n hectares \n'
        self.assertEqual((1.1, 'ha'), self.parse())

    def test_text(self):
        """An exception is raised if the area is not a number."""
        self.value = 'four hectares'
        self.assertRaises(ValueError, self.parse)

    def test_units_capitalized(self):
        """The area units can be capitalized."""
        self.value = '1.1 Hectares'
        self.assertEqual((1.1, 'ha'), self.parse())

    def test_units_abbreviated(self):
        """The area in hectares can be abbreviated to ha."""
        self.value = '1.1 ha'
        self.assertEqual((1.1, 'ha'), self.parse())

    def test_units_unknown(self):
        """An exception is raised if the area units is not supported."""
        self.value = '1.1 sq. mile(s)'
        self.assertRaises(KeyError, self.parse)
