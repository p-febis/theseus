from ..types import Product


class BaseUploader:
    def bulk(self, products: list[Product]) -> None:
        raise Exception("Base class should never be called")
