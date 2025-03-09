import pytest
from datetime import datetime

from app.services.accounting_time import ThisMonth
from app.services.plot.by_plotly import MonthAmountByCtg




class TestMonthAmountbyCtg:
    def test_create(self, monthly_data):
        buy_data = monthly_data[0]["buy"]
        buy_ctl_data = monthly_data[1]["buy"]

        this_month = ThisMonth(now_date="2025-01-21")

        fig = MonthAmountByCtg(
            account_interval=this_month,
            buy_ctl_data=buy_ctl_data,
            buy_data=buy_data,
            ).create()

        fig.write_html("tests/out_plot/unit_plot/MonthAmountByCtg.html")

