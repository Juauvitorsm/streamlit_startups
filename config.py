import os
from dotenv import load_dotenv


load_dotenv()


API_URL = os.getenv("API_URL")


if not API_URL:
    raise ValueError("A variável de ambiente API_URL não está configurada.")
