from typing import Any, Optional
import click
from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport

_createCategoryMutation = gql("""
mutation ($input: CategoryInput!, $parent: ID) {
  categoryCreate(input: $input, parent:$parent) {
		errors {
      message
    }
    category {
      id
    }
  }
}
""")

_createProductTypeMutation = gql("""
mutation ($input: ProductTypeInput!) {
	productTypeCreate(input: $input) {
    productType {
      id
    }
    errors {
      message
    }
  }
}
""")

_createProductBulkMutation = gql("""
mutation ($input: [ProductBulkCreateInput!]!) {
  productBulkCreate(products: $input) {
    errors {
      message
    }
  }
}
""")


class GqlCommands:
    def __init__(self, saleor_url: str, app_token: str):
        transport = AIOHTTPTransport(
            url=saleor_url, headers={"Authorization": f"Bearer {app_token}"}
        )
        self.client = Client(transport=transport)

    def createCategoryMutation(
        self, category_input: dict[str, str], parent_id: Optional[str] = None
    ) -> Optional[str]:
        variable_values: dict[str, dict | str] = {
            "input": category_input,
        }

        if parent_id is not None:
            variable_values["parent"] = parent_id

        result = self.client.execute(
            _createCategoryMutation,
            variable_values=variable_values,
        )

        if len(result["categoryCreate"]["errors"]) == 0:
            return result["categoryCreate"]["category"]["id"]
        else:
            click.echo(
                f"createCategoryMutation: {result['categoryCreate']['errors']}",
                err=True,
            )
            return None

    def createProductTypeMutation(self, product_type_input: dict[str, str]):
        result = self.client.execute(
            _createProductTypeMutation,
            variable_values={"input": product_type_input},
        )
        if len(result["productTypeCreate"]["errors"]) == 0:
            return result["productTypeCreate"]["productType"]["id"]
        else:
            click.echo(
                f"createProductTypeMutation: {result['productTypeCreate']['errors']}",
                err=True,
            )
            return None

    def createProductBulkMutation(
        self, product_bulk_create_input: list[dict[str, str | list[dict[str, Any]]]]
    ):
        result = self.client.execute(
            _createProductBulkMutation,
            variable_values={"input": product_bulk_create_input},
        )
        if len(result["productBulkCreate"]["errors"]) != 0:
            click.echo(
                f"createProductBulkMutation: {result['createProductTypeMutation']['errors']}",
                err=True,
            )
