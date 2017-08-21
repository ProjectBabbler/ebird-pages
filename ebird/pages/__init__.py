# -*- coding: utf-8 -*-

"""A set of functions for scraping data from eBird web pages."""

from .version import __version__

# Import all the functions that make up the public API.
# noinspection PyUnresolvedReferences
from ebird.pages.checklists import get_checklist

