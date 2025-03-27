from .base import BaseParser
from ..types import Product


class DefaultParser(BaseParser):
    def parse_line(self, line: str) -> Product:
        values = line.split(",")

        product = {
            "category": values[0],
            "name": values[1],
            "attribute": values[2],
            "size": values[3],
            "qty": values[4],
            "price": values[5],
            "sku": values[6],
            "description": values[8],
        }

        return Product(
            product["name"],
            product["category"],
            _,
            int(product["qty"]),
            self.makeEdjsDescription(product["description"]),
        )
