from ..gql import GqlCommands
from ..types import Product


class BaseUploader:
    def __init__(self, gql_commands: GqlCommands) -> None:
        self.gql = gql_commands

    def bulk(self, products: list[Product]) -> None:
        raise Exception("Base class should never be called")
