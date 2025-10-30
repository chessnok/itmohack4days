import json
from typing import Dict, Any
from app.core.config import settings
from app.core.llm import llm_client


class Classifier:
    def __init__(self):
        self.client = llm_client

        self.json_schema = {
            "type": "json_schema",
            "name": "document_type",
            "strict": True,
            "schema": {
                "type": "object",
                "properties": {
                    "document_type": {
                        "type": "string",
                        "description": "The type of the document.",
                        "enum": [
                            "Universal Correction Document",
                            "Invoice",
                            "Goods Shipment Note",
                            "Garbage"
                        ]
                    }
                },
                "required": [
                    "document_type"
                ],
                "additionalProperties": False
            }
        }

        # Системный промпт
        self.system_prompt = (
            "You are the most responsible chief accountant in the company with 40 years of experience. "
            "You must determine the type of document from the following options: "
            "Universal Correction Document, Invoice, Goods Shipment Note, Other, Garbage."
        )

    def classify(self, file_url: str, is_image) -> Dict[str, Any]:
        selected_model = settings.LLM_MODEL
        file = {
            "type": "input_image",
            "image_url": file_url,
        } if is_image else {
            "type": "input_file",
            "file_url": file_url,
        }
        response = self.client.responses.parse(
            model=selected_model,
            text={"format": self.json_schema},
            input=[
                {
                    "role": "system",
                    "content": [
                        {"type": "input_text", "text": self.system_prompt},
                    ],
                },
                {
                    "role": "user",
                    "content": [
                        file
                    ]
                }
            ]
        )
        return json.loads(response.output[0].content[0].text)


classifier_service = Classifier()
