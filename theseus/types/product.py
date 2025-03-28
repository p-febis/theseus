from dataclasses import dataclass


@dataclass
class Currency:
    code: str
    value: float


@dataclass
class Product:
    name: str
    type_: str
    sku: str
    category: str
    currencies: list[Currency]
    quantity: int
    description: str
