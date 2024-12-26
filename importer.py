from dotenv import dotenv_values
from lib.commands import Commands
from slugify import slugify
import csv
import sys
import json

if len(sys.argv) < 2:
    print("importer.py requires the filename to be passed as an argument!")
    exit()


config = dotenv_values(".env")

if config["REFRESH_TOKEN"] == None:
    print("REFRESH_TOKEN must be set in .env file.")

if config["API_URL"] == None:
    print("API_URL must be set in .env file.")

# Change these values!
CHANNEL_IDS = ["Q2hhbm5lbDoz"]
WAREHOUSE_ID = "V2FyZWhvdXNlOjFlZjQzYmE3LTQyZjUtNDc5Yi1hNTUyLTNhODljMzRiN2Y1Zg=="
DEFAULT_PRODUCT_TYPE = "UHJvZHVjdFR5cGU6Mg=="

commands = Commands(config["REFRESH_TOKEN"], config["API_URL"])

category_id = {}
attribute_id = {}


def getOrCreateCategory(category: str, parent_id: str | None = None) -> str:
    if category in category_id:
        return category_id[category]

    id = commands.createCategory(
        {"name": category, "slug": slugify(category)}, parent_id
    )
    if id == None:
        print(f"Failed to create Category {category}")
        exit()

    category_id[category] = id

    return id


def getOrCreateAttribute(attribute: str) -> str:
    if attribute in attribute_id:
        return attribute_id[attribute]

    id = commands.createAttribute(
        {"name": attribute, "slug": slugify(attribute), "type": "PRODUCT_TYPE"}
    )
    if id == None:
        print(f"Failed to create Variant {attribute}")
        exit()

    attribute_id[attribute] = id

    return id


with open(sys.argv[1], newline="") as file:
    reader = csv.reader(file, delimiter=",")

    next(reader)

    for row in reader:
        values = {
            "category": row[0],
            "name": row[1],
            "attribute": row[2],
            "size": row[3],
            "qty": row[4],
            "price": row[5],
            "sku": row[6],
            "description": row[8],
        }

        categories = values["category"].split("/")
        print(categories)

        id = (
            getOrCreateCategory(categories[1], getOrCreateCategory(categories[0]))
            if len(categories) > 1
            else getOrCreateCategory(categories[0])
        )

        product_id = commands.createProduct(
            product_input={
                "category": id,
                "productType": DEFAULT_PRODUCT_TYPE,
                "name": values["name"],
                "slug": slugify(values["name"]),
                "description": json.dumps(
                    {
                        "time": 1735178172938,
                        "blocks": [
                            {
                                "id": "my-random-id",
                                "type": "paragraph",
                                "data": {"text": values["description"]},
                            }
                        ],
                        "version": "2.24.3",
                    }
                ),
            },
            channel_listing_input=list(
                map(
                    lambda channel: {
                        "channelId": channel,
                        "isAvailableForPurchase": True,
                        "isPublished": True,
                        "visibleInListings": True,
                    },
                    CHANNEL_IDS,
                )
            ),
            variant_input={
                "attributes": [],
                "trackInventory": True,
                "sku": values["sku"],
            },
            channel_listing_update_input=list(
                map(
                    lambda channel: {
                        "channelId": channel,
                        "price": float(values["price"].replace(",", "")),
                    },
                    CHANNEL_IDS,
                )
            ),
            variant_update_input=[
                {"warehouse": WAREHOUSE_ID, "quantity": int(values["qty"])}
            ],
        )
