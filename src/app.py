from flask import Flask, render_template, request

from datetime import datetime

from handle_spreadsheet import BuyControlSheet, BuyDataSheet, IncomeControlSheet, IncomeDataSheet, SavingControlSheet, SavingDataSheet
from calc_kpi import CalcMonthKPI, CalcYearKPI
from plotting import MonthBuyPlot, YearIncomePlot

import pdb

app = Flask(__name__)

def get_ctg():
    ctg_dict = {}
    # 購買カテゴリ
    buy_ctl_sheet = BuyControlSheet()
    buy_ctg = buy_ctl_sheet.get_ctg_dict()
    ctg_dict["buy_ctg"] = buy_ctg
    # 収入カテゴリ
    income_ctl_sheet = IncomeControlSheet()
    income_ctg = income_ctl_sheet.get_income_ctg()
    ctg_dict["income_ctg"] = {i : income_ctg[i] for i in range(len(income_ctg))}
    # 貯金カテゴリ
    saving_ctl_sheet = SavingControlSheet()
    saving_ctg = saving_ctl_sheet.get_saving_ctg()
    ctg_dict["saving_ctg"] = {i : saving_ctg[i] for i in range(len(saving_ctg))}

    return ctg_dict


def transform_date_from_ymd(year, month, day):
    if len(month) == 1:
        month = "0" + month
    if len(day) == 1:
        day = "0" + day

    return year + "-" + month + "-" + day

### main page ################################################################
@app.route('/', methods=['GET'])
def get():
    """
    最初のページを表示
    """
    ctg_dict = get_ctg()
    return render_template('index.html')

@app.route('/', methods=['POST'])
def post():
    """
    最初のページを表示
    """
    return render_template('index.html')

### month plotting page ################################################################
@app.route("/move_month_report_page", methods=["GET", "POST"])
def move_html_month_report():
    # 各KPIの取得
    calc_kpi = CalcMonthKPI()
    kpi_dict = {
        "residual_income" : calc_kpi.calc_residual_income() / 1000,
        "amount" : calc_kpi.calc_amount() / 1000,
        "budget" : (calc_kpi.calc_residual_income() - calc_kpi.calc_amount()) / 1000,
        "oir" : (calc_kpi.calc_amount() / calc_kpi.calc_residual_income()) * 100,
        "fixed_cost" : (calc_kpi.calc_fixed_cost()) / 1000,
        "variable_cost" : (calc_kpi.calc_variable_cost()) / 1000,
        "saving_amount" : calc_kpi.saving_amount / 1000,
        "family_cost" : calc_kpi.calc_family_cost() / 1000,
        "work_book_cost": calc_kpi.calc_work_book_cost() / 1000,
        "engel_coefficient" : (calc_kpi.calc_engel_coefficient()) * 100,
        "extraordinary_cost" : calc_kpi.calc_extraordinary_cost() / 1000
    }

    report_name_dict = {}
    # カテゴリ別支出レポートを作成
    month_buy_plot = MonthBuyPlot()
    month_amount_by_ctg_report_name = month_buy_plot.month_amount_by_ctg()
    report_name_dict["month_amount_by_ctg"] = month_amount_by_ctg_report_name

    # 日別購入レポートを作成
    month_amount_by_date_report_name = month_buy_plot.month_amount_by_date()
    report_name_dict["month_amount_by_date"] = month_amount_by_date_report_name

    return render_template("month_report.html", report_name_dict=report_name_dict, kpi_dict=kpi_dict)


### year report page ################################################################
@app.route("/move_year_report_page", methods=["GET", "POST"])
def move_html_year_report():
    # 各KPIの取得
    calc_kpi = CalcYearKPI()
    kpi_dict = {
        "income" : calc_kpi.calc_income() / 1000,
        "residual_income" : calc_kpi.calc_residual_income() / 1000,
        "pred_income" : calc_kpi.calc_pred_income() / 1000
    }

    report_name_dict = {}
    # 年収グラフ
    year_income_plot = YearIncomePlot()
    year_income_by_month_report_name = year_income_plot.year_income_by_month()
    report_name_dict["year_income_by_month"] = year_income_by_month_report_name

    return render_template("year_report.html", report_name_dict=report_name_dict, kpi_dict=kpi_dict)


