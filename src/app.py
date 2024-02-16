from flask import Flask, render_template, request

import numpy as np
import pandas as pd
from datetime import datetime

from handle_time import ThisMonth, ThisYear
from handle_spreadsheet import BuyControlSheet, BuyDataSheet, IncomeControlSheet, IncomeDataSheet, SavingControlSheet, SavingDataSheet
from calc_kpi import CalcMonthKPI, CalcYearKPI
from plotting import MonthBuyPlot, YearIncomePlot

import pdb

init_date = datetime.strptime("2022-04-01", "%Y-%m-%d")
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

def transform_date_from_ymd(year: str, month: str, day: str) -> str:
    """
    年-月-日の文字型に変換

    Parameters
    ----------
    year : str
        年
    month : str
        月
    day : str
        日

    Returns
    -------
    str
        年-月-日の文字型
    """
    if len(month) == 1:
        month = "0" + month
    if len(day) == 1:
        day = "0" + day

    return year + "-" + month + "-" + day

def get_history_year_month_list():
    # 現在の年月を取得
    this_month = ThisMonth()
    now_date = this_month.get_now_date()
    # データの最初の日付を取得
    first_date = init_date

    # first_dateからnow_dateまでの年月のリストを生成
    year_month_list = []

    # 現在の日付をfirst_dateから1ヶ月ずつ増やしていき、now_dateの年月までリストに追加する
    current_date = first_date
    while current_date <= now_date:
        year_month = current_date.strftime("%Y-%m")
        year_month_list.append(year_month)
        # 次の月へ
        if current_date.month == 12:
            current_date = datetime(current_date.year + 1, 1, 1)
        else:
            current_date = datetime(current_date.year, current_date.month + 1, 1)

    return year_month_list

def get_annual(date):
    if date < datetime(date.year, 4, 1):
        year = date.year - 1
    else:
        year = date.year

    return year

def get_history_year_list():
    # 現在の年次を取得
    this_year = ThisYear()
    now_date = this_year.get_now_date()
    now_year = get_annual(now_date)
    # データの最初の年次を取得
    first_date = init_date
    if first_date < datetime(first_date.year, 4, 1):
        first_year = first_date.year - 1
    else:
        first_year = first_date.year
    # first_dateからnow_dateまでの年月のリストを生成
    year_list = [str(int(x)) for x in np.arange(first_year, now_year+1, 1)]

    return year_list

def transform_datetime_from_str(date_str: str):
    if date_str == None:
        return datetime.now()
    elif len(date_str.split("-")) == 1:
        year = int(date_str)
        if year >= get_annual(datetime.now()):
            return datetime.now()
        else:
            return datetime.strptime(str(year+1)+"-03-31", "%Y-%m-%d")
    elif len(date_str.split("-")) == 2:
        if datetime.strptime(date_str+"-24", "%Y-%m-%d") >= datetime.now():
            return datetime.now()
        else:
            return datetime.strptime(date_str+"-24", "%Y-%m-%d")
    else:
        print("Error!!")

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
    # レポートの対象月を選択可能にする
    year_month_list = get_history_year_month_list()
    if request.method == "POST":
        year_month = request.form.get("month_selector")
    else:
        year_month = year_month_list[-1]
    now_date = transform_datetime_from_str(year_month)
    # 各KPIの取得
    calc_kpi = CalcMonthKPI(now_date=now_date)
    kpi_dict = {
        "income" : calc_kpi.calc_income() / 1000,
        "residual_income" : calc_kpi.calc_residual_income() / 1000,
        "saving" : calc_kpi.calc_saving() / 1000,
        "amount" : calc_kpi.calc_amount() / 1000,
        "budget" : (calc_kpi.calc_residual_income() - calc_kpi.calc_amount()) / 1000,
        "oir" : (calc_kpi.calc_amount() / calc_kpi.calc_residual_income()) * 100,
        "fixed_cost" : (calc_kpi.calc_fixed_cost()) / 1000,
        "variable_cost" : (calc_kpi.calc_variable_cost()) / 1000,
        "family_cost" : calc_kpi.calc_family_cost() / 1000,
        "work_book_cost": calc_kpi.calc_work_book_cost() / 1000,
        "engel_coefficient" : (calc_kpi.calc_engel_coefficient()) * 100,
        "extraordinary_cost" : calc_kpi.calc_extraordinary_cost() / 1000
    }

    graph_dict = {}
    # カテゴリ別支出レポートを作成
    month_buy_plot = MonthBuyPlot(now_date=now_date)
    month_amount_by_ctg_graph = month_buy_plot.month_amount_by_ctg()
    graph_dict["month_amount_by_ctg"] = month_amount_by_ctg_graph

    # 日別購入レポートを作成
    month_amount_by_date_graph = month_buy_plot.month_amount_by_date()
    graph_dict["month_amount_by_date"] = month_amount_by_date_graph

    return render_template("month_report.html", graph_dict=graph_dict, kpi_dict=kpi_dict, year_month_list=year_month_list, current_month=year_month)


### year report page ################################################################
@app.route("/move_year_report_page", methods=["GET", "POST"])
def move_html_year_report():
    # レポートの対象年を選択可能にする
    year_list = get_history_year_list()
    if request.method == "POST":
        year = request.form.get("year_selector")
    else:
        year = year_list[-1]
    now_date = transform_datetime_from_str(year)
    # 各KPIの取得
    calc_kpi = CalcYearKPI(now_date=now_date)
    kpi_dict = {
        "income" : calc_kpi.calc_income() / 1000,
        "residual_income" : calc_kpi.calc_residual_income() / 1000,
        "pred_income" : calc_kpi.calc_pred_income() / 1000,
        "saving" : calc_kpi.calc_saving() / 1000
    }

    graph_dict = {}
    # 年収グラフ
    year_income_plot = YearIncomePlot(now_date=now_date)
    year_income_by_month_graph = year_income_plot.year_income_by_month()
    graph_dict["year_income_by_month"] = year_income_by_month_graph

    # 収支グラフ
    year_income_and_outgo_by_month_graph = year_income_plot.year_income_and_outgo_by_month()
    graph_dict["year_income_and_outgo_by_month"] = year_income_and_outgo_by_month_graph

    # 貯金グラフ
    year_cumsum_saving_graph = year_income_plot.year_cumsum_saving()
    graph_dict["year_cumsum_saving"] = year_cumsum_saving_graph

    return render_template("year_report.html", graph_dict=graph_dict, kpi_dict=kpi_dict, year_list=year_list, current_year=year)


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