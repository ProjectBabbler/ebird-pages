[![Build Status](https://travis-ci.org/ProjectBabbler/ebird-pages.svg?branch=master)](https://travis-ci.org/ProjectBabbler/ebird-pages)
[![PyPI version](https://badge.fury.io/py/ebird-pages.svg)](https://badge.fury.io/py/ebird-pages)
[![Supported Python Versions](https://img.shields.io/pypi/pyversions/ebird-pages.svg)](https://img.shields.io/pypi/pyversions/ebird-pages)

# eBird Pages

Although eBird has an API, not all the information from the database is
available. The API, for example, does not return links to any uploaded 
photos; comments on an individual observation are also missing. eBird Pages 
is a set of scrapers for extracting data from various pages on the eBird 
web site. It complements the API, giving access to all the data that eBird 
makes publicly available.

## Install

```sh
pip install ebird-pages
```

## Usage

Scraping the data from a page is as simple as a function call. For example
to get all the data from a checklist use get_checklist() and pass in the 
unique identifier generated when the checklist was submitted to the eBird
database:

```python
from ebird.pages import get_checklist

data = get_checklist('S38429565')
```
The function returns a dict with keys for the location, date, observers, etc.

You can also get the complete list of checklists from the "Recent Checklists"
page, e.g. https://ebird.org/region/US-MA/recent-checklists. From there you 
can download each checklist:

```python
import time

from ebird.pages import get_checklist, get_recent_checklists

for item in get_recent_checklists("US-MA"):
    checklist = get_checklist(item["identifier"])
    # Be nice and don't hit the servers as fast as possible
    time.sleep(10)
```


## Compatibility

ebird-pages works with all currently supported versions of Python (3.8+). 

## License

eBird Pages is available under the terms of the [MIT](https://opensource.org/licenses/MIT) license.