### saving report page ################################################################
@app.route("/move_saving_report_page", methods=["GET", "POST"])
def move_html_saving_report():
    # 各KPIの取得
    calc_kpi = CalcYearKPI()
    kpi_dict = {
        "income" : calc_kpi.calc_income() / 1000,
        "residual_income" : calc_kpi.calc_residual_income() / 1000,
        "pred_income" : calc_kpi.calc_pred_income() / 1000
    }

    report_name_dict = {}
    # 年収グラフ
    year_income_plot = YearIncomePlot()
    year_income_by_month_report_name = year_income_plot.year_income_by_month()
    report_name_dict["year_income_by_month"] = year_income_by_month_report_name

    return render_template("year_report.html", report_name_dict=report_name_dict, kpi_dict=kpi_dict)


### registration_buy page ################################################################

@app.route("/move_registration_buy_page", methods=["GET", "POST"])
def move_html_registration_buy():
    ctg_dict = get_ctg()

    return render_template("registration_buy.html", ctg_dict=ctg_dict)


@app.route('/input_buy', methods=['GET', 'POST'])
def input_buy():
    """
    購入金額を登録
    """
    # カテゴリーと金額をindex.htmlから取得
    """
    buy_ctg = request.form.get('buy_ctg')
    buy_amount = request.form.get('buy_amount')
    """

    buy_data_sheet = BuyDataSheet()
    for i in range(10):
        # 購入日の取得
        buy_year = request.form.get("buy_year_" + str(i))
        buy_month = request.form.get("buy_month_" + str(i))
        buy_day = request.form.get("buy_day_" + str(i))
        buy_date = transform_date_from_ymd(buy_year, buy_month, buy_day)

        buy_ctg_i = request.form.get("buy_ctg_" + str(i))
        buy_amount_i = request.form.get("buy_amount_" + str(i))

        if (buy_ctg_i != None) & (buy_amount_i != ""):
            # スプレッドシートに書き込み
            buy_data_sheet.input_buy(buy_date, buy_ctg_i, int(buy_amount_i))

    ctg_dict = get_ctg()

    return render_template('registration_buy.html', ctg_dict=ctg_dict)

### registration_income page ################################################################

@app.route("/move_registration_income_page", methods=["GET", "POST"])
def move_html_registration_income():
    ctg_dict = get_ctg()

    return render_template("registraion_income.html", ctg_dict=ctg_dict)


@app.route('/input_income', methods=['GET', 'POST'])
def input_income():
    """
    収入を登録
    """

    income_data_sheet = IncomeDataSheet()
    for i in range(3):
        # 受取日の取得
        income_year = request.form.get("income_year_" + str(i))
        income_month = request.form.get("income_month_" + str(i))
        income_day = request.form.get("income_day_" + str(i))
        income_date = transform_date_from_ymd(income_year, income_month, income_day)

        # カテゴリーと金額をindex.htmlから取得
        income_ctg = request.form.get('income_ctg_' + str(i))
        income_type = request.form.get("income_type_" + str(i))
        income = request.form.get('income_' + str(i))
        residual_income = request.form.get("residual_income_" + str(i))
        if (income_ctg != None) & (income != "") & (residual_income != ""):
            # スプレッドシートに書き込み
            income_data_sheet.input_income(income_date, income_ctg, income_type, int(income), int(residual_income))

    ctg_dict = get_ctg()

    return render_template('registraion_income.html', ctg_dict=ctg_dict)


### registration_saving page ################################################################

@app.route("/move_registration_saving_page", methods=["GET", "POST"])
def move_html_registration_saving():
    ctg_dict = get_ctg()

    return render_template("registraion_saving.html", ctg_dict=ctg_dict)


@app.route('/input_saving', methods=['GET', 'POST'])
def input_saving():
    """
    収入を登録
    """

    saving_data_sheet = SavingDataSheet()
    for i in range(10):
        # 受取日の取得
        saving_year = request.form.get("saving_year_" + str(i))
        saving_month = request.form.get("saving_month_" + str(i))
        saving_day = request.form.get("saving_day_" + str(i))
        saving_date = transform_date_from_ymd(saving_year, saving_month, saving_day)

        # カテゴリーと金額をindex.htmlから取得
        saving_ctg = request.form.get('saving_ctg_' + str(i))
        amount = request.form.get('amount_' + str(i))
        if (saving_ctg != None) & (amount != None):
            ctg = saving_ctg.split("-")[0]
            how_to_save = saving_ctg.split("-")[1]
            # スプレッドシートに書き込み
            saving_data_sheet.input_saving(saving_date, ctg, how_to_save, int(amount))

    ctg_dict = get_ctg()


    return render_template('registraion_saving.html', ctg_dict=ctg_dict)


if __name__ == "__main__":
    app.run()