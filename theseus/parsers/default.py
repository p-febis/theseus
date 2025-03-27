import click
from theseus.types.product import Currency
from .base import BaseParser
from ..types import Product


class DefaultParser(BaseParser):
    def takeName(self) -> None:
        self.name = self.values.pop()

    def takeCategory(self) -> None:
        self.category = self.values.pop()

    def takeQuantity(self) -> None:
        self.quanitity = int(self.values.pop())

    def takeSku(self) -> None:
        self.sku = self.values.pop()

    def takeDescription(self) -> None:
        self.description = self.makeEdjsDescription(self.values.pop())

    def takeCurrency(self, currency_code: str) -> None:
        self.currencies.append(Currency(currency_code, float(self.values.pop())))

    def toProduct(self) -> Product:
        return Product(self.name, self.category, self.currencies, self.quanitity, self.description)

    def parse_line(self, line: str) -> Product:
        self.values = line.split(";") # greek question mark
        self.currencies: list[Currency] = []

        keys = self.first_line[:-1].split(";") # idem.
        keys.reverse()

        for key in keys:

            if key.startswith("Price"):
                [_, currency_code] = key.split(" ")
                self.takeCurrency(currency_code)
                continue

            match key:
                case "Name":
                    self.takeName()
                    continue
                case "Category":
                    self.takeCategory()
                    continue
                case "Quantity":
                    self.takeQuantity()
                    continue
                case "Sku":
                    self.takeSku()
                    continue
                case "Description":
                    self.takeDescription()
                    continue
                case _:
                    click.echo(f"Unkonwn key: {key}", err=True)
                    self.values.pop()

        return self.toProduct()
