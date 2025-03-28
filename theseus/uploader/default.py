from .base import BaseUploader
from ..types import Product


class DefaultUploader(BaseUploader):
    def __init__(self):
        self.categories: dict[str, str] = {}

    def makeCategories(self, categories: list[str]) -> None:
        print(categories)

    def bulk(self, products: list[Product]) -> None:
        categories = list(map(lambda product: product.category, products))
        self.makeCategories(categories)
