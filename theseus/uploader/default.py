from .base import BaseUploader
from ..types import Product 

class DefaultUploader(BaseUploader):
    def upload(self, product: Product) -> None:
        pass
