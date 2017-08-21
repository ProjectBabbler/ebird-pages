#!/bin/sh

# Tests for the get-checklists script.

# Get the data for a checklist.
get-checklist --id S38645981 --out -

# Missing values should be prompted for.
get-checklist --out -
