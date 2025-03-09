import numpy as np
import pandas as pd
import plotly.graph_objects as go

from app.services.plot.plot_interface import CreatePlotly
from app.services.accounting_time import AccountingTime


class BuyByDate(CreatePlotly):
    def __init__(
        self,
        accounting_time: AccountingTime,
        buy_ctl_data: pd.DataFrame,
        buy_data: pd.DataFrame,
        residual_income: int
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
        self._ctg_dict = self._buy_ctl_data.groupby("カテゴリー1", sort=False)["カテゴリー2"].apply(list).to_dict()
        self._residual_income = residual_income
        # time列がdatetime型に変換されているか確認
        if type(self._buy_data.iloc[0]["time"]) != pd.Timestamp:
            raise ValueError("time列がpd.Timestamp型になっていません")
        # データを会計期間に絞る
        interval = self._accounting_time.get_date_interval()
        self._buy_data = self._buy_data.loc[
            (interval[0] <= self._buy_data["time"]) &
            (self._buy_data["time"] < interval[1])
        ]

    def _get_buy_history(self) -> pd.Series:
        """
        累積の支出履歴を出力する

        Returns
        -------
        pd.DataFrame
            累積の支出履歴。indexに日時、valueに累積支出
        """
        buy_history = self._buy_data.sort_values(by="time").groupby("time").sum()["amount"]
        # 最初日、最終日を追加して、グラフが最終日まで表示されるようにする
        interval = self._accounting_time.get_date_interval()
        if buy_history.index.min() != interval[0]: # 既に初日に購入履歴があれば、0を追加しなくてい
            buy_history.loc[interval[0]] = 0
        buy_history.loc[interval[1]] = np.nan
        # 改めて日付順に並び替える
        buy_history = buy_history.sort_index()
        # 累積和を計算
        buy_sum_history = buy_history.cumsum()

        return buy_sum_history

    def _add_trace_plot(self, buy_sum_history):
        """
        累積支出のグラフを追加する

        Parameters
        ----------
        buy_sum_history : _type_
            累積支出の履歴
        """
        trace = go.Scatter(
            x=buy_sum_history.index,
            y=buy_sum_history.values,
            name="累積支出",
            marker_color="lightslategray",
            mode="lines+markers"
        )

        self._traces_data.append(trace_name="by_date_plot", trace=trace)

    def _add_trace_hline(self, buy_sum_history):
        """
        可処分所得のhlineを追加

        Parameters
        ----------
        buy_sum_history : _type_
            累積支出の履歴
        """
        trace = go.Scatter(
            x=buy_sum_history.index,
            y=[self._residual_income]*len(buy_sum_history),
            name="可処分所得",
            marker_color="crimson",
            mode="lines"
        )

        self._traces_data.append(trace_name="residual_income_hline", trace=trace)

    def traces(self) -> str[go.Trace]:
        """
        全てのtraceのリストを出力する

        Returns
        -------
        str[go.Trace]
            全てのtraceのリスト
        """
        buy_sum_history = self._get_buy_history()
        self._add_trace_plot(buy_sum_history=buy_sum_history)
        self._add_trace_hline(buy_sum_history=buy_sum_history)

        return self._traces_data.traces

    def layout(self) -> dict:
        """
        layoutを出力する

        Returns
        -------
        dict
            layout
        """
        return go.Layout(
            title=dict(text="今月の日別の使用額　\n期間：" + self._accounting_time.get_date_interval_str() + "　\n残り日数：" + str(self._accounting_time.get_days_left())),
            hovermode="x"
            )
