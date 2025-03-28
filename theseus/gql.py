from typing import Optional
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


class GqlCommands:
    def __init__(self, saleor_url: str, app_token: str):
        transport = AIOHTTPTransport(
            url=saleor_url, headers={"Authorization": f"Bearer {app_token}"}
        )
        self.client = Client(transport=transport)

    def createCategoryQuery(
        self, category_input: dict[str, str], parent_id: Optional[str] = None
    ) -> Optional[int]:
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
            click.echo(f"createCategoryQuery: {result['categoryCreate']['errors']}", err = True)
            return None
