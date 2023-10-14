import numpy as np
import pandas as pd
import pdb

import datetime
from dateutil.relativedelta import relativedelta

import plotly.graph_objects as go

from handle_spreadsheet import BuyControlSheet, BuyDataSheet, IncomeControlSheet, IncomeDataSheet
from handle_time import ThisMonth, ThisYear
from calc_kpi import CalcMonthKPI


class MonthBuyPlot:
    def __init__(self):

        # 今月のデータ(25日~24日)のみ所得 ########################################################################
        # 今月の日時情報を取得
        this_month = ThisMonth()
        self.date_format = this_month.get_date_format()
        self.now_date = this_month.get_now_date()
        self.date_interval = this_month.get_date_interval()
        # 期間の名前
        self.interval_name = self.date_interval[0].strftime(self.date_format) + "_" + self.date_interval[1].strftime(self.date_format)
        # 残り日数
        self.days_left = this_month.get_days_left()

        # 今月のデータだけに変更
        # 支出カテゴリーの取得
        buy_ctl_sheet = BuyControlSheet()
        self.buy_ctg = buy_ctl_sheet.get_ctg_dict()
        # 支出データの所得
        buy_data_sheet = BuyDataSheet()
        self.buy_df = buy_data_sheet.get_buy_df()
        self.buy_df["time"] = pd.to_datetime(self.buy_df["time"])
        self.buy_df = self.buy_df.loc[
            (self.date_interval[0] < self.buy_df["time"]) &
            (self.buy_df["time"] < self.date_interval[1])
        ]
        # 支出データの金額を整数型へ変換
        self.buy_df["amount"] = self.buy_df["amount"].astype(int)
        # 予算データの取得
        self.buy_ctl_data = buy_ctl_sheet.get_buy_ctl_data(col_range="ctl")

    def month_amount_by_ctg(self):
        """
        カテゴリー毎の支出グラフ
        """
        # plot type
        ## カテゴリー1の項目リスト作成
        ctg1_list = []
        for ctg_index in self.buy_ctg:
            ctg = self.buy_ctg[ctg_index]["カテゴリー" + str(1)]
            ctg1_list.append(ctg)
        ctg1_list = sorted(set(ctg1_list), key=ctg1_list.index)
        ctg2_dict = {ctg2 : [] for ctg2 in ctg1_list}
        plot_ctg_type = {"カテゴリー1" : ctg1_list}
        plot_ctg_type.update(ctg2_dict)
        ## カテゴリー2の項目リスト作成
        for ctg_index in self.buy_ctg:
            ctg1 = self.buy_ctg[ctg_index]["カテゴリー" + str(1)]
            ctg2 = self.buy_ctg[ctg_index]["カテゴリー" + str(2)]
            plot_ctg_type[ctg1].append(ctg2)
        ## 各データの保存
        plot_datas = {}
        for ctg_type in plot_ctg_type:
            if ctg_type == "カテゴリー1":
                ctg_level = 1
            else:
                ctg_level = 2
            ctg_list = plot_ctg_type[ctg_type]
            amount_list = []
            limit_list = []
            rate_list = []
            amount_hoverlist = []
            limit_hoverlist = []
            for ctg in ctg_list:
                ctg_data = self.buy_df[self.buy_df["category" + str(ctg_level)] == ctg]
                amount = ctg_data["amount"].astype(int).sum()
                amount_list.append(amount)
                limit_data = self.buy_ctl_data[self.buy_ctl_data["カテゴリー" + str(ctg_level)] == ctg]
                limit = limit_data["予算"].astype(float).sum()
                #limit = int(limit * 10000)
                limit = int(limit)
                limit_list.append(limit)
                if limit != 0:
                    rate = str(round(100*(amount / limit), 1)) + "%"
                else:
                    rate = "100>%"
                rate_list.append(rate)
                ## hovertext作成
                amount_hoverlist.append("支出：" + str(amount/1000) + "k" + "\n" + "割合:" + rate + "残金:" + str((limit - amount)/1000) + "k")
                limit_hoverlist.append("予算:" + str(limit/1000) + "k")
                plot_datas[ctg_type] = {"amount_data" : amount_list, "limit_data" : limit_list, "rate_data" : rate_list, "amount_hoverlist" : amount_hoverlist, "limit_hoverlist" : limit_hoverlist}

        ## plotの作成
        plots = []
        for ctg_type in plot_ctg_type:
            if ctg_type == "カテゴリー1":
                visible = True
            else:
                visible = False
            ## 予算グラフの作成
            limit_plot = go.Bar(
                x=plot_ctg_type[ctg_type],
                y=plot_datas[ctg_type]["limit_data"],
                marker_color=['lightslategray',] * len(plot_ctg_type[ctg_type]),
                name="予算",
                hovertext = plot_datas[ctg_type]["limit_hoverlist"],
                hovertemplate=None,
                visible=visible
                )
            ## 支出グラフの作成
            amount_plot = go.Bar(
                x=plot_ctg_type[ctg_type],
                y=plot_datas[ctg_type]["amount_data"],
                textposition="inside",
                text=plot_datas[ctg_type]["rate_data"],
                marker_color=["crimson",] * len(plot_ctg_type[ctg_type]),
                name="支出",
                hovertext = plot_datas[ctg_type]["amount_hoverlist"],
                hovertemplate=None,
                visible=visible
                )
            plots.append(limit_plot)
            plots.append(amount_plot)

        ## ボタンの作成
        buttons = []
        for ctg_type_index in range(len(plot_ctg_type)):
            visible = [False] * (2 * len(plot_ctg_type))
            visible[2*ctg_type_index] = True
            visible[2*ctg_type_index+1] = True
            ctg_name = list(plot_ctg_type.keys())[ctg_type_index]
            sum_amount = sum(plot_datas[ctg_name]["amount_data"])
            sum_limit = sum(plot_datas[ctg_name]["limit_data"])
            button_title = "今月の支出レポート　\n期間：" + self.interval_name + "　\n残り日数：" + str(self.days_left) + "　\n予算合計：" + str(sum_limit) + "　\n出費合計" + str(sum_amount)
            button = dict(
                label = ctg_name, method="update",
                args=[dict(visible=visible), dict(title=button_title)]
                )
            buttons.append(button)
        ## updatemenuの作成
        updatemenus = [
            dict(
                type="buttons", direction="right",
                x=0.5, y=1.01, xanchor='center', yanchor='bottom',
                active=0, buttons=buttons,
                )
            ]
        ## レイアウトデータの作成
        layout = go.Layout(
            title=dict(text="今月のカテゴリ別支出　\n期間：" + self.interval_name + "　\n残り日数：" + str(self.days_left)),
            updatemenus=updatemenus,
            barmode="overlay",
            hovermode="x"
            )

        ## figの作成
        fig = go.Figure(data=plots, layout=layout)
        report_name = "{}.html".format(self.interval_name)
        save_path_filename = "src/templates/reports/month_amount_by_ctg/"+report_name
        fig.write_html(save_path_filename)

        return report_name

    def month_amount_by_date(self):
        buy_history = self.buy_df.sort_values(by="time").groupby("time").sum()["amount"]
        # 最初日、最終日を追加して、グラフが最終日まで表示されるようにする
        if buy_history.index.min() != self.date_interval[0]: # 既に初日に購入履歴があれば、0を追加しなくてい
            buy_history.loc[self.date_interval[0]] = 0
        buy_history.loc[self.date_interval[1]] = np.nan
        # 改めて日付順に並び替える
        buy_history = buy_history.sort_index()
        # 累積和を計算
        buy_sum_history = buy_history.cumsum()

        plots = []
        time_series_plot = go.Scatter(
            x = buy_sum_history.index,
            y = buy_sum_history,
            marker_color = "lightslategray"
        )
        plots.append(time_series_plot)

        layout = go.Layout(
            title=dict(text="今月の日別の使用額　\n期間：" + self.interval_name + "　\n残り日数：" + str(self.days_left)),
            hovermode="x"
            )

        fig = go.Figure(data=plots, layout=layout)

        calc_kpi = CalcMonthKPI()
        residual_income = calc_kpi.calc_residual_income()
        fig.add_hline(residual_income, line_color="crimson")

        report_name = "{}.html".format(self.interval_name)
        save_path_filename = "src/templates/reports/month_amount_by_date/"+report_name
        fig.write_html(save_path_filename)

        return report_name


