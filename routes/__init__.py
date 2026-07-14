"""
Routes Package
"""

from .auth_routes import auth_bp
from .dashboard_routes import dashboard_bp
from .faq_routes import faq_bp
from .chatbot_routes import chatbot_bp
from .api_routes import api_bp

__all__ = [
    "auth_bp",
    "dashboard_bp",
    "faq_bp",
    "chatbot_bp",
    "api_bp"
]