import click
from .base import BaseParser
from ..types import Product, Currency


class DefaultParser(BaseParser):
    def take(self, values: list[str]) -> str:
        return values.pop()

    def takeDescription(self, values: list[str]) -> str:
        return self.makeEdjsDescription(values.pop())

    def takeCurrency(self, currency_code: str, values: list[str]) -> Currency:
        return Currency(currency_code, float(values.pop()))

    def parse_line(self, line: str) -> Product:
        values = line.split(";")  # greek question mark
        currencies: list[Currency] = []

        keys = self.first_line[:-1].split(";")  # idem.
        keys.reverse()

        name = type_ = category = sku = description = ""
        quantity = 0

        for key in keys:
            match key:
                case "Name":
                    name = self.take(values)
                    continue
                case "Item Type":
                    type_ = self.take(values)
                    continue
                case "Category":
                    category = self.take(values)
                    continue
                case "Quantity":
                    quantity = int(self.take(values))
                    continue
                case "Sku":
                    sku = self.take(values)
                    continue
                case "Description":
                    description = self.takeDescription(values)
                    continue

            if key.startswith("Price"):
                [_, currency_code] = key.split(" ")
                currencies.append(self.takeCurrency(currency_code, values))
                continue

            click.echo(f"Unkonwn key: {key}", err=True)
            values.pop()

        return Product(name, type_, sku, category, currencies, quantity, description)