class YearIncomePlot:
    def __init__(self):
        # 今月の日時情報を取得
        this_year = ThisYear()
        self.now_date = this_year.get_now_date()
        self.date_format = this_year.get_date_format()
        self.date_interval = this_year.get_date_interval()
        # 今月を除く残りの月
        self.month_left = this_year.get_month_left()
        # 期間の名前
        self.interval_name = self.date_interval[0].strftime(self.date_format) + "_" + self.date_interval[1].strftime(self.date_format)

        # 収入データ
        income_data_sheet = IncomeDataSheet()
        self.all_income_df = income_data_sheet.get_income_df()
        # 日付をdatetime型へ
        self.all_income_df["time"] = pd.to_datetime(self.all_income_df["time"])
        # income, residual_incomeを数値データへ
        self.all_income_df["income"] = self.all_income_df["income"].astype(int)
        self.all_income_df["residual_income"] = self.all_income_df["residual_income"].astype(int)
        # 今年のデータのみにする
        self.income_df = self.all_income_df.loc[
            (self.date_interval[0] <= self.all_income_df["time"]) &
            (self.all_income_df["time"] < self.date_interval[1])
        ]

        # 収入カテゴリを取得
        income_ctl_sheet = IncomeControlSheet()
        self.income_ctg = income_ctl_sheet.get_income_ctg()
        # その他カテゴリを定義
        self.payday_dict = income_ctl_sheet.get_income_pay_day()
        self.permanent_income_ctg = [ctg for ctg in self.payday_dict if self.payday_dict[ctg] != "臨時"] # 恒久的に給与が与えられる会社
        self.bonus_type_dict = income_ctl_sheet.get_income_bonus_month()
        self.bonus_income_ctg = [ctg for ctg in self.bonus_type_dict if self.bonus_type_dict[ctg] != "なし"] # ボーナスのある会社


    def year_income_by_month(self):

        month_list = []
        month_income_dict = {ctg : [] for ctg in self.income_ctg}
        for plus_month in range(12):
            # 月の収入データを取得
            this_month_first = self.date_interval[0] + relativedelta(months=plus_month)
            next_month_first = self.date_interval[0] + relativedelta(months=plus_month+1)

            this_month_income_df = self.income_df.loc[
                (this_month_first <= self.income_df["time"]) &
                (self.income_df["time"] < next_month_first)
            ]

            # 月の収入を、会社毎に足し算
            for ctg in self.income_ctg:
                this_month_ctg_income_df = this_month_income_df.loc[this_month_income_df["category"] == ctg]
                if len(this_month_ctg_income_df) != 0:
                    month_income_dict[ctg].append(np.sum(this_month_ctg_income_df["income"]))
                else:
                    month_income_dict[ctg].append(np.nan)

            # 月を文字にして、month_listに追加しておく
            if str(this_month_first.month) == 1:
                xlabel = str(this_month_first.year) + "-" + "0" + str(this_month_first.month)
            else:
                xlabel = str(this_month_first.year) + "-" + str(this_month_first.month)
            month_list.append(xlabel)

        plots = []
        for ctg in self.income_ctg:
            plot = go.Bar(
                x = month_list,
                y = month_income_dict[ctg],
                name = ctg,
            )
            plots.append(plot)

        layout = go.Layout(
            title=dict(text="今年の月毎の給与　\n期間：" + self.interval_name),
            hovermode="x",
            barmode='stack'
            )

        fig = go.Figure(data=plots, layout=layout)

        report_name = "{}.html".format(self.interval_name)
        save_path_filename = "src/templates/reports/year_income_by_month/"+report_name
        fig.write_html(save_path_filename)

        return report_name



















