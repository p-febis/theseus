from typing import Any, Optional
import click
from theseus.gql import GqlCommands
from .base import BaseUploader
from ..types import Product


class DefaultUploader(BaseUploader):
    def __init__(
        self,
        gql_commands: GqlCommands,
        currency_map: dict[str, str],
        warehouse_id: str,
        chunks_size: int,
    ):
        super().__init__(gql_commands)
        # TODO: Introspection
        self.categories: dict[str, str] = {}
        self.product_types: dict[str, str] = {}

        self.currency_map = currency_map
        self.warehouse_id = warehouse_id
        self.chunks_size = chunks_size

    def makeCategory(self, category: str, parent_id: Optional[str]) -> Optional[str]:
        if category in self.categories:
            return self.categories[category]

        return self.gql.createCategoryMutation({"name": category}, parent_id)

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

    def makeProductType(self, product_type: str) -> Optional[str]:
        if product_type in self.product_types:
            return self.product_types[product_type]

        return self.gql.createProductTypeMutation({"name": product_type})

    def makeProductTypes(self, product_types: list[str]) -> None:
        for product_type in product_types:
            product_type_id = self.makeProductType(product_type)
            if product_type_id:
                self.product_types[product_type] = product_type_id

    def chunks(self, list_: list[Any], n: int):
        for i in range(0, len(list_), n):
            yield list_[i : i + n]

    def productToBulkCreateInfo(
        self, product: Product
    ) -> dict[str, str | list[dict[str, Any]]]:  # TODO: Strenghten typing
        return {
            "category": self.categories[product.category.split("/")[-1]],
            "description": product.description,
            "name": product.name,
            "productType": self.product_types[product.type_],
            "channelListings": list(
                map(
                    lambda currency: {
                        "channelId": self.currency_map[currency.code],
                        "isPublished": True,
                        "isAvailableForPurchase": True,
                    },
                    product.currencies,
                )
            ),
            # TODO: Allow multiple product variants, perhaps in a more complex parser
            "variants": [
                {
                    "attributes": [],
                    "sku": product.sku,
                    "name": product.name,
                    "stocks": [
                        {
                            "warehouse": self.warehouse_id,
                            "quantity": product.quantity,
                        }
                    ],
                    "channelListings": list(
                        map(
                            lambda currency: {
                                "channelId": self.currency_map[currency.code],
                                "price": currency.value,
                            },
                            product.currencies,
                        )
                    ),
                }
            ],
        }

    def bulkUploadProducts(self, products: list[Product]) -> None:
        product_bulk_create_input = list(
            map(lambda product: self.productToBulkCreateInfo(product), products)
        )

        self.gql.createProductBulkMutation(product_bulk_create_input)

    def bulk(self, products: list[Product]) -> None:
        categories = list(map(lambda product: product.category, products))
        product_types = list(map(lambda product: product.type_, products))

        self.makeCategories(categories)
        click.echo("Created categories")

        self.makeProductTypes(product_types)
        click.echo("Created product types")

        done = 0

        for chunk in self.chunks(products, self.chunks_size):
            self.bulkUploadProducts(chunk)

            done += len(chunk)
            click.echo(f"Finished {done} products")
