import numpy as np
import pandas as pd
import plotly.graph_objects as go
from dateutil.relativedelta import relativedelta

from app.services.plot.plot_interface import CreatePlotly
from app.services.accounting_time import AccountingTime



class IncomeOutgoByMonth(CreatePlotly):
    def __init__(
        self,
        accounting_time: AccountingTime,
        buy_ctl_data: pd.DataFrame,
        buy_data: pd.DataFrame,
        income_ctl_data: pd.DataFrame,
        income_data: pd.DataFrame,
        saving_data: pd.DataFrame,
        ):
        """
        コンストラクタ

        Parameters
        ----------
        accounting_time : AccountingTime
            会計期間。グラフのデータ自体には適用されず、グラフのタイトルなどに使用される。
        buy_ctl_data : pd.DataFrame
            支出管理データ
        buy_data : pd.DataFrame
            支出データ
        """
        # buy_dataを受け取る際、全て受け取ってコンストラクタで会計期間に絞ることも考えたが、
        # そうすると、他のクラスでも会計期間のに絞られているかの単体テストを実施する必要があるため、
        # raisesチェックのみにした。
        super().__init__(accounting_time=accounting_time)
        self._buy_ctl_data = buy_ctl_data
        self._buy_data = buy_data
        self._income_ctl_data = income_ctl_data
        self._income_data = income_data
        self._saving_data = saving_data
        # time列がdatetime型に変換されているか確認
        if (type(self._income_data.iloc[0]["time"]) != pd.Timestamp) or (type(self._buy_data.iloc[0]["time"]) != pd.Timestamp):
            raise ValueError("time列がpd.Timestamp型になっていません")
        # データを会計期間に絞る
        interval = self._accounting_time.get_date_interval()
        self._buy_data = self._buy_data.loc[
            (interval[0] <= self._buy_data["time"]) &
            (self._buy_data["time"] < interval[1])
        ]
        self._income_data = self._income_data.loc[
            (interval[0] <= self._income_data["time"]) &
            (self._income_data["time"] < interval[1])
        ]
        self._saving_data = self._saving_data.loc[
            (interval[0] <= self._income_data["time"]) &
            (self._saving_data["time"] < interval[1])
        ]

    def _get_diff_from_limit(self) -> pd.DataFrame:
        """
        予算と支出の月ごとの差を持つデータを出力

        Returns
        -------
        pd.DataFrame
            予算と支出の差のデータ
        """
        self._buy_data["year-month"] = self._buy_data["time"].dt.strftime("%Y-%m-25")
        monthly_buy = self._buy_data[["year-month", "amount"]].groupby("year-month", as_index=False).sum()
        monthly_buy["diff"] = monthly_buy["amount"] - self._buy_ctl_data["予算"].sum()
        monthly_buy["cumsum_diff"] = monthly_buy["diff"].cumsum()
        monthly_buy["time"] = pd.to_datetime(monthly_buy["year-month"], format="%Y-%m-%d")

        return monthly_buy

    def _add_trace_diff_from_limit(self, diff_from_limit: pd.DataFrame):
        """
        予算と支出の差の月ごとの棒グラフを追加する。

        Parameters
        ----------
        diff_from_limit : pd.DataFrame
            予算と支出の差のデータ
        """
        trace = go.Bar(
            x=diff_from_limit["time"],
            y=diff_from_limit["diff"],
            name="差分",
            visible=True,
            marker_color=["#636EFA" if  x > 0 else "#EF553B" for x in diff_from_limit["diff"]]
        )

        self._traces_data.append(trace_name="diff_from_limit", trace=trace)

    def _add_trace_cumsum_diff_from_limit(self, diff_from_limit: pd.DataFrame):
        """
        予算と支出の差の月ごとの累積の棒グラフを追加する。

        Parameters
        ----------
        diff_from_limit : pd.DataFrame
            予算と支出の差のデータ
        """
        if diff_from_limit.iloc[-1]["cumsum_diff"] > 0:
            color = "lime"
        else:
            color = "red"
        trace = go.Scatter(
            x=diff_from_limit["time"],
            y=diff_from_limit["cumsum_diff"],
            name="累積差分",
            visible=True,
            marker_color=color
        )

        self._traces_data.append(trace_name="cumsum_diff_from_limit", trace=trace)

    def _get_diff_from_residual_income(self) -> pd.DataFrame:
        """
        可処分所得と支出の月ごとの差を持つデータを出力

        Returns
        -------
        pd.DataFrame
            可処分所得と支出の差のデータ
        """
        self._buy_data["year-month"] = self._buy_data["time"].dt.strftime("%Y-%m-25")
        monthly_buy = self._buy_data[["year-month", "amount"]].groupby("year-month", as_index=False).sum()
        monthly_buy.columns = ["year-month", "buy-amount"]

        self._saving_data["year-month"] = self._saving_data["time"].dt.strftime("%Y-%m-25")
        monthly_saving = self._saving_data[["year-month", "amount"]].groupby("year-month", as_index=False).sum()
        monthly_saving.columns = ["year-month", "saving-amount"]

        self._income_data["year-month"] = self._income_data["time"].dt.strftime("%Y-%m-25")
        monthly_income = self._income_data[["year-month", "residual_income"]].groupby("year-month", as_index=False).sum()
        monthly_income.columns = ["year-month", "residual-income"]

        diff_df = pd.merge(monthly_buy, monthly_saving, on="year-month", how="left").fillna(0)
        diff_df = pd.merge(diff_df, monthly_income, on="year-month", how="left").fillna(0)
        diff_df["diff"] = diff_df["residual-income"] - diff_df["saving-amount"] - diff_df["buy-amount"]
        diff_df["cumsum_diff"] = diff_df["diff"].cumsum()
        diff_df["time"] = pd.to_datetime(diff_df["year-month"], format="%Y-%m-%d")

        return diff_df

    def _add_trace_diff_from_residual_income(self, diff_from_residual_income: pd.DataFrame):
        """
        可処分所得と支出の差の月ごとの棒グラフを追加する。

        Parameters
        ----------
        diff_from_limit : pd.DataFrame
            可処分所得と支出の差のデータ
        """
        trace = go.Bar(
            x=diff_from_residual_income["time"],
            y=diff_from_residual_income["diff"],
            name="差分",
            visible=False,
            marker_color=["#636EFA" if  x > 0 else "#EF553B" for x in diff_from_residual_income["diff"]]
        )

        self._traces_data.append(trace_name="diff_from_residual_income", trace=trace)

    def _add_trace_cumsum_diff_from_residual_income(self, diff_from_residual_income: pd.DataFrame):
        """
        可処分所得と支出の差の月ごとの累積の棒グラフを追加する。

        Parameters
        ----------
        diff_from_limit : pd.DataFrame
            可処分所得と支出の差のデータ
        """
        if diff_from_residual_income.iloc[-1]["cumsum_diff"] > 0:
            color = "lime"
        else:
            color = "red"
        trace = go.Scatter(
            x=diff_from_residual_income["time"],
            y=diff_from_residual_income["cumsum_diff"],
            name="累積差分",
            visible=False,
            marker_color=color
        )

        self._traces_data.append(trace_name="cumsum_diff_from_residual_income", trace=trace)

    def traces(self) -> list[go.Trace]:
        """
        全てのtraceを作成し、リストで出力する

        Returns
        -------
        list[go.Trace]
            全てのtraceのリスト
        """
        diff_from_limit = self._get_diff_from_limit()
        self._add_trace_diff_from_limit(diff_from_limit=diff_from_limit)
        self._add_trace_cumsum_diff_from_limit(diff_from_limit=diff_from_limit)
        diff_from_residual_income = self._get_diff_from_residual_income()
        self._add_trace_diff_from_residual_income(diff_from_residual_income=diff_from_residual_income)
        self._add_trace_cumsum_diff_from_residual_income(diff_from_residual_income=diff_from_residual_income)

        return self._traces_data.traces

    def layout(self) -> go.Layout:
        """
        layoutを出力する。

        Returns
        -------
        go.Layout
            設定したレイアウト
        """
        return go.Layout(
            title=dict(text="今年の月毎の収支　\n期間：" + self._accounting_time.get_date_interval_str()),
            updatemenus=self._updatemenus(),
            hovermode="x",
            barmode='stack'
            )

    def _buttons(self) -> dict:
        """
        ボタンを作成。具体的には以下の項目を設定する

        - 支出との差を測るのに予算を使用する
        - 支出との差を測るのに可処分所得を使用する

        Returns
        -------
        dict
            ボタンの設定
        """
        buttons = []

        button_names = ["予算", "可処分所得"]
        for button_name in button_names:
            if button_name == "予算":
                visible_trace_names = ["diff_from_limit", "cumsum_diff_from_limit"]
                visible_status = self._traces_data.get_bool_from_name(search_trace_names=visible_trace_names)
            elif button_name == "可処分所得":
                visible_trace_names = ["diff_from_residual_income", "cumsum_diff_from_residual_income"]
                visible_status = self._traces_data.get_bool_from_name(search_trace_names=visible_trace_names)

            button_title = "今年の月毎の収支　\n期間：" + self._accounting_time.get_date_interval_str()
            button = dict(
                label = button_name, method="update",
                args=[
                    {"visible": visible_status},
                    {"title": button_title}
                    ]
                )
            buttons.append(button)

        return buttons

    def _updatemenus(self) -> dict:
        """
        ボタンを押した時にグラフをアップデートするための設定

        Returns
        -------
        dict
            updatemenus
        """
        return [
            dict(
                type="buttons", direction="right",
                x=0.5, y=1.01, xanchor='center', yanchor='bottom',
                active=0, buttons=self._buttons(),
                )
            ]