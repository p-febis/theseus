from gql import Client, gql
from gql.transport.aiohttp import AIOHTTPTransport
from datetime import datetime, timedelta
from typing import Optional

REFRESH_AFTER = timedelta(minutes=4, seconds=50)

_createAccesTokenQuery = gql("""
mutation ($refresh_token: String!) {
  tokenRefresh(refreshToken: $refresh_token) {
    token
    errors {
      message
    }
  }
}
""")

_listFirstHundredCategoriesQuery = gql("""
query {
  categories(first: 100) {
    edges {
      node {
        name
        id
        parent {
          id
          name
        }
      }
    }
  }
}
""")

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

_createAttributeMutation = gql("""
mutation($input: AttributeCreateInput!) {
  attributeCreate(input: $input) {
    attribute {
      id
    }
    errors {
      message
    }
  }
}
""")

_createProductMutation = gql("""
mutation($product_input: ProductCreateInput!) {
  productCreate(input: $product_input) {
    product {
      id
    }
    errors {
      message
    }
  }
}
""")

_updateChannelListingMutation = gql("""
mutation($id:ID!, $channel_listing_input: [ProductChannelListingAddInput!]!) {
	productChannelListingUpdate(id: $id, input: {updateChannels: $channel_listing_input}) {
    errors {
      message
    }
  }
}
""")

_createProductVariant = gql("""
mutation($variant_input: ProductVariantCreateInput!) {
	productVariantCreate(input: $variant_input) {
    productVariant {
      id
    }
    errors {
      message
    }
  }
}
""")

_updateProductVariantChannelListing = gql("""
mutation($id: ID!, $variant_channel_input: [ProductVariantChannelListingAddInput!]!) {
  productVariantChannelListingUpdate(id: $id, input: $variant_channel_input) {
    errors {
      message
    }
  }
}
""")

_updateProductVariant = gql("""
mutation($stocks: [StockInput!]!, $variant: ID!) {
 productVariantStocksCreate(stocks: $stocks, variantId: $variant) {
  	errors {
    	message
  	}
	}
}
""")


class Commands:
    def __init__(self, refresh_token: str | None, url: str | None) -> None:
        if refresh_token is None or url is None:
            raise Exception("refresh_token and/or url cannot be None!")

        self._refresh_token = refresh_token
        self._url = url

        self._createSingleUseClient()
        success = self._createAccessToken()
        if success:
            self._createClient()
        else:
            raise Exception("Failed to create access token!")

    def _createSingleUseClient(self) -> None:
        transport = AIOHTTPTransport(url=self._url)
        self._client = Client(transport=transport)

    def _createAccessToken(self) -> bool:
        self._time_since_refresh = datetime.now()
        result = self._client.execute(
            _createAccesTokenQuery,
            variable_values={"refresh_token": self._refresh_token},
        )

        if len(result["tokenRefresh"]["errors"]) == 0:
            self._access_token = result["tokenRefresh"]["token"]
            return True
        else:
            print(result["tokenRefresh"]["errors"])
            return False

    def _createClient(self) -> None:
        transport = AIOHTTPTransport(
            url=self._url, headers={"Authorization-Bearer": self._access_token}
        )
        self._client = Client(transport=transport)

    def _refreshIfNeeded(self) -> None:
        if (datetime.now() - self._time_since_refresh) >= REFRESH_AFTER:
            success = self._createAccessToken()
            if success:
                self._createClient()
            else:
                raise Exception("Failed to refresh!")

    # ideally this should keep running until all categories are exhausted,
    # but lets just hope you don't want to have more than 100 categories!

    def listCategories(self) -> list[dict]:
        self._refreshIfNeeded()

        result = self._client.execute(_listFirstHundredCategoriesQuery)

        return result["categories"]["edges"]

    # (category_input) https://docs.saleor.io/api-reference/products/inputs/category-input
    def createCategory(
        self, category_input: dict, parent_id: Optional[str] = None
    ) -> str | None:
        self._refreshIfNeeded()

        variable_values: dict[str, dict | str] = {
            "input": category_input,
        }

        if parent_id != None:
            variable_values["parent"] = parent_id

        result = self._client.execute(
            _createCategoryMutation,
            variable_values=variable_values,
        )

        if len(result["categoryCreate"]["errors"]) == 0:
            return result["categoryCreate"]["category"]["id"]
        else:
            print(result["categoryCreate"]["errors"])
            return None

    def createAttribute(self, attribute_info: dict) -> str | None:
        result = self._client.execute(
            _createAttributeMutation,
            variable_values={"input": attribute_info},
        )

        if len(result["attributeCreate"]["errors"]) == 0:
            return result["attributeCreate"]["attribute"]["id"]
        else:
            print(result["attributeCreate"]["errors"])
            return None

    # (product_input) https://docs.saleor.io/api-reference/products/inputs/product-create-input
    # (channel_listing_input) https://docs.saleor.io/api-reference/products/inputs/product-channel-listing-add-input
    # (variant_input) https://docs.saleor.io/api-reference/products/inputs/product-variant-channel-listing-add-input
    def createProduct(
        self,
        product_input: dict,
        channel_listing_input: list[dict],
        variant_input: dict,
        channel_listing_update_input: list[dict],
        variant_update_input: list[dict],
    ) -> str | None:
        self._refreshIfNeeded()

        product_result = self._client.execute(
            _createProductMutation, variable_values={"product_input": product_input}
        )

        product_id = (
            product_result["productCreate"]["product"]["id"]
            if len(product_result["productCreate"]["errors"]) == 0
            else None
        )

        if product_id == None:
            print("createProductMutation", product_result["productCreate"]["errors"])
            return None

        update_listing_result = self._client.execute(
            _updateChannelListingMutation,
            variable_values={
                "id": product_id,
                "channel_listing_input": channel_listing_input,
            },
        )

        if len(update_listing_result["productChannelListingUpdate"]["errors"]) != 0:
            print(
                "updateChannelListingMutation",
                update_listing_result["productChannelListingUpdate"]["errors"],
            )
            return None

        create_variant_result = self._client.execute(
            _createProductVariant,
            variable_values={
                "variant_input": {**{"product": product_id}, **variant_input}
            },
        )

        variant_id = (
            create_variant_result["productVariantCreate"]["productVariant"]["id"]
            if len(create_variant_result["productVariantCreate"]["errors"]) == 0
            else None
        )

        if variant_id == None:
            print(
                "createProductVariant",
                create_variant_result["productVariantCreate"]["errors"],
            )
            return

        update_variant_listing_result = self._client.execute(
            _updateProductVariantChannelListing,
            variable_values={
                "id": variant_id,
                "variant_channel_input": channel_listing_update_input,
            },
        )

        if (
            len(
                update_variant_listing_result["productVariantChannelListingUpdate"][
                    "errors"
                ]
            )
            != 0
        ):
            print(
                "updateProductVariantChannelListing",
                update_variant_listing_result["productVariantChannelListingUpdate"][
                    "errors"
                ],
            )
            return None

        update_variant_input_result = self._client.execute(
            _updateProductVariant,
            variable_values={"stocks": variant_update_input, "variant": variant_id},
        )

        if (
            len(update_variant_input_result["productVariantStocksCreate"]["errors"])
            != 0
        ):
            print(
                "productVariantStocksCreate",
                update_variant_input_result["productVariantStocksCreate"]["errors"],
            )
            return None

        return product_id
