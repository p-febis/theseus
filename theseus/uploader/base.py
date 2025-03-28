from ..types import Product 

class BaseUploader:
    def upload(self, product: Product) -> None:
        raise Exception("Base class should never be called")
