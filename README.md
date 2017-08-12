[![Build Status](https://travis-ci.org/ProjectBabbler/ebird-pages.svg?branch=master)](https://travis-ci.org/ProjectBabbler/ebird-pages)
[![PyPI version](https://badge.fury.io/py/ebird-pages.svg)](https://badge.fury.io/py/ebird-pages)
[![Supported Python Versions](https://img.shields.io/pypi/pyversions/ebird-pages.svg)](https://img.shields.io/pypi/pyversions/ebird-pages)

# eBird Pages

Although eBird has an API, not all the information from the database is 
available. The API, for example, does not return links to any uploaded 
photos; comments on an individual observation are also missing. eBird 
Pages is a set of scrapers for extracting data from various pages on 
the eBird web site. It complements the API, giving access to all the 
data that eBird makes publicly available.

## Install

```sh
pip install ebird-pages
```

## Usage

Scraping the data from a page is as simple as a function call. For example
to get all the data from a checklist use get_checklist() and pass in the unique 
identifier generated when the checklist was submitted to the eBird database:

```python
from ebird.pages import get_checklist

data = get_checklist('S38429565')
```
The function returns a dict with keys for the location, date, observers, etc.

### Command line

Each of the functions has a corresponding script that can be used on the 
command-line:

```sh
$ ebird-get-checklists S38429565
```
The script allows data for one or more checklists to be downloaded and written 
to a file in JSON format.

## Compatibility

ebird-pages works with Python 3.3+. 

## Dependencies

eBird Pages makes use of the following packages: Requests, BeautifulSoup4, lxml and pyCLI.
See requirements.txt for the version numbers of each of the libraries.

## License

eBird Pages is available under the terms of the [MIT](https://opensource.org/licenses/MIT) license.