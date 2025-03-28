from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport

_categoryCreate = gql(
    """
mutation ($input: CategoryInput!, $parent: ID) {
  categoryCreate(input: $input, parent: $parent) {
    errors {
      message
    }
  }
}
        """
)


def createCategoryQuery():
    pass


del _categoryCreate
