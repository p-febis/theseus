from typing import Optional
import click
import yaml
import io

from theseus.gql import GqlCommands
from theseus.parsers.default import DefaultParser
from theseus.uploader.default import DefaultUploader


def makeParserFromName(name: str, first_line: str) -> DefaultParser:
    match name:
        case _:
            return DefaultParser(first_line)
def makeUploaderFromName(name: str) -> DefaultUploader:
    
    app_token: Optional[str] = None
    saleor_url: Optional[str] = None

    with open("config.yml", 'r') as config:
        data = yaml.safe_load(config)
    
        app_token = data["credentials"]["app_token"]
        saleor_url = data["credentials"]["saleor_url"]

    if saleor_url is None:
        click.echo("saleor_url not set!")
        exit(-1)
    if app_token is None:
        click.echo("app_token not set!")
        exit(-1)

    gql_commands = GqlCommands(saleor_url, app_token)

    match name:
        case _:
            return DefaultUploader(gql_commands)


@click.command()
@click.option("--importer", default="default", help="Available importers: default")
@click.option("--uploader", default="default", help="Available uploaders: default")
@click.argument("input", type=click.File("r"))
def import_file(importer: str, uploader: str,input: io.TextIOWrapper):
    parser = makeParserFromName(importer, input.readline())
    products = list(map(parser.parse_line, input.readlines()[1:]))

    up = makeUploaderFromName(uploader)
    up.bulk(products)


if __name__ == "__main__":
    import_file()
