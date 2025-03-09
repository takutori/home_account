import pytest
import numpy as np
from datetime import datetime

from app.services.accounting_time import AccountingMonth
from app.services.plot.buy_by_date import BuyByDate




class TestBuyByDate:
    def test_init(self, monthly_data):
        buy_data = monthly_data[0]["buy"]
        buy_ctl_data = monthly_data[1]["buy"]
        accounting_month = AccountingMonth(now_date="2025-01-21")

        buy_data["time"] = buy_data["time"].dt.strftime(date_format="%Y-%m-%d")
        with pytest.raises(ValueError) as e:
            BuyByDate(
                accounting_time=accounting_month,
                buy_ctl_data=buy_ctl_data,
                buy_data=buy_data,
                residual_income=240000
                )
        assert "time列がpd.Timestamp型になっていません" in str(e.value)

    def test_create(self, monthly_data):
        """tests/out_plot/unit_plot/にグラフを保存する形でテスト"""
        buy_data = monthly_data[0]["buy"]
        buy_ctl_data = monthly_data[1]["buy"]

        accounting_month = AccountingMonth(now_date="2025-01-21")

        fig = BuyByDate(
            accounting_time=accounting_month,
            buy_ctl_data=buy_ctl_data,
            buy_data=buy_data,
            residual_income=240000
            ).create()

        fig.write_html("tests/out_plot/unit_plot/TestBuyByDate.html")

    def test_get_buy_history(self, monthly_data):
        """tests/out_plot/unit_plot/にグラフを保存する形でテスト"""
        buy_data = monthly_data[0]["buy"]
        buy_ctl_data = monthly_data[1]["buy"]

        accounting_month = AccountingMonth(now_date="2025-01-21")

        buy_history = BuyByDate(
            accounting_time=accounting_month,
            buy_ctl_data=buy_ctl_data,
            buy_data=buy_data,
            residual_income=240000
            )._get_buy_history()

        assert np.isnan(buy_history.iloc[-1])
        assert len(buy_history) == 20

    def test_add_trace_plot(self, monthly_data):
        buy_data = monthly_data[0]["buy"]
        buy_ctl_data = monthly_data[1]["buy"]

        accounting_month = AccountingMonth(now_date="2025-01-21")

        buy_by_date = BuyByDate(
            accounting_time=accounting_month,
            buy_ctl_data=buy_ctl_data,
            buy_data=buy_data,
            residual_income=240000
            )
        buy_by_date._add_trace_plot(buy_sum_history=buy_by_date._get_buy_history())

        assert buy_by_date._traces_data.trace_len == 1

    def test_add_trace_hline(self, monthly_data):
        buy_data = monthly_data[0]["buy"]
        buy_ctl_data = monthly_data[1]["buy"]

        accounting_month = AccountingMonth(now_date="2025-01-21")

        buy_by_date = BuyByDate(
            accounting_time=accounting_month,
            buy_ctl_data=buy_ctl_data,
            buy_data=buy_data,
            residual_income=240000
            )
        buy_by_date._add_trace_hline(buy_sum_history=buy_by_date._get_buy_history())

        assert buy_by_date._traces_data.trace_len == 1

    def test_traces(self, monthly_data):
        buy_data = monthly_data[0]["buy"]
        buy_ctl_data = monthly_data[1]["buy"]

        accounting_month = AccountingMonth(now_date="2025-01-21")

        buy_by_date = BuyByDate(
            accounting_time=accounting_month,
            buy_ctl_data=buy_ctl_data,
            buy_data=buy_data,
            residual_income=240000
            )
        _ = buy_by_date.traces()

        assert buy_by_date._traces_data.trace_len == 2

    def test_layout(self, monthly_data):
        buy_data = monthly_data[0]["buy"]
        buy_ctl_data = monthly_data[1]["buy"]

        accounting_month = AccountingMonth(now_date="2025-01-21")

        buy_by_date = BuyByDate(
            accounting_time=accounting_month,
            buy_ctl_data=buy_ctl_data,
            buy_data=buy_data,
            residual_income=240000
            )
        layout = buy_by_date.layout()

        assert layout.title.text == '今月の日別の使用額\u3000\n期間：2024-12-25_2025-01-25\u3000\n残り日数：4'

