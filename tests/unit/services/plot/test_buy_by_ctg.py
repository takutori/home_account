import pytest
from datetime import datetime

from app.services.accounting_time import AccountingMonth
from app.services.plot.buy_by_ctg import BuyByCtg




class TestBuyByCtg:
    def test_init(self, monthly_data):
        buy_data = monthly_data[0]["buy"]
        buy_ctl_data = monthly_data[1]["buy"]
        accounting_month = AccountingMonth(now_date="2025-01-21")

        buy_data["time"] = buy_data["time"].dt.strftime(date_format="%Y-%m-%d")
        with pytest.raises(ValueError) as e:
            BuyByCtg(
                accounting_time=accounting_month,
                buy_ctl_data=buy_ctl_data,
                buy_data=buy_data,
                )
        assert "time列がpd.Timestamp型になっていません" in str(e.value)

    def test_create(self, monthly_data):
        """tests/out_plot/unit_plot/にグラフを保存する形でテスト"""
        buy_data = monthly_data[0]["buy"]
        buy_ctl_data = monthly_data[1]["buy"]

        accounting_month = AccountingMonth(now_date="2025-01-21")

        fig = BuyByCtg(
            accounting_time=accounting_month,
            buy_ctl_data=buy_ctl_data,
            buy_data=buy_data,
            ).create()

        fig.write_html("tests/out_plot/unit_plot/TestBuyByCtg.html")

    def test_get_plot_data(self, monthly_data):
        buy_data = monthly_data[0]["buy"]
        buy_ctl_data = monthly_data[1]["buy"]

        accounting_month = AccountingMonth(now_date="2025-01-21")

        plot_data = BuyByCtg(
            accounting_time=accounting_month,
            buy_ctl_data=buy_ctl_data,
            buy_data=buy_data,
            )._get_plot_data(
                category_level=1,
            )

        assert len(plot_data) == 14

        plot_data = BuyByCtg(
            accounting_time=accounting_month,
            buy_ctl_data=buy_ctl_data,
            buy_data=buy_data,
            )._get_plot_data(
                category_level=2,
                ctg1="住居費"
            )
        assert len(plot_data) == 2

    def test_hoverlist(self, monthly_data):
        buy_data = monthly_data[0]["buy"]
        buy_ctl_data = monthly_data[1]["buy"]

        accounting_month = AccountingMonth(now_date="2025-01-21")

        hover_list = BuyByCtg(
            accounting_time=accounting_month,
            buy_ctl_data=buy_ctl_data,
            buy_data=buy_data,
            )._get_hoverlist(
                plot_data=buy_ctl_data,
                limit_or_buy="limit"
            )
        assert len(hover_list) == 38

        buy_ctl_data["amount"] = range(len(buy_ctl_data))
        hover_list = BuyByCtg(
            accounting_time=accounting_month,
            buy_ctl_data=buy_ctl_data,
            buy_data=buy_data,
            )._get_hoverlist(
                plot_data=buy_ctl_data,
                limit_or_buy="buy"
            )
        assert len(hover_list) == 38

    def test_color_list(self, monthly_data):
        buy_data = monthly_data[0]["buy"]
        buy_ctl_data = monthly_data[1]["buy"]

        accounting_month = AccountingMonth(now_date="2025-01-21")

        buy_by_ctg = BuyByCtg(
            accounting_time=accounting_month,
            buy_ctl_data=buy_ctl_data,
            buy_data=buy_data,
            )

        assert buy_by_ctg._color_list("limit") == "lightslategray"
        assert buy_by_ctg._color_list("buy") == "crimson"
        with pytest.raises(ValueError) as e:
            buy_by_ctg._color_list("aaa")
        assert "aaaは指定できません。" in str(e.value)

    def test_add_trace_bar(self, monthly_data):
        buy_data = monthly_data[0]["buy"]
        buy_ctl_data = monthly_data[1]["buy"]

        accounting_month = AccountingMonth(now_date="2025-01-21")

        buy_by_ctg = BuyByCtg(
            accounting_time=accounting_month,
            buy_ctl_data=buy_ctl_data,
            buy_data=buy_data,
            )
        buy_by_ctg._add_trace_bar(
                category_level=1,
                limit_or_buy="limit"
            )
        assert buy_by_ctg._traces_data.trace_len == 1
        buy_by_ctg._add_trace_bar(
                category_level=2,
                limit_or_buy="limit",
                ctg1="住居費"
            )
        assert buy_by_ctg._traces_data.trace_len == 2
        buy_by_ctg._add_trace_bar(
                category_level=1,
                limit_or_buy="buy",
            )
        assert buy_by_ctg._traces_data.trace_len == 3
        buy_by_ctg._add_trace_bar(
                category_level=2,
                limit_or_buy="buy",
                ctg1="趣味費"
            )
        assert buy_by_ctg._traces_data.trace_len == 4
        assert buy_by_ctg._traces_data._traces[3].text == ("47%", "0%", "73%", "0%", "100%>", "48%")


    def test_traces(self, monthly_data):
        buy_data = monthly_data[0]["buy"]
        buy_ctl_data = monthly_data[1]["buy"]

        accounting_month = AccountingMonth(now_date="2025-01-21")

        traces = BuyByCtg(
            accounting_time=accounting_month,
            buy_ctl_data=buy_ctl_data,
            buy_data=buy_data,
            ).traces()

        assert len(traces) == 30

    def test_layout(self, monthly_data):
        buy_data = monthly_data[0]["buy"]
        buy_ctl_data = monthly_data[1]["buy"]

        accounting_month = AccountingMonth(now_date="2025-01-21")

        layout = BuyByCtg(
            accounting_time=accounting_month,
            buy_ctl_data=buy_ctl_data,
            buy_data=buy_data,
            ).layout()

        # グラフの初期値を確認
        assert layout.title.text == "【カテゴリー1】 残り日数:4 予算合計:236,400 出費合計:194,082 残金:42,318"
        assert layout.hovermode == "x"

    def test_get_limit_and_buy_by_ctg(self, monthly_data):
        buy_data = monthly_data[0]["buy"]
        buy_ctl_data = monthly_data[1]["buy"]

        accounting_month = AccountingMonth(now_date="2025-01-21")

        values = BuyByCtg(
            accounting_time=accounting_month,
            buy_ctl_data=buy_ctl_data,
            buy_data=buy_data,
            )._get_limit_and_buy_by_ctg(
                category_level=1,
            )
        assert values["buy"] == 194082
        assert values["limit"] == 236400

    def test_buttons(self, monthly_data):
        buy_data = monthly_data[0]["buy"]
        buy_ctl_data = monthly_data[1]["buy"]

        accounting_month = AccountingMonth(now_date="2025-01-21")

        buttons = BuyByCtg(
            accounting_time=accounting_month,
            buy_ctl_data=buy_ctl_data,
            buy_data=buy_data,
            )._buttons()
        assert len(buttons) == 15
        assert buttons[0]["label"] == "カテゴリー1"
        assert buttons[0]["method"] == "update"

    def test_updatemenus(self, monthly_data):
        buy_data = monthly_data[0]["buy"]
        buy_ctl_data = monthly_data[1]["buy"]

        accounting_month = AccountingMonth(now_date="2025-01-21")

        updatemenus = BuyByCtg(
            accounting_time=accounting_month,
            buy_ctl_data=buy_ctl_data,
            buy_data=buy_data,
            )._updatemenus()
        assert len(updatemenus) == 1
        assert updatemenus[0]["type"] == "buttons"
        assert updatemenus[0]["direction"] == "right"
        assert len(updatemenus[0]["buttons"]) == 15