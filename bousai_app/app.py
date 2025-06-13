from flask import Flask
from config.config import SECRET_KEY, DEBUG, PORT
from controllers.controller import main_bp, auth_bp, shelter_bp, api_bp

def create_app():
    """Flaskアプリケーションファクトリ"""
    app = Flask(__name__)
    app.secret_key = SECRET_KEY
    
    # Blueprintの登録
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(shelter_bp)
    app.register_blueprint(api_bp, url_prefix='/api')
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=DEBUG, port=PORT) 