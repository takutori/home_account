import numpy as np
import pandas as pd

from dateutil.relativedelta import relativedelta

import plotly.graph_objects as go
import plotly.io as pio

from app.models.gspread_workbook import BuyControlSheet, BuyDataSheet, IncomeControlSheet, IncomeDataSheet, SavingControlSheet, SavingDataSheet
from app.services.accounting_interval import ThisMonth, ThisYear
from calc_kpi import CalcMonthKPI




class YearIncomePlot:
    def __init__(self, now_date):
        # 今月の日時情報を取得
        this_year = ThisYear(now_date)
        self.now_date = this_year.get_now_date()
        self.date_format = this_year.get_date_format()
        self.date_interval = this_year.get_date_interval()
        # 今月を除く残りの月
        self.month_left = this_year.get_month_left()
        # 期間の名前
        self.interval_name = self.date_interval[0].strftime(self.date_format) + "_" + self.date_interval[1].strftime(self.date_format)
        # 支出カテゴリーの取得 #########################################################################
        buy_ctl_sheet = BuyControlSheet()
        self.buy_ctg = buy_ctl_sheet.get_ctg_dict()
        # 支出データの所得
        buy_data_sheet = BuyDataSheet()
        self.buy_df = buy_data_sheet.get_buy_df()
        self.buy_df["time"] = pd.to_datetime(self.buy_df["time"])
        # 今年のデータだけに変更
        self.buy_df = self.buy_df.loc[
            (self.date_interval[0] < self.buy_df["time"]) &
            (self.buy_df["time"] <= self.date_interval[1])
        ]
        # 支出データの金額を整数型へ変換
        self.buy_df["amount"] = self.buy_df["amount"].astype(int)
        # 予算データの取得
        self.buy_ctl_data = buy_ctl_sheet.get_buy_ctl_data(col_range="ctl")
        self.buy_ctl_data["予算"] = self.buy_ctl_data["予算"].astype(int)

        # 収入データ ########################################################################
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

        # 貯金データを取得 ################################################################
        saving_ctl_sheet = SavingControlSheet()
        self.saving_ctg_data = saving_ctl_sheet.get_saving_ctl_data()

        saving_data_sheet = SavingDataSheet()
        self.saving_data = saving_data_sheet.get_saving_df()
        self.saving_data["time"] = pd.to_datetime(self.saving_data["time"])
        self.saving_data["amount"] = self.saving_data["amount"].astype(int)

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
            trace = go.Bar(
                x = month_list,
                y = month_income_dict[ctg],
                name = ctg,
            )
            plots.append(trace)

        layout = go.Layout(
            title=dict(text="今年の月毎の給与　\n期間：" + self.interval_name),
            hovermode="x",
            barmode='stack'
            )

        fig = go.Figure(data=plots, layout=layout)

        return pio.to_html(fig, full_html=False)

    def year_income_and_outgo_by_month(self):

        month_list = []
        amount_list = []
        all_budget_list = []
        budget_list = []
        for plus_month in range(12):
            # 月の支出を取得
            this_month_first = self.date_interval[0] + relativedelta(months=plus_month)
            this_month = ThisMonth(now_date=this_month_first)
            date_interval = this_month.get_date_interval()

            this_month_buy_df = self.buy_df.loc[
                (date_interval[0] <= self.buy_df["time"]) &
                (self.buy_df["time"] < date_interval[1])
            ]
            this_month_amount = np.sum(this_month_buy_df["amount"])
            amount_list.append(this_month_amount)
            # 月の予算を計算
            this_month_budget = np.sum(self.buy_ctl_data["予算"])
            if this_month_amount == 0: # 支出データが存在しない場合
                this_month_budget = 0
            budget_list.append(this_month_budget)
            # 月の手取り-貯金額を計算
            this_month_income = self.income_df.loc[
                (date_interval[0] <= self.income_df["time"]) &
                (self.income_df["time"] < date_interval[1])
            ]
            residual_income = np.sum(this_month_income["residual_income"])
            this_month_saving = self.saving_data.loc[
                (date_interval[0] <= self.saving_data["time"]) &
                (self.saving_data["time"] < date_interval[1])
            ]
            saving = np.sum(this_month_saving["amount"])
            if saving < 0:
                saving = 0
            all_budget_list.append(residual_income - saving - this_month_amount)
            # 月を文字にして、month_listに追加しておく
            if str(this_month_first.month) == 1:
                xlabel = str(this_month_first.year) + "-" + "0" + str(this_month_first.month)
            else:
                xlabel = str(this_month_first.year) + "-" + str(this_month_first.month)
            month_list.append(xlabel)

        income_outgo_list = [budget - amount for budget, amount in zip(budget_list, amount_list)]
        plots = []
        trace = go.Bar(
            x = month_list,
            y = income_outgo_list,
            marker_color = ["#636EFA" if  x > 0 else "#EF553B" for x in income_outgo_list],
            visible = True
        )
        plots.append(trace)
        trace = go.Bar(
            x = month_list,
            y = all_budget_list,
            marker_color = ["#636EFA" if  x > 0 else "#EF553B" for x in all_budget_list],
            visible = False
        )
        plots.append(trace)
        # 可処分所得の残金の累積
        cumsum_all_budget_array = np.cumsum(all_budget_list)
        if cumsum_all_budget_array[-1] > 0:
            color="lime"
        else:
            color="red"
        trace = go.Scatter(
            x = month_list,
            y = cumsum_all_budget_array,
            marker_color = color,
            visible = False
        )
        plots.append(trace)
        ## ボタンの作成
        buttons = []
        button = dict(
            label="予算", method="update",
            args=[
                dict(visible=[True, False, False]),
                dict(title="予算")
            ]
        )
        buttons.append(button)
        button = dict(
            label="可処分所得", method="update",
            args=[
                dict(visible=[False, True, True]),
                dict(title="貯金額を除いた可処分所得")
            ]
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

        layout = go.Layout(
            title=dict(text="今年の月毎の収支　\n期間：" + self.interval_name),
            updatemenus=updatemenus,
            hovermode="x",
            barmode='stack'
            )

        fig = go.Figure(data=plots, layout=layout)

        return pio.to_html(fig, full_html=False)

    def year_cumsum_saving(self):
        # 貯金カテゴリを取得
        saving_ctg_list = self.saving_ctg_data["貯金項目"].unique().tolist()
        saving_how_to_save_list = self.saving_ctg_data["貯金方法"].unique().tolist()

        month_list = []
        # グラフの値の初期化
        saving_dict = {"all_saving" : []}
        for i in saving_ctg_list + saving_how_to_save_list:
            saving_dict[i] = []
        for ctg in saving_ctg_list:
            for how_to in saving_how_to_save_list:
                saving_dict[ctg+"-"+how_to] = []
        # グラフの値の計算
        for plus_month in range(12):
            this_month_first = self.date_interval[0] + relativedelta(months=plus_month)
            this_month = ThisMonth(now_date=this_month_first)
            date_interval = this_month.get_date_interval()

            if self.now_date < date_interval[0]: # 現在の日時より先の貯金額はnp.nanとする。
                saving_dict["all_saving"].append(np.nan)
                for ctg in saving_ctg_list:
                    saving_dict[ctg].append(np.nan)
                # 貯金方法での貯金合計
                for how_to in saving_how_to_save_list:
                    saving_dict[how_to].append(np.nan)
            else:
                # 今月の合計金額を計算
                if plus_month == 0:
                    this_month_saving_data = self.saving_data.loc[(self.saving_data["time"] <= date_interval[0])]
                else:
                    this_month_saving_data = self.saving_data.loc[(
                        (date_interval[0] <= self.saving_data["time"]) &
                        (self.saving_data["time"] < date_interval[1])
                    )]

                # 貯金の合計
                all_saving = np.sum(this_month_saving_data["amount"])
                saving_dict["all_saving"].append(all_saving)
                # 各カテゴリでの貯金合計
                for ctg in saving_ctg_list:
                    ctg_saving = np.sum(this_month_saving_data.loc[this_month_saving_data["category"] == ctg, "amount"])
                    saving_dict[ctg].append(ctg_saving)
                # カテゴリでの貯金方法の貯金合計
                for ctg in saving_ctg_list:
                    for how_to in saving_how_to_save_list:
                        ctg_howto_saving = np.sum(this_month_saving_data.loc[
                            (this_month_saving_data["category"] == ctg) &
                            (this_month_saving_data["how_to_save"] == how_to)
                        , "amount"])
                        saving_dict[ctg+"-"+how_to].append(ctg_howto_saving)
                # 貯金方法での貯金合計
                for how_to in saving_how_to_save_list:
                    how_to_saving = np.sum(this_month_saving_data.loc[this_month_saving_data["how_to_save"] == how_to, "amount"])
                    saving_dict[how_to].append(how_to_saving)

            # 月を文字にして、month_listに追加しておく
            if str(this_month_first.month) == 1:
                xlabel = str(this_month_first.year) + "-" + "0" + str(this_month_first.month)
            else:
                xlabel = str(this_month_first.year) + "-" + str(this_month_first.month)
            month_list.append(xlabel)

        # 貯金額を累積和にする。
        for key, value in saving_dict.items():
            saving_dict[key] = np.cumsum(value).tolist()

        graph_name_list = []
        plots = []
        # 合計貯金のグラフ
        trace = go.Scatter(
            x = month_list,
            y = saving_dict["all_saving"],
            #marker_color = "blue",
            mode = "lines+markers",
            name = "合計金額",
            visible = True,
            fill = "tozeroy"
        )
        plots.append(trace)
        graph_name_list.append("all_saving")
        # 各カテゴリのグラフ
        for ctg in saving_ctg_list:
            trace = go.Scatter(
                x = month_list,
                y = saving_dict[ctg],
                #marker_color = "blue",
                mode = "lines+markers",
                name = ctg,
                visible = True,
                fill = "tozeroy"
            )
            plots.append(trace)
            graph_name_list.append(ctg)
        # 各カテゴリ-貯金方法のグラフ
        for ctg in saving_ctg_list:
            for how_to in saving_how_to_save_list:
                trace = go.Scatter(
                    x = month_list,
                    y = saving_dict[ctg+"-"+how_to],
                    #marker_color = "blue",
                    mode = "lines+markers",
                    name = ctg + "-" + how_to,
                    visible = False,
                    fill = "tozeroy"
                )
                plots.append(trace)
                graph_name_list.append(ctg+"-"+how_to)
        # 各貯金方法のグラフ
        for how_to in saving_how_to_save_list:
            trace = go.Scatter(
                x = month_list,
                y = saving_dict[how_to],
                #marker_color = "blue",
                mode = "lines+markers",
                name = how_to,
                visible = False,
                fill = "tozeroy"
            )
            plots.append(trace)
            graph_name_list.append(how_to)

        ## ボタンの作成
        buttons = []
        for button_name in ["貯金額合計"] + saving_ctg_list + saving_how_to_save_list:
            visible = [False] * len(plots)
            if button_name == "貯金額合計":
                visible[graph_name_list.index("all_saving")] = True
                for ctg in saving_ctg_list: # 貯金額合計では、各貯金項目のグラフも表示
                    visible[graph_name_list.index(ctg)] = True
            elif saving_ctg_list.count(button_name) == 1:
                visible[graph_name_list.index(button_name)] = True
                for how_to in saving_how_to_save_list:
                    visible[graph_name_list.index(button_name+"-"+how_to)] = True
            else:
                visible[graph_name_list.index(button_name)] = True

            button_title = "今年度の「" + button_name + "」　\n期間：" + self.interval_name
            button = dict(
                label = button_name, method="update",
                args=[
                    dict(visible=visible),
                    dict(title=button_title),
                ]
            )
            buttons.append(button)
        # 全部のグラフを表示
        visible = [True] * len(saving_dict)
        button_title = "今年度の「全ての貯金項目」　\n期間：" + self.interval_name
        button = dict(
            label = "全カテゴリー", method="update",
            args=[
                dict(visible=visible),
                dict(title=button_title),
            ]
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
            title=dict(text="今年度の「貯金額合計」　\n期間：" + self.interval_name),
            updatemenus=updatemenus,
            barmode="overlay",
            hovermode="x",
            )

        ## figの作成
        fig = go.Figure(data=plots, layout=layout)

        fig.update_yaxes(autorange=False, range=[-(np.nanmax(saving_dict["all_saving"])*0.1), np.nanmax(saving_dict["all_saving"])*1.1])

        return pio.to_html(fig, full_html=False)