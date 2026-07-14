from flask import Flask, render_template

from config import Config
from routes.auth_routes import auth_bp
from routes.dashboard_routes import dashboard_bp
from routes.faq_routes import faq_bp
from routes.chatbot_routes import chatbot_bp
from routes.api_routes import api_bp
from services.database_service import initialize_database


def create_app():
    """
    Create and configure the Flask application.
    """

    app = Flask(__name__)

    # Load configuration from config.py
    app.config.from_object(Config)

    # Create SQLite database tables
    initialize_database(app.config["DATABASE_PATH"])

    # Register route blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(faq_bp)
    app.register_blueprint(chatbot_bp)
    app.register_blueprint(api_bp)

    # Homepage
    @app.route("/")
    def index():
        return render_template("index.html")

    # Error pages
    @app.errorhandler(404)
    def page_not_found(error):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def internal_server_error(error):
        return render_template("errors/500.html"), 500

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=app.config["DEBUG"])