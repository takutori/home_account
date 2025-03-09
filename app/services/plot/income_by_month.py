import numpy as np
import pandas as pd
import plotly.graph_objects as go
from dateutil.relativedelta import relativedelta

from app.services.plot.plot_interface import CreatePlotly
from app.services.accounting_time import AccountingTime



class IncomeByMonth(CreatePlotly):
    def __init__(
        self,
        accounting_time: AccountingTime,
        income_ctl_data: pd.DataFrame,
        income_data: pd.DataFrame,
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
        self._income_ctl_data = income_ctl_data
        self._income_data = income_data
        # time列がdatetime型に変換されているか確認
        if type(self._income_data.iloc[0]["time"]) != pd.Timestamp:
            raise ValueError("time列がpd.Timestamp型になっていません")
        # データを会計期間に絞る
        interval = self._accounting_time.get_date_interval()
        self._income_data = self._income_data.loc[
            (interval[0] <= self._income_data["time"]) &
            (self._income_data["time"] < interval[1])
        ]

    def _get_income_ctg(self) -> list:
        """
        収入カテゴリーのリストを出力する

        Returns
        -------
        list
            収入カテゴリー
        """
        return self._income_ctl_data["収入カテゴリー"].tolist()[:-1]

    def _income_data_groupby_yearmonth_ctg(self) -> pd.DataFrame:
        """
        収入データに対して年-月とカテゴリーごとの足し算を実行する

        Returns
        -------
        pd.DataFrame
            収入データに対して年-月とカテゴリーごとの足し算した結果
        """
        self._income_data["year-month"] = self._income_data["time"].dt.strftime("%Y-%m-25")
        return self._income_data[["year-month", "category", "income"]].groupby(["year-month", "category"], as_index=False).sum()

    def _add_trace_income_by_ctg(self, ctg: str, income_data_groupby_yearmonth_ctg: pd.DataFrame):
        """
        月の売上の棒グラフを追加する。

        Parameters
        ----------
        ctg : str
            収入カテゴリー
        income_data_groupby_yearmonth_ctg : pd.DataFrame
            月-年とカテゴリーでgroupby.sumされたもの
        """
        plot_data = income_data_groupby_yearmonth_ctg.loc[
            income_data_groupby_yearmonth_ctg["category"] == ctg
            , income_data_groupby_yearmonth_ctg.columns.tolist()
            ]
        plot_data["time"] = pd.to_datetime(plot_data["year-month"], format="%Y-%m-%d")
        trace = go.Bar(
            x=plot_data["time"],
            y=plot_data["income"],
            name=ctg,
            visible=False,
        )

        self._traces_data.append(trace_name=f"income_by_month_{ctg}", trace=trace)

    def _add_trace_cumsum_income_by_ctg(self, ctg: str, income_data_groupby_yearmonth_ctg: pd.DataFrame):
        """
        月の累積売上の棒グラフを追加する。

        Parameters
        ----------
        ctg : str
            収入カテゴリー
        income_data_groupby_yearmonth_ctg : pd.DataFrame
            月-年とカテゴリーでgroupby.sumされたもの
        """
        plot_data = income_data_groupby_yearmonth_ctg.loc[
            income_data_groupby_yearmonth_ctg["category"] == ctg
            , income_data_groupby_yearmonth_ctg.columns.tolist()
            ]
        plot_data["time"] = pd.to_datetime(plot_data["year-month"], format="%Y-%m-%d")
        trace = go.Scatter(
            x=plot_data["time"],
            y=plot_data["income"].cumsum(),
            name=ctg,
            visible=True,
            fill="tozeroy"
        )

        self._traces_data.append(trace_name=f"cumsum_income_by_month_{ctg}", trace=trace)

    def _add_trace_cumsum_all_income(self, plot_data: pd.DataFrame):
        """
        月の全てのカテゴリーの累積売上の棒グラフを追加する。

        Parameters
        ----------
        income_data_groupby_yearmonth_ctg : pd.DataFrame
            月-年とカテゴリーでgroupby.sumされたもの
        """
        plot_data["time"] = pd.to_datetime(plot_data["year-month"], format="%Y-%m-%d")
        plot_data = plot_data[["time", "income"]].groupby("time", as_index=False).sum()
        trace = go.Scatter(
            x=plot_data["time"],
            y=plot_data["income"].cumsum(),
            name="合計",
            visible=True,
            fill="tozeroy"
        )

        self._traces_data.append(trace_name=f"cumsum_income_by_month_all", trace=trace)

    def traces(self) -> list[go.Trace]:
        """
        全てのtraceを追加し、リストにして出力する。

        Returns
        -------
        list[go.Trace]
            全てのtraceのリスト
        """
        income_ctg = self._get_income_ctg()
        income_data_groupby_yearmonth_ctg = self._income_data_groupby_yearmonth_ctg()
        for ctg in income_ctg:
            self._add_trace_income_by_ctg(
                ctg=ctg,
                income_data_groupby_yearmonth_ctg=income_data_groupby_yearmonth_ctg
                )
            self._add_trace_cumsum_income_by_ctg(
                ctg=ctg,
                income_data_groupby_yearmonth_ctg=income_data_groupby_yearmonth_ctg
                )
        self._add_trace_cumsum_all_income(
            plot_data=income_data_groupby_yearmonth_ctg
            )

        return self._traces_data.traces



    def layout(self) -> go.Layout:
        """
        figureに追加するレイアウト

        Returns
        -------
        go.Layout
            レイアウト設定
        """
        return go.Layout(
            title=dict(text="今年の月毎の給与　\n期間：" + self._accounting_time.get_date_interval_str()),
            updatemenus=self._updatemenus(),
            hovermode="x",
            barmode='stack'
            )

    def _buttons(self) -> dict:
        """
        ボタンを作成。具体的には以下の項目を設定する

        - 月ごとのincomeを棒グラフで
        - 月ごとの累積incomeを折れ線グラフで

        Returns
        -------
        dict
            ボタンの設定
        """
        buttons = []

        button_names = ["累積売上", "売上"]
        for button_name in button_names:
            if button_name == "累積売上":
                visible_trace_names = [f"cumsum_income_by_month_{ctg}" for ctg in self._get_income_ctg()] + ["cumsum_income_by_month_all"]
                visible_status = self._traces_data.get_bool_from_name(search_trace_names=visible_trace_names)
            elif button_name == "売上":
                visible_trace_names = [f"income_by_month_{ctg}" for ctg in self._get_income_ctg()]
                visible_status = self._traces_data.get_bool_from_name(search_trace_names=visible_trace_names)

            button_title = "今年の月毎の給与　\n期間：" + self._accounting_time.get_date_interval_str()
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
        ボタンを押したときにアップデートする内容を設定する。

        Returns
        -------
        dict
            ボタンを押した時の挙動の設定
        """
        return [
            dict(
                type="buttons", direction="right",
                x=0.5, y=1.01, xanchor='center', yanchor='bottom',
                active=0, buttons=self._buttons(),
                )
            ]
