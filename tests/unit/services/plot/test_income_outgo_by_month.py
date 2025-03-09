import pytest
import numpy as np

from app.services.accounting_time import AccountingYear
from app.services.plot.income_outgo_by_month import IncomeOutgoByMonth




class TestIncomeByMonth:
    def test_init(self, monthly_data):
        buy_data = monthly_data[0]["buy"]
        buy_ctl_data = monthly_data[1]["buy"]
        income_data = monthly_data[0]["income"]
        income_ctl_data = monthly_data[1]["income"]
        saving_data = monthly_data[0]["saving"]

        accounting_month = AccountingYear(now_date="2025-01-21")

        income_data["time"] = income_data["time"].dt.strftime(date_format="%Y-%m-%d")
        with pytest.raises(ValueError) as e:
            IncomeOutgoByMonth(
                accounting_time=accounting_month,
                buy_ctl_data=buy_ctl_data,
                buy_data=buy_data,
                income_ctl_data=income_ctl_data,
                income_data=income_data,
                saving_data=saving_data
                )
        assert "time列がpd.Timestamp型になっていません" in str(e.value)

    def test_create(self, monthly_data):
        buy_data = monthly_data[0]["buy"]
        buy_ctl_data = monthly_data[1]["buy"]
        income_data = monthly_data[0]["income"]
        income_ctl_data = monthly_data[1]["income"]
        saving_data = monthly_data[0]["saving"]

        accounting_month = AccountingYear(now_date="2025-01-21")
        fig = IncomeOutgoByMonth(
            accounting_time=accounting_month,
            buy_ctl_data=buy_ctl_data,
            buy_data=buy_data,
            income_ctl_data=income_ctl_data,
            income_data=income_data,
            saving_data=saving_data
            ).create()

        fig.write_html("tests/out_plot/unit_plot/TestIncomeOutgoByMonth.html")

    def test_get_diff_from_limit(self, monthly_data):
        buy_data = monthly_data[0]["buy"]
        buy_ctl_data = monthly_data[1]["buy"]
        income_data = monthly_data[0]["income"]
        income_ctl_data = monthly_data[1]["income"]
        saving_data = monthly_data[0]["saving"]

        accounting_month = AccountingYear(now_date="2025-01-21")
        data = IncomeOutgoByMonth(
            accounting_time=accounting_month,
            buy_ctl_data=buy_ctl_data,
            buy_data=buy_data,
            income_ctl_data=income_ctl_data,
            income_data=income_data,
            saving_data=saving_data
            )._get_diff_from_limit()

        assert len(data) == 12
        assert data.columns.tolist() == ["year-month", "amount", "diff", "cumsum_diff", "time"]

    def test_add_trace_diff_from_limit(self, monthly_data):
        buy_data = monthly_data[0]["buy"]
        buy_ctl_data = monthly_data[1]["buy"]
        income_data = monthly_data[0]["income"]
        income_ctl_data = monthly_data[1]["income"]
        saving_data = monthly_data[0]["saving"]

        accounting_month = AccountingYear(now_date="2025-01-21")
        income_out_by_month = IncomeOutgoByMonth(
            accounting_time=accounting_month,
            buy_ctl_data=buy_ctl_data,
            buy_data=buy_data,
            income_ctl_data=income_ctl_data,
            income_data=income_data,
            saving_data=saving_data
            )
        income_out_by_month._add_trace_diff_from_limit(
            diff_from_limit=income_out_by_month._get_diff_from_limit()
        )

        assert income_out_by_month._traces_data.trace_len == 1

    def test_trace_cumsum_diff_from_limit(self, monthly_data):
        buy_data = monthly_data[0]["buy"]
        buy_ctl_data = monthly_data[1]["buy"]
        income_data = monthly_data[0]["income"]
        income_ctl_data = monthly_data[1]["income"]
        saving_data = monthly_data[0]["saving"]

        accounting_month = AccountingYear(now_date="2025-01-21")
        income_out_by_month = IncomeOutgoByMonth(
            accounting_time=accounting_month,
            buy_ctl_data=buy_ctl_data,
            buy_data=buy_data,
            income_ctl_data=income_ctl_data,
            income_data=income_data,
            saving_data=saving_data
            )
        income_out_by_month._add_trace_cumsum_diff_from_limit(
            diff_from_limit=income_out_by_month._get_diff_from_limit()
        )

        assert income_out_by_month._traces_data.trace_len == 1

    def test_trace_cumsum_diff_from_limit(self, monthly_data):
        buy_data = monthly_data[0]["buy"]
        buy_ctl_data = monthly_data[1]["buy"]
        income_data = monthly_data[0]["income"]
        income_ctl_data = monthly_data[1]["income"]
        saving_data = monthly_data[0]["saving"]

        accounting_month = AccountingYear(now_date="2025-01-21")
        income_out_by_month = IncomeOutgoByMonth(
            accounting_time=accounting_month,
            buy_ctl_data=buy_ctl_data,
            buy_data=buy_data,
            income_ctl_data=income_ctl_data,
            income_data=income_data,
            saving_data=saving_data
            )
        data = income_out_by_month._get_diff_from_residual_income()

        assert len(data) == 12

    def test_add_trace_diff_residual_income(self, monthly_data):
        buy_data = monthly_data[0]["buy"]
        buy_ctl_data = monthly_data[1]["buy"]
        income_data = monthly_data[0]["income"]
        income_ctl_data = monthly_data[1]["income"]
        saving_data = monthly_data[0]["saving"]

        accounting_month = AccountingYear(now_date="2025-01-21")
        income_out_by_month = IncomeOutgoByMonth(
            accounting_time=accounting_month,
            buy_ctl_data=buy_ctl_data,
            buy_data=buy_data,
            income_ctl_data=income_ctl_data,
            income_data=income_data,
            saving_data=saving_data
            )
        income_out_by_month._add_trace_diff_from_residual_income(
            diff_from_residual_income=income_out_by_month._get_diff_from_residual_income()
        )

        assert income_out_by_month._traces_data.trace_len == 1

    def test_add_trace_cumsum_diff_residual_income(self, monthly_data):
        buy_data = monthly_data[0]["buy"]
        buy_ctl_data = monthly_data[1]["buy"]
        income_data = monthly_data[0]["income"]
        income_ctl_data = monthly_data[1]["income"]
        saving_data = monthly_data[0]["saving"]

        accounting_month = AccountingYear(now_date="2025-01-21")
        income_out_by_month = IncomeOutgoByMonth(
            accounting_time=accounting_month,
            buy_ctl_data=buy_ctl_data,
            buy_data=buy_data,
            income_ctl_data=income_ctl_data,
            income_data=income_data,
            saving_data=saving_data
            )
        income_out_by_month._add_trace_cumsum_diff_from_residual_income(
            diff_from_residual_income=income_out_by_month._get_diff_from_residual_income()
        )

        assert income_out_by_month._traces_data.trace_len == 1

    def test_traces(self, monthly_data):
        buy_data = monthly_data[0]["buy"]
        buy_ctl_data = monthly_data[1]["buy"]
        income_data = monthly_data[0]["income"]
        income_ctl_data = monthly_data[1]["income"]
        saving_data = monthly_data[0]["saving"]

        accounting_month = AccountingYear(now_date="2025-01-21")
        traces = IncomeOutgoByMonth(
            accounting_time=accounting_month,
            buy_ctl_data=buy_ctl_data,
            buy_data=buy_data,
            income_ctl_data=income_ctl_data,
            income_data=income_data,
            saving_data=saving_data
            ).traces()

        assert len(traces) == 4

    def test_traces(self, monthly_data):
        buy_data = monthly_data[0]["buy"]
        buy_ctl_data = monthly_data[1]["buy"]
        income_data = monthly_data[0]["income"]
        income_ctl_data = monthly_data[1]["income"]
        saving_data = monthly_data[0]["saving"]

        accounting_month = AccountingYear(now_date="2025-01-21")
        layout = IncomeOutgoByMonth(
            accounting_time=accounting_month,
            buy_ctl_data=buy_ctl_data,
            buy_data=buy_data,
            income_ctl_data=income_ctl_data,
            income_data=income_data,
            saving_data=saving_data
            ).layout()

        assert layout.title.text == '今年の月毎の収支\u3000\n期間：2024-04-01_2025-04-01'

    def test_buttons(self, monthly_data):
        buy_data = monthly_data[0]["buy"]
        buy_ctl_data = monthly_data[1]["buy"]
        income_data = monthly_data[0]["income"]
        income_ctl_data = monthly_data[1]["income"]
        saving_data = monthly_data[0]["saving"]

        accounting_month = AccountingYear(now_date="2025-01-21")
        buttons = IncomeOutgoByMonth(
            accounting_time=accounting_month,
            buy_ctl_data=buy_ctl_data,
            buy_data=buy_data,
            income_ctl_data=income_ctl_data,
            income_data=income_data,
            saving_data=saving_data
            )._buttons()

        assert len(buttons) == 2

    def test_updatemenus(self, monthly_data):
        buy_data = monthly_data[0]["buy"]
        buy_ctl_data = monthly_data[1]["buy"]
        income_data = monthly_data[0]["income"]
        income_ctl_data = monthly_data[1]["income"]
        saving_data = monthly_data[0]["saving"]

        accounting_month = AccountingYear(now_date="2025-01-21")
        updatemenus = IncomeOutgoByMonth(
            accounting_time=accounting_month,
            buy_ctl_data=buy_ctl_data,
            buy_data=buy_data,
            income_ctl_data=income_ctl_data,
            income_data=income_data,
            saving_data=saving_data
            )._updatemenus()

        assert updatemenus[0]["type"] == "buttons"
        assert len(updatemenus[0]["buttons"]) == 2