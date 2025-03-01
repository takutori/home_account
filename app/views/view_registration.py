from flask import Blueprint, render_template

registration_app = Blueprint('registration', __name__)


### registration_buy page ###
@registration_app.route("/move_registration_buy_page", methods=["GET", "POST"])
def move_html_registration_buy():
    return render_template("registration_buy.html")


@registration_app.route('/input_buy', methods=['GET', 'POST'])
def input_buy():
    return render_template('registration_buy.html')

### registration_income page ###

@registration_app.route("/move_registration_income_page", methods=["GET", "POST"])
def move_html_registration_income():
    return render_template("registraion_income.html")


@registration_app.route('/input_income', methods=['GET', 'POST'])
def input_income():
    return render_template('registraion_income.html')


### registration_saving page ###

@registration_app.route("/move_registration_saving_page", methods=["GET", "POST"])
def move_html_registration_saving():
    return render_template("registraion_saving.html")


@registration_app.route('/input_saving', methods=['GET', 'POST'])
def input_saving():
    return render_template('registraion_saving.html')
