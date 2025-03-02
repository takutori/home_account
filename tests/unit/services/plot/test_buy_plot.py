import pytest
from datetime import datetime
from app.services.plot.by_plotly import MonthAmountByCtg




class TestMonthAmountbyCtg:
    def test_create(self, monthly_data):
        buy_data = monthly_data[0]["buy"]
        buy_ctl_data = monthly_data[1]["buy"]

        accounting_interval = [
            datetime(year=2024, month=12, day=25),
            datetime(year=2025, month=1, day=25)
            ]

        fig = MonthAmountByCtg(
            accounting_interval=accounting_interval,
            buy_ctl_data=buy_ctl_data,
            buy_data=buy_data,
            ).create()

        fig.write_html("tests/out_plot/unit_plot/MonthAmountByCtg.html")

