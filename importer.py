import click
import io

from theseus.parsers.default import DefaultParser
from theseus.uploader.default import DefaultUploader


def makeParserFromName(name: str, first_line: str) -> DefaultParser:
    match name:
        case _:
            return DefaultParser(first_line)
def makeUploaderFromName(name: str, first_line: str) -> DefaultUploader:
    match name:
        case _:
            return DefaultUploader()


@click.command()
@click.option("--importer", default="default", help="Available importers: default")
@click.option("--uploader", default="default", help="Available uploaders: default")
@click.argument("input", type=click.File("r"))
def import_file(importer: str, input: io.TextIOWrapper):
    parser = makeParserFromName(importer, input.readline())
    products = list(map(parser.parse_line, input.readlines()[1:]))


if __name__ == "__main__":
    import_file()
