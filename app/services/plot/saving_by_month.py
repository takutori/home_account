from typing import Literal
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from dateutil.relativedelta import relativedelta

from app.services.plot.plot_interface import CreatePlotly
from app.services.accounting_time import AccountingTime



class SavingByMonth(CreatePlotly):
    def __init__(
        self,
        accounting_time: AccountingTime,
        saving_ctl_data: pd.DataFrame,
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
        self._saving_ctl_data = saving_ctl_data
        self._saving_data = saving_data
        # time列がdatetime型に変換されているか確認
        if type(self._saving_data.iloc[0]["time"]) != pd.Timestamp:
            raise ValueError("time列がpd.Timestamp型になっていません")
        # データを会計期間に絞る
        interval = self._accounting_time.get_date_interval()
        self._saving_data = self._saving_data.loc[
            (interval[0] <= self._saving_data["time"]) &
            (self._saving_data["time"] < interval[1])
        ]

    def _get_ctg_list(self) -> list[str]:
        """
        貯金カテゴリーのリストを出力する

        Returns
        -------
        list
            貯金カテゴリーのリスト
        """
        return self._saving_ctl_data["貯金項目"].unique().tolist()

    def _get_how_list(self) -> list[str]:
        """
        貯金方法のリストを出力する

        Returns
        -------
        list
            貯金方法のリスト
        """
        return self._saving_ctl_data["貯金方法"].unique().tolist()

    def _get_ctg_how_list(self) -> list[str]:
        """
        貯金項目-貯金方法の形で全ての組み合わせをリストとして出力

        Returns
        -------
        list[str]
            貯金項目-貯金方法のリスト
        """
        return (self._saving_ctl_data["貯金項目"] + "-" + self._saving_ctl_data["貯金方法"]).tolist()

    def _add_first_data_and_now_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        会計期間の最初の月と現在の月に貯金額0で全ての項目-方法の組み合わせだけデータを追加する。
        こうすることでplotした時に最初の月に貯金をしていない項目も0からplotが始ま流。
        また、現在の月で貯金をしていない項目も、現在の月までplotの点が入る。

        Parameters
        ----------
        data : pd.DataFrame
            追加されるデータ

        Returns
        -------
        pd.DataFrame
            追加したデータ
        """
        ctg_how_list = self._get_ctg_how_list()
        interval = self._accounting_time.get_date_interval()
        accounting_start = interval[0].strftime(format=self._accounting_time.date_format)
        now_date = self._accounting_time.now_date.strftime(format=self._accounting_time.date_format)
        for ctg_how in ctg_how_list:
            data.loc[len(data), :] = [
                accounting_start,
                ctg_how.split("-")[0],
                ctg_how.split("-")[1],
                0
            ]
            data.loc[len(data), :] = [
                now_date,
                ctg_how.split("-")[0],
                ctg_how.split("-")[1],
                0
            ]
        return data.sort_values(by="time")

    def _get_saving_monthly_data(self) -> pd.DataFrame:
        """
        月ごとに貯金額をまとめる

        Returns
        -------
        pd.DataFrame
            月ごとの貯金額合計
        """
        monthly_saving = self._add_first_data_and_now_data(data=self._saving_data)
        monthly_saving["year-month"] = monthly_saving["time"].dt.strftime("%Y-%m-25")
        monthly_saving = monthly_saving[["year-month", "category", "how_to_save", "amount"]].groupby(["year-month", "category", "how_to_save"], as_index=False).sum()

        return monthly_saving

    def _add_trace_saving_ctg_how(self, saving_monthly_data: pd.DataFrame, ctg_or_how: Literal["ctg", "how", "all"], condition_str: str | None=None):
        """
        貯金項目や貯金方法ごとの貯金額のtraceを作成する。

        Parameters
        ----------
        saving_monthly_data : pd.DataFrame
            月ごとの貯金額合計のデータ
        ctg_or_how : Literal["ctg", "how", "all"]
            どの項目名でtraceを作るか。ctgは貯金項目、howは貯金方法、allは全てを使う。
        condition_str : str | None, optional
            ctg_or_howがctg, howのどちらかの場合、どの値でデータを絞るか

        """
        if ctg_or_how == "ctg":
            column_name = "category"
        elif ctg_or_how == "how":
            column_name = "how_to_save"

        if ctg_or_how != "all":
            plot_data = saving_monthly_data.loc[saving_monthly_data[column_name] == condition_str]
            name = condition_str
            if ctg_or_how == "ctg":
                visible = True
            else:
                visible = False
            trace_name = f"{ctg_or_how}-{condition_str}"
        else:
            plot_data = saving_monthly_data
            name = "合計"
            visible = True
            trace_name = "合計"

        plot_data = plot_data[["year-month", "amount"]].groupby("year-month", as_index=False).sum()
        plot_data["cumsum_amount"] = plot_data["amount"].cumsum()
        plot_data["time"] = pd.to_datetime(plot_data["year-month"], format="%Y-%m-%d")

        trace = go.Scatter(
            x = plot_data["time"],
            y = plot_data["cumsum_amount"],
            mode = "lines+markers",
            name = name,
            visible = visible,
            fill = "tozeroy"
        )

        self._traces_data.append(trace_name=trace_name, trace=trace)

    def traces(self) -> list[go.Trace]:
        """
        全てのtraceを作成し、リストで出力する

        Returns
        -------
        list[go.Trace]
            すべてのtraceのリスト
        """
        saving_monthly_data = self._get_saving_monthly_data()

        self._add_trace_saving_ctg_how(
            saving_monthly_data=saving_monthly_data,
            ctg_or_how="all",
            )

        ctg_list = self._get_ctg_list()
        for ctg in ctg_list:
            self._add_trace_saving_ctg_how(
                saving_monthly_data=saving_monthly_data,
                ctg_or_how="ctg",
                condition_str=ctg
                )

        how_list = self._get_how_list()
        for how in how_list:
            self._add_trace_saving_ctg_how(
                saving_monthly_data=saving_monthly_data,
                ctg_or_how="how",
                condition_str=how
                )

        return self._traces_data.traces

    def layout(self) -> go.Layout:
        """
        グラフのレイアウトを設定する

        Returns
        -------
        go.Layout
            レイアウトの設定
        """
        return go.Layout(
            title=dict(text="貯金結果 期間：" + self._accounting_time.get_date_interval_str()),
            updatemenus=self._updatemenus(),
            barmode="overlay",
            hovermode="x",
            )

    def _buttons(self) -> dict:
        """
        ボタンを作成。具体的には以下の項目を設定する

        - 貯金項目ごとに見るか
        - 貯金方法ごとに見るか

        Returns
        -------
        dict
            ボタンの設定
        """
        buttons = []

        button_names = ["貯金項目別", "貯金方法別"]
        ctg_list = self._get_ctg_list()
        how_list = self._get_how_list()
        for button_name in button_names:
            if button_name == "貯金項目別":
                visible_trace_names = ["合計"] + [f"ctg-{ctg}" for ctg in ctg_list]
                visible_status = self._traces_data.get_bool_from_name(search_trace_names=visible_trace_names)
            elif button_name == "貯金方法別":
                visible_trace_names = ["合計"] + [f"how-{how}" for how in how_list]
                visible_status = self._traces_data.get_bool_from_name(search_trace_names=visible_trace_names)

            button_title = "貯金結果 期間：" + self._accounting_time.get_date_interval_str()
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