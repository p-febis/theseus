from typing import Optional
from slugify import slugify
from theseus.gql import GqlCommands
from .base import BaseUploader
from ..types import Product


class DefaultUploader(BaseUploader):
    def __init__(self, gql_commands: GqlCommands):
        super().__init__(gql_commands)
        self.categories: dict[str, str] = {}

    def makeCategory(self, category: str, parent_id: Optional[str]) -> Optional[str]:
        if category in self.categories:
            return self.categories[category]

        category_id = self.gql.createCategoryQuery(
            {"name": category, "slug": slugify(category)}, parent_id
        )

        if category_id:
            self.categories[category] = category_id

    def makeCategories(self, categories: list[str]) -> None:
        for category_path in categories:
            parts = category_path.split("/")
            parent_id = None
            
            for part in parts:
                if part not in self.categories:  
                    category_id = self.makeCategory(part, parent_id)
                    if category_id:
                        self.categories[part] = category_id
                parent_id = self.categories.get(part)


    def bulk(self, products: list[Product]) -> None:
        categories = list(map(lambda product: product.category, products))
        self.makeCategories(categories)
