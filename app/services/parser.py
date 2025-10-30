import json
from typing import Dict, Any
from app.core.config import settings
from app.core.llm import llm_client


class Parser:
    def __init__(self):
        self.client = llm_client

        # Строгая JSON-схема
        self.json_schemas = {
            "Goods Shipment Note": {
                "type": "json_schema",
                "name": "GoodsShipmentNote",
                "strict": False,
                "schema": {
                    "type": "object",
                    "properties": {
                        "header": {
                            "type": "object",
                            "properties": {
                                "НомерДокумента": {
                                    "type": "string"
                                },
                                "ДатаСоставления": {
                                    "type": "string",
                                    "format": "date"
                                },
                                "Поставщик": {
                                    "type": "object",
                                    "properties": {
                                        "Наименование": {
                                            "type": "string"
                                        },
                                        "ИНН": {
                                            "type": "string"
                                        }
                                    }
                                },
                                "Плательщик": {
                                    "type": "object",
                                    "properties": {
                                        "Наименование": {
                                            "type": "string"
                                        },
                                        "ИНН": {
                                            "type": "string"
                                        }
                                    }
                                },
                                "Основание": {
                                    "type": "string"
                                }
                            }
                        },
                        "table": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "НомерПоПорядку": {
                                        "type": "string"
                                    },
                                    "НаименованиеТовара": {
                                        "type": "string"
                                    },
                                    "Код": {
                                        "type": [
                                            "string",
                                            "null"
                                        ]
                                    },
                                    "ЕдиницаИзмеренияНаименование": {
                                        "type": "string"
                                    },
                                    "ВидУпаковки": {
                                        "type": [
                                            "string",
                                            "null"
                                        ]
                                    },
                                    "КоличествоВОдномМесте": {
                                        "type": [
                                            "string",
                                            "null"
                                        ]
                                    },
                                    "КоличествоМестШтук": {
                                        "type": [
                                            "string",
                                            "null"
                                        ]
                                    },
                                    "МассаБрутто": {
                                        "type": [
                                            "string",
                                            "null"
                                        ]
                                    },
                                    "КоличествоМассаНетто": {
                                        "type": "string"
                                    },
                                    "ЦенаРубКоп": {
                                        "type": "string"
                                    },
                                    "СуммаБезУчетаНДС": {
                                        "type": "string"
                                    },
                                    "СтавкаНДС": {
                                        "type": [
                                            "string",
                                            "null"
                                        ]
                                    },
                                    "СуммаНДС": {
                                        "type": [
                                            "string",
                                            "null"
                                        ]
                                    },
                                    "СуммаСУчетомНДС": {
                                        "type": "string"
                                    },
                                    "Итого": {
                                        "type": "object",
                                        "properties": {
                                            "КоличествоМестШтук": {
                                                "type": "string"
                                            },
                                            "СуммаБезНДС": {
                                                "type": "string"
                                            },
                                            "СуммаСНДС": {
                                                "type": "string"
                                            }
                                        }
                                    },
                                    "ВсегоПоНакладной": {
                                        "type": "object",
                                        "properties": {
                                            "КоличествоМестШтук": {
                                                "type": "string"
                                            },
                                            "СуммаБезНДС": {
                                                "type": "string"
                                            },
                                            "СуммаСНДС": {
                                                "type": "string"
                                            }
                                        }
                                    }
                                }
                            }
                        },
                        "footer": {
                            "type": "object",
                            "properties": {
                                "Итого": {
                                    "type": "string"
                                },
                                "ВсегоПоНакладной": {
                                    "type": "string"
                                }
                            }
                        }
                    },
                    "additionalProperties": False
                }
            },
            "Invoice": {
                "type": "json_schema",
                "name": "Invoice",
                "strict": False,
                "schema": {
                    "type": "object",
                    "properties": {
                        "document_type": {
                            "type": "string",
                            "description": "The type of the document.",
                            "enum": [
                                "Invoice"
                            ]
                        },
                        "header": {
                            "type": "object",
                            "properties": {
                                "НомерДокумента": {
                                    "type": "string"
                                },
                                "ДатаДокумента": {
                                    "type": "string",
                                    "format": "date"
                                },
                                "Статус": {
                                    "type": "integer"
                                },
                                "Продавец": {
                                    "type": "object",
                                    "properties": {
                                        "Наименование": {
                                            "type": "string"
                                        },
                                        "Адрес": {
                                            "type": "string"
                                        },
                                        "ИНН": {
                                            "type": "string"
                                        },
                                        "КПП": {
                                            "type": "string"
                                        }
                                    }
                                },
                                "Покупатель": {
                                    "type": "object",
                                    "properties": {
                                        "Наименование": {
                                            "type": "string"
                                        },
                                        "Адрес": {
                                            "type": "string"
                                        },
                                        "ИНН": {
                                            "type": "string"
                                        },
                                        "КПП": {
                                            "type": "string"
                                        }
                                    }
                                },
                                "Валюта": {
                                    "type": "object",
                                    "properties": {
                                        "Наименование": {
                                            "type": "string"
                                        },
                                        "Код": {
                                            "type": "integer"
                                        }
                                    }
                                },
                                "Госконтракт": {
                                    "type": [
                                        "string",
                                        "null"
                                    ]
                                },
                                "ДополнительнаяИнформация": {
                                    "type": [
                                        "string",
                                        "null"
                                    ]
                                }
                            }
                        },
                        "table": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "ТипПозиции": {
                                        "type": "string",
                                        "enum": [
                                            "Товар",
                                            "Услуга"
                                        ]
                                    },
                                    "ПорядковыйНомер": {
                                        "type": "string"
                                    },
                                    "Наименование": {
                                        "type": "string"
                                    },
                                    "КодТНВЭД": {
                                        "type": [
                                            "string",
                                            "null"
                                        ]
                                    },
                                    "ЕдиницаИзмерения": {
                                        "type": "object",
                                        "properties": {
                                            "Код": {
                                                "type": "string"
                                            },
                                            "Наименование": {
                                                "type": "string"
                                            }
                                        }
                                    },
                                    "Количество": {
                                        "type": "string"
                                    },
                                    "Цена": {
                                        "type": "string"
                                    },
                                    "СтоимостьБезНалога": {
                                        "type": "string"
                                    },
                                    "Акциз": {
                                        "type": [
                                            "string",
                                            "null"
                                        ]
                                    },
                                    "НалоговаяСтавка": {
                                        "type": "string"
                                    },
                                    "СуммаНалога": {
                                        "type": "string"
                                    },
                                    "СтоимостьСНалогом": {
                                        "type": "string"
                                    },
                                    "СтранаПроисхождения": {
                                        "type": "object",
                                        "properties": {
                                            "Код": {
                                                "type": [
                                                    "string",
                                                    "null"
                                                ]
                                            },
                                            "Наименование": {
                                                "type": [
                                                    "string",
                                                    "null"
                                                ]
                                            }
                                        }
                                    },
                                    "НомерДекларации": {
                                        "type": [
                                            "string",
                                            "null"
                                        ]
                                    },
                                    "ВсегоКОплате": {
                                        "type": "object",
                                        "properties": {
                                            "СтоимостьБезНалогов": {
                                            },
                                            "Universal Correction Document": {}, "type": [
                                                "string",
                                                "null"
                                            ]
                                        },
                                        "СуммаНалогаПокупателю": {
                                            "type": [
                                                "string",
                                                "null"
                                            ]
                                        },
                                        "СтоимостьСНалогомВсего": {
                                            "type": [
                                                "string",
                                                "null"
                                            ]
                                        }
                                    }
                                }
                            }
                        }
                    }
                },
                "required": [
                    "document_type"
                ],
                "additionalProperties": False
            },
            "Universal Correction Document": {
                "type": "json_schema",
                "name": "Invoice",
                "strict": False,
                "schema": {
                    "type": "object",
                    "properties": {
                        "document_type": {
                            "type": "string",
                            "description": "The type of the document.",
                            "enum": ["Universal Correction Document"]
                        },
                        "header": {
                            "type": "object",
                            "properties": {
                                "НомерКорректировки": {"type": "string"},
                                "ДатаКорректировки": {"type": "string", "format": "date"},
                                "НомерИсходногоСФ": {"type": "string"},
                                "ДатаИсходногоСФ": {"type": "string", "format": "date"},
                                "Статус": {"type": "integer"},
                                "Продавец": {
                                    "type": "object",
                                    "properties": {
                                        "Наименование": {"type": "string"},
                                        "Адрес": {"type": "string"},
                                        "ИНН": {"type": "string"},
                                        "КПП": {"type": "string"}
                                    }
                                },
                                "Покупатель": {
                                    "type": "object",
                                    "properties": {
                                        "Наименование": {"type": "string"},
                                        "Адрес": {"type": "string"},
                                        "ИНН": {"type": "string"},
                                        "КПП": {"type": "string"}
                                    }
                                },
                                "Валюта": {
                                    "type": "object",
                                    "properties": {
                                        "Наименование": {"type": "string"},
                                        "Код": {"type": "integer"}
                                    }
                                },
                                "ОснованиеКоррекции": {"type": "string"},
                                "РеквизитыДоговора": {"type": "string"},
                                "ДополнительнаяИнформация": {"type": ["string", "null"]}
                            }
                        },
                        "table": {"type": "array", "items": {"type": "object"}},
                        "footer": {"type": "object"}
                    },
                    "required": ["document_type"],
                    "additionalProperties": False
                }
            }
        }

        # Системный промпт
        self.system_prompt = (
            "You are the most responsible chief accountant in the company with 40 years of experience. You must enter "
            "all the data in the document in the correct format. Skip any fields that are not there, and write what "
            "is there clearly in the format specified in the document, namely.\n"
            "Critical requirements:\n"
            "I. Accuracy of data transfer:\n"
            "- Transfer all values from the document exactly as they are specified:\n"
            "* Keep the original formatting (spaces, line breaks, punctuation marks)\n"
            "* Do not delete or add characters\n"
            "* Do not round numbers\n"
            "* Do not change the text case\n"
            "II. Technical requirements:\n"
            "- Numerical values as numbers (when possible)\n"
            "- Strict adherence to JSON structure\n"
            "III. Special instructions:\n"
            "- For goods, retain the original values of units of measurement and quantity\n"
            "- For services, retain the original spelling, even without units of measurement\n"
            "- For UKD, retain the original values in all substrings (A, B, C, D)\n"
            "- Responsible persons only in the footer (not in the table part)"
        )

    def parse(self, file_url: str, is_image, document_type: str) -> Dict[str, Any]:
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
            text={"format": self.json_schemas[document_type]},
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


parser_service = Parser()
