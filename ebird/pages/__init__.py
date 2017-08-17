# -*- coding: utf-8 -*-

"""A set of functions for scraping data from eBird web pages."""

# TODO Configure logging and add NullHandler
# See https://docs.python.org/3/howto/logging.html#configuring-logging-for-a-library

from .version import __version__

# Import all the functions that make up the public API.
# noinspection PyUnresolvedReferences
from ebird.pages.checklists import get_checklist

