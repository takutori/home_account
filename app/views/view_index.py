from flask import Blueprint, render_template

index_app = Blueprint('index', __name__)

@index_app.route('/', methods=["GET"])
def index():
    return render_template('index.html')


### index page ################################################################
@index_app.route('/', methods=['GET'])
def get():
    """
    最初のページを表示
    """
    return render_template('index.html')

@index_app.route('/', methods=['POST'])
def post():
    """
    最初のページを表示
    """
    return render_template('index.html')







