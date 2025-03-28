import click
import io

from theseus.parsers.default import DefaultParser


def makeParserFromName(name: str, first_line: str) -> DefaultParser:
    match name:
        case _:
            return DefaultParser(first_line)


@click.command()
@click.option("--importer", default="default", help="Available importers: default")
@click.argument("input", type=click.File("r"))
def import_file(importer: str, input: io.TextIOWrapper):
    parser = makeParserFromName(importer, input.readline())

    products = list(map(parser.parse_line, input.readlines()[1:]))

    click.echo(products)


if __name__ == "__main__":
    import_file()
