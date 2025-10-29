import json
from typing import Dict, Any

from langchain.output_parsers import StructuredOutputParser, ResponseSchema
from langchain_core.prompts import ChatPromptTemplate

from app.core.config import settings
from app.core.llm import llm_client


class Parser:
    def __init__(self):
        self.client=llm_client
        schemas = [
            ResponseSchema(name="document_type", description="Тип документа"),
            ResponseSchema(name="number", description="Номер документа"),
            ResponseSchema(name="date", description="Дата"),
            ResponseSchema(name="organization", description="Контрагент"),
            ResponseSchema(name="amount", description="Сумма"),
        ]
        self.json_schema = {
            "type": "object",
            "properties": {
                "document_type": {"type": "string", "description": "Тип документа"},
                "organization": {"type": "string", "description": "Контрагент"},
                "date": {"type": "string", "description": "Дата"},
                "number": {"type": "integer", "description": "Номер документа"},
                "amount": {"type": "integer", "description": "Сумма"},
            },
            "required": ["document_type", "organization","date","number","amount"]
        }

        self._parser = StructuredOutputParser.from_response_schemas(schemas)
        self._format_instructions = self._parser.get_format_instructions()

        self.prompt = ChatPromptTemplate.from_template(
            "Извлеки данные из текста документа.\n"
            "{format_instructions}\n\n"
            "Название файла:\n{filename}\n\n"
            "Текст:\n{document}\n"
        )

        self.prompt = self.prompt.partial(format_instructions=self._format_instructions)


    def extract_metadata(self, text: str, filename: str) -> Dict[str, Any]:
        selected_model = settings.LLM_MODEL

        # Выполнение запроса
        response = llm_client.chat.completions.create(
            response_format={"type": "json_schema", "json_schema": self.json_schema},
            model=selected_model,
            messages=[
                {"role": "user", "content": self.prompt.format(filename=filename, document=text)}
            ],
        )

        message = response.choices[0].message

        return message.content

parser_service = Parser()




