import os

from dotenv import load_dotenv


# Load variables from the .env file
load_dotenv()


BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    """
    Main application configuration.
    """

    SECRET_KEY = os.getenv(
        "SECRET_KEY",
        "development-secret-key-change-before-deployment",
    )

    DEBUG = os.getenv("FLASK_DEBUG", "True").lower() == "true"

    DATABASE_PATH = os.path.join(
        BASE_DIR,
        "database",
        "faqflow.db",
    )

    UPLOAD_FOLDER = os.path.join(
        BASE_DIR,
        "static",
        "uploads",
    )

    MAX_CONTENT_LENGTH = 10 * 1024 * 1024

    ALLOWED_EXTENSIONS = {
        "txt",
        "pdf",
        "csv",
        "docx",
    }

    AI_API_KEY = os.getenv("AI_API_KEY", "")
    
    
