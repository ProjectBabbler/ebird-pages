"""
Command-line script to scape the web page(s) for a checklists and
save the data in JSON format to a file or to stdout.

"""

import click

from ebird.pages import get_checklist

from .base import save


# noinspection PyShadowingBuiltins
@click.command()
@click.option('--id', prompt=True,
              help="The unique identifier for the checklist.")
@click.option('--out', prompt=True, type=click.File('wb'),
              help='The name of a file to write the results to. To print'
                   ' the results to the screen use -.')
@click.option('--indent', type=int, default=None,
              help='Pretty-print the results with this level of indentation.')
def cli(id, out, indent):
    """Get the data for a checklist from its eBird web page."""
    save(out, get_checklist(id), indent)

if __name__ == '__main__':
    cli()
