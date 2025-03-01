from flask import Flask
from app.views.view_index import index_app
from app.views.view_registration import registration_app
from app.views.view_report import report_app

def boot_app():
    app = Flask(__name__)

    # ビュー関数を登録
    app.register_blueprint(index_app)
    app.register_blueprint(registration_app)
    app.register_blueprint(report_app)

    return app