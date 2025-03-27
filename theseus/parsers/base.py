from ..types import Product
import json


class BaseParser:
    def makeEdjsDescription(self, description: str) -> str:
        return json.dumps(
            {
                "time": 1735178172938,
                "blocks": [
                    {
                        "id": "my-random-id",
                        "type": "paragraph",
                        "data": {"text": description},
                    }
                ],
                "version": "2.24.3",
            }
        )

    def parse_line(self, line: str) -> Product:
        raise Exception("Base class should never be called")
