import numpy as np
import pandas as pd
import pdb

import datetime

import plotly.graph_objects as go

from handle_spreadsheet import BuyControlSheet, BuyDataSheet, ThisMonth
from calc_kpi import CalcKPI


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

        calc_kpi = CalcKPI()
        residual_income = calc_kpi.calc_residual_income()
        fig.add_hline(residual_income, line_color="crimson")

        report_name = "{}.html".format(self.interval_name)
        save_path_filename = "src/templates/reports/month_amount_by_date/"+report_name
        fig.write_html(save_path_filename)

        return report_name



















