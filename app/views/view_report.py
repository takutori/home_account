from flask import Blueprint, render_template

report_app = Blueprint('report', __name__)


### month plotting page ################################################################
@report_app.route("/move_month_report_page", methods=["GET", "POST"])
def move_html_month_report():
    return render_template("month_report.html")


### year report page ################################################################
@report_app.route("/move_year_report_page", methods=["GET", "POST"])
def move_html_year_report():
    return render_template("year_report.html")