from typing import Literal
import pandas as pd
import plotly.graph_objects as go

from app.services.plot.plot_interface import CreatePlotly
from app.services.accounting_time import AccountingTime


class BuyByCtg(CreatePlotly):
    def __init__(
        self,
        accounting_time: AccountingTime,
        buy_ctl_data: pd.DataFrame,
        buy_data: pd.DataFrame,
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
        # time列がdatetime型に変換されているか確認
        if type(self._buy_data.iloc[0]["time"]) != pd.Timestamp:
            raise ValueError("time列がpd.Timestamp型になっていません")
        # データを会計期間に絞る
        interval = self._accounting_time.get_date_interval()
        self._buy_data = self._buy_data.loc[
            (interval[0] <= self._buy_data["time"]) &
            (self._buy_data["time"] < interval[1])
        ]

    def _get_plot_data(
        self,
        category_level: Literal[1, 2],
        ctg1: str | None = None,
    ) -> pd.DataFrame:
        """
        カテゴリーレベルに合わせたデータを出力する。

        Parameters
        ----------
        category_level : Literal[1, 2]
            カテゴリーレベル
        ctg1 : str | None
            カテゴリーレベルが2の場合に、指定するカテゴリーレベル1の値

        Returns
        -------
        pd.DataFrame
            指定されたカテゴリーのデータ
        """
        if category_level == 1:
            amount_data = self._buy_data[["category1", "amount"]].groupby("category1", sort=False, as_index=False).sum()
            ctl_data = self._buy_ctl_data[["カテゴリー1", "予算"]].groupby("カテゴリー1", sort=False, as_index=False).sum()
        else:
            amount_data = self._buy_data.loc[self._buy_data["category1"] == ctg1, ["category2", "amount"]].groupby("category2", sort=False, as_index=False).sum()
            ctl_data = self._buy_ctl_data.loc[self._buy_ctl_data["カテゴリー1"] == ctg1, ["カテゴリー2", "予算"]]

        ctg_amount_data = pd.merge(ctl_data, amount_data, left_on=f"カテゴリー{category_level}", right_on=f"category{category_level}", how="left")
        ctg_amount_data.loc[:, "amount"] = ctg_amount_data.loc[:, "amount"].fillna(0)

        return ctg_amount_data

    def _get_hoverlist(self, plot_data: pd.DataFrame, limit_or_buy: Literal["limit", "buy"]) -> list[str]:
        """
        plotlyに使用するホバーのリストを出力

        Parameters
        ----------
        plot_data : pd.DataFrame
            可視化するグラフのデータ
        limit_or_buy : Literal[&quot;limit&quot;, &quot;buy&quot;]
            予算グラフか支出グラフか

        Returns
        -------
        list[str]
            ホバーのリスト
        """
        if limit_or_buy == "limit":
            hoverlist = [
                    f"予算: {limit}" for limit in plot_data["予算"]
                ]
        elif limit_or_buy == "buy":
            hoverlist = [
                f"残予算： {int(limit - buy)}<br>　支出： {int(buy)}" for limit, buy in zip(plot_data["予算"], plot_data["amount"])
            ]

        return hoverlist

    def _color_list(self, limit_or_buy: Literal["limit", "buy"]) -> str:
        """
        棒グラフの色を取得する

        Parameters
        ----------
        limit_or_buy : Literal[&quot;limit&quot;, &quot;buy&quot;]
            棒グラフの種類

        Returns
        -------
        str
            色
        """
        if limit_or_buy == "limit":
            return "lightslategray"
        elif limit_or_buy == "buy":
            return "crimson"
        else:
            raise ValueError(f"{limit_or_buy}は指定できません。")


    def _add_trace_bar(
        self,
        category_level: Literal[1, 2],
        limit_or_buy: Literal["limit", "buy"],
        ctg1: str | None = None,
    ):
        """
        棒グラフのtraceを作成し、trace管理用クラスに保持させる

        Parameters
        ----------
        category_level : Literal[1, 2]
            カテゴリーレベル
        limit_or_buy : Literal[&quot;limit&quot;, &quot;buy&quot;]
            予算グラフか支出グラフか
        ctg1 : str | None, optional
            カテゴリーレベルが2の場合の、カテゴリーレベル1の値
        """

        plot_data = self._get_plot_data(category_level=category_level, ctg1=ctg1)
        if limit_or_buy == "limit":
            color_list = ["lightslategray"]*len(plot_data)
        else:
            color_list = ["crimson"]*len(plot_data)

        hoverlist = self._get_hoverlist(plot_data=plot_data, limit_or_buy=limit_or_buy)

        if category_level == 1:
            visible = True
        else:
            visible = False

        if limit_or_buy == "limit":
            trace = go.Bar(
                x=plot_data[f"カテゴリー{category_level}"],
                y=plot_data["予算"],
                marker_color=color_list,
                name="予算",
                hovertext = hoverlist,
                hovertemplate=None,
                visible=visible
                )
        elif limit_or_buy == "buy":
            text_list = []
            for buy, limit in zip(plot_data["amount"], plot_data["予算"]):
                if limit != 0:
                    per = str(round(100*(buy / limit))) + "%"
                else:
                    if buy == 0:
                        per = "0%"
                    else:
                        per = "100%>"
                text_list.append(per)

            trace = go.Bar(
                x=plot_data[f"カテゴリー{category_level}"],
                y=plot_data["amount"],
                textposition="inside",
                text=text_list,
                marker_color=color_list,
                name="支出",
                hovertext = hoverlist,
                hovertemplate=None,
                visible=visible
                )

        # traceの名前を決める。
        if category_level == 1:
            trace_name = f"カテゴリー1-{limit_or_buy}"
        elif category_level == 2:
            trace_name = f"カテゴリー2-{limit_or_buy}-{ctg1}"

        self._traces_data.append(trace_name=trace_name, trace=trace)

    def traces(self) -> list[go.Bar]:
        """
        カテゴリーレベル1でのtraceとカテゴリーレベル1の各カテゴリごとのtrceを全て作成する

        Returns
        -------
        list[go.Figure]
            traceのリスト
        """
        # カテゴリー1のグラフ
        self._add_trace_bar(category_level=1, limit_or_buy="limit")
        self._add_trace_bar(category_level=1, limit_or_buy="buy")

        # カテゴリー2のグラフ
        for ctg1 in self._ctg_dict.keys():
            self._add_trace_bar(category_level=2, ctg1=ctg1, limit_or_buy="limit")
            self._add_trace_bar(category_level=2, ctg1=ctg1, limit_or_buy="buy")

        return self._traces_data.traces

    def layout(self) -> go.Layout:
        """
        グラフの全体的なレイアウトを出力

        Returns
        -------
        go.Layout
            グラフのレイアウト
        """
        limit_and_buy = self._get_limit_and_buy_by_ctg(category_level=1, ctg1=None)
        limit = format(limit_and_buy["limit"], ",")
        buy = format(limit_and_buy["buy"], ",")
        left_limit = format(limit_and_buy["limit"] - limit_and_buy["buy"], ",")
        title = f"【カテゴリー1】 残り日数:{self._accounting_time.get_days_left()} 予算合計:{limit} 出費合計:{buy} 残金:{left_limit}"

        return go.Layout(
            title=dict(text=title),
            updatemenus=self._updatemenus(),
            barmode="overlay",
            hovermode="x",
            legend=dict(itemsizing="constant")
            )

    def _get_limit_and_buy_by_ctg(self, category_level: Literal[1, 2], ctg1: str | None = None) -> dict[str, int]:
        """
        対象の項目の予算合計と出費合計を計算する

        Parameters
        ----------
        category_level : Literal[1, 2]
            カテゴリーレベル
        ctg1 : str | None, optional
            カテゴリー1の値 by default None。どのカテゴリで計算するか。

        Returns
        -------
        dict[str, int]
            予算合計と出費合計
        """
        plot_data = self._get_plot_data(category_level=category_level, ctg1=ctg1)
        return {
            "buy": int(plot_data["amount"].sum()),
            "limit": int(plot_data["予算"].sum())
        }


    def _buttons(self) -> dict:
        """
        ボタンを作成。具体的には以下の項目を設定する

        - "カテゴリー1"とカテゴリー1の値全てをボタンにする
        - ボタンを押した時のグラフタイトルを設定する
        - ボタンを押した時のグラフを設定する

        Returns
        -------
        dict
            ボタンの設定
        """
        buttons = []
        button_names = ["カテゴリー1"] + [ctg1 for ctg1 in self._ctg_dict.keys()]
        for button_name in button_names:
            if button_name == "カテゴリー1":
                visible_trace_names=["カテゴリー1-limit", "カテゴリー1-buy"]
                category_level = 1
                ctg1 = None
            else:
                visible_trace_names=[f"カテゴリー2-limit-{button_name}", f"カテゴリー2-buy-{button_name}"]
                category_level = 2
                ctg1 = button_name
            visible_status = self._traces_data.get_bool_from_name(search_trace_names=visible_trace_names)

            limit_and_buy = self._get_limit_and_buy_by_ctg(category_level=category_level, ctg1=ctg1)
            limit = format(limit_and_buy["limit"], ",")
            buy = format(limit_and_buy["buy"], ",")
            left_limit = format(limit_and_buy["limit"] - limit_and_buy["buy"], ",")
            button_title = f"【{button_name}】 残り日数:{self._accounting_time.get_days_left()} 予算合計:{limit} 出費合計:{buy} 残金:{left_limit}"
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
