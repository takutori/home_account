from typing import Literal
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

import plotly.graph_objects as go
import plotly.io as pio

from app.services.plot.plot_interface import CreatePlotly




class MonthAmountByCtg(CreatePlotly):
    def __init__(self, buy_ctl_data: pd.DataFrame, buy_data: pd.DataFrame, accounting_interval: list[datetime]):
        super().__init__(accounting_interval=accounting_interval)
        self._buy_ctl_data = buy_ctl_data
        self._buy_data = buy_data
        self._ctg_dict = self._buy_ctl_data.groupby("カテゴリー1", sort=False)["カテゴリー2"].apply(list).to_dict()

    def _get_plot_data(
        self,
        category_level: Literal[1, 2],
        ctg1: str | None,
    ) -> pd.DataFrame:
        if category_level == 1:
            amount_data = self._buy_data[["category1", "amount"]].groupby("category1", sort=False, as_index=False).sum()
            ctl_data = self._buy_ctl_data[["カテゴリー1", "予算"]].groupby("カテゴリー1", sort=False, as_index=False).sum()
        else:
            amount_data = self._buy_data.loc[self._buy_data["category1"] == ctg1, ["category2", "amount"]].groupby("category2", sort=False, as_index=False).sum()
            ctl_data = self._buy_ctl_data.loc[self._buy_ctl_data["カテゴリー1"] == ctg1, ["カテゴリー2", "予算"]]

        ctg_amount_data = pd.merge(ctl_data, amount_data, left_on=f"カテゴリー{category_level}", right_on=f"category{category_level}", how="left")
        ctg_amount_data.loc[:, "amount"] = ctg_amount_data.loc[:, "amount"].fillna(0)

        return ctg_amount_data

    def _get_hoverlist(self, plot_data: pd.DataFrame, limit_or_buy: Literal["limit", "buy"]):
        if limit_or_buy == "limit":
            hoverlist = [
                    f"予算: {limit}" for limit in plot_data["予算"]
                ]
        elif limit_or_buy == "buy":
            hoverlist = [
                f"残予算： {int(limit - buy)}<br>　支出： {int(buy)}" for limit, buy in zip(plot_data["予算"], plot_data["amount"])
            ]

        return hoverlist

    def _add_trace_bar(
        self,
        category_level: Literal[1, 2],
        limit_or_buy: Literal["limit", "buy"],
        ctg1: str | None = None,
    ):

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

    def traces(self) -> list[go.Figure]:
        # カテゴリー1のグラフ
        self._add_trace_bar(category_level=1, limit_or_buy="limit")
        self._add_trace_bar(category_level=1, limit_or_buy="buy")

        # カテゴリー2のグラフ
        for ctg1 in self._ctg_dict.keys():
            self._add_trace_bar(category_level=2, ctg1=ctg1, limit_or_buy="limit")
            self._add_trace_bar(category_level=2, ctg1=ctg1, limit_or_buy="buy")

        return self._traces_data.traces

    def layout(self):
        limit_and_buy = self._get_limit_and_buy_by_ctg(category_level=1, ctg1=None)
        limit = format(limit_and_buy["limit"], ",")
        buy = format(limit_and_buy["buy"], ",")
        left_limit = format(limit_and_buy["limit"] - limit_and_buy["buy"], ",")
        title = f"【カテゴリー1】 残り日数:{self._get_days_until_25th()} 予算合計:{limit} 出費合計:{buy} 残金:{left_limit}"

        return go.Layout(
            title=dict(text=title),
            updatemenus=self._updatemenus(),
            barmode="overlay",
            hovermode="x"
            )

    def _get_days_until_25th(self):
        today = datetime.now()
        year = today.year
        month = today.month

        # 今月の25日の日付を生成
        target_date = datetime(year, month, 25)

        # 今日が25日以降なら、次の月の25日を目標日に設定
        if today > target_date:
            # 月が12月の場合、年を繰り上げる
            if month == 12:
                target_date = datetime(year+1, 1, 25)
            else:
                target_date = datetime(year, month+1, 25)

        # 目標日までの残り日数を計算
        delta = target_date - today
        return delta.days

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


    def _buttons(self):
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
            button_title = f"【{button_name}】 残り日数:{self._get_days_until_25th()} 予算合計:{limit} 出費合計:{buy} 残金:{left_limit}"
            button = dict(
                label = button_name, method="update",
                args=[
                    {"visible": visible_status},
                    {"title": button_title}
                    ]
                )
            buttons.append(button)

        return buttons

    def _updatemenus(self):
        return [
            dict(
                type="buttons", direction="right",
                x=0.5, y=1.01, xanchor='center', yanchor='bottom',
                active=0, buttons=self._buttons(),
                )
            ]
