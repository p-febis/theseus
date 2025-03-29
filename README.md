# Theseus
---

Theseus is a streamlined tool for importing and uploading product data into a Saleor instance via GraphQL. It provides flexible parsing and bulk uploading capabilities using configurable importers and uploaders.

## Features
- Parse product data from structured text files.
- Upload products in bulk to a Saleor backend.
- Configurable currency mappings and warehouse settings.

## Installation

Theseus requires Python 3 (Developed on 3.11) and `pip`. Install dependencies using:

```sh
pip install click "gql[all]"
```

## Configuration

Theseus requires a config.yml file to define credentials and settings. Below is an example configuration:
```yaml
credentials:
  saleor_url: http://localhost:8000/graphql/
  app_token: XXXX

# Map a currency to a channel ID: (Consult the trunc.csv file to see how this is used.)
currencies:
  USD: <USD Channel ID>
  EUR: <EUR Channel ID>

uploader:
  warehouse_id: <warehouse_id>
  chunk_size: 25
```


```sh
python3 importer.py trunc.csv
```
