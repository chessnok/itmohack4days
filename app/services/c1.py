import requests

from app.core.config import settings


class C1Uploader:
    @staticmethod
    async def upload_file(content):
        try:
            res = requests.post(settings.C1_UPLOAD_PATH, json =content)
            res.raise_for_status()
        except Exception as e:
            print(e)
            return False
        return True