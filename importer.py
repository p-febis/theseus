import click
import io

from theseus.parsers.default import DefaultParser

def getParserFromName(name: str) -> DefaultParser:
    match name:
        case _:
            return DefaultParser()


@click.command()
@click.option("--importer", default="default", help="Available importers: default")
@click.argument("input", type=click.File("r"))
def import_file(importer: str, input: io.TextIOWrapper):
    parser = getParserFromName(importer)

    products = list(map(parser.parse_line, input.readlines()[1:]))

    click.echo(products)


if __name__ == "__main__":
    import_file()
