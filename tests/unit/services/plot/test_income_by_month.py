import pytest
import numpy as np

from app.services.accounting_time import AccountingYear
from app.services.plot.income_by_month import IncomeByMonth




class TestIncomeByMonth:
    def test_init(self, monthly_data):
        income_data = monthly_data[0]["income"]
        income_ctl_data = monthly_data[1]["income"]
        accounting_month = AccountingYear(now_date="2025-01-21")

        income_data["time"] = income_data["time"].dt.strftime(date_format="%Y-%m-%d")
        with pytest.raises(ValueError) as e:
            IncomeByMonth(
                accounting_time=accounting_month,
                income_ctl_data=income_ctl_data,
                income_data=income_data,
                )
        assert "time列がpd.Timestamp型になっていません" in str(e.value)

    def test_create(self, monthly_data):
        income_data = monthly_data[0]["income"]
        income_ctl_data = monthly_data[1]["income"]
        accounting_month = AccountingYear(now_date="2025-01-21")
        fig = IncomeByMonth(
            accounting_time=accounting_month,
            income_ctl_data=income_ctl_data,
            income_data=income_data,
            ).create()

        fig.write_html("tests/out_plot/unit_plot/TestIncomeByMonth.html")

    def test_get_income_ctg(self, monthly_data):
        income_data = monthly_data[0]["income"]
        income_ctl_data = monthly_data[1]["income"]
        accounting_month = AccountingYear(now_date="2025-01-21")
        income_ctg = IncomeByMonth(
            accounting_time=accounting_month,
            income_ctl_data=income_ctl_data,
            income_data=income_data,
            )._get_income_ctg()

        assert income_ctg == ["会社A", "会社B", "会社C", "Homepage", "その他"]

    def test_income_data_groupby_yearmonth_ctg(self, monthly_data):
        income_data = monthly_data[0]["income"]
        income_ctl_data = monthly_data[1]["income"]
        accounting_month = AccountingYear(now_date="2025-01-21")
        data = IncomeByMonth(
            accounting_time=accounting_month,
            income_ctl_data=income_ctl_data,
            income_data=income_data,
            )._income_data_groupby_yearmonth_ctg()

        assert len(data) == 31

    def test_add_trace_income_by_ctg(self, monthly_data):
        income_data = monthly_data[0]["income"]
        income_ctl_data = monthly_data[1]["income"]
        accounting_month = AccountingYear(now_date="2025-01-21")
        income_by_month = IncomeByMonth(
            accounting_time=accounting_month,
            income_ctl_data=income_ctl_data,
            income_data=income_data,
            )
        income_by_month._add_trace_income_by_ctg(
            ctg="会社A",
            income_data_groupby_yearmonth_ctg=income_by_month._income_data_groupby_yearmonth_ctg()
        )

        assert income_by_month._traces_data.trace_len == 1

    def test_add_trace_cumsum_income_ctg(self, monthly_data):
        income_data = monthly_data[0]["income"]
        income_ctl_data = monthly_data[1]["income"]
        accounting_month = AccountingYear(now_date="2025-01-21")
        income_by_month = IncomeByMonth(
            accounting_time=accounting_month,
            income_ctl_data=income_ctl_data,
            income_data=income_data,
            )
        income_by_month._add_trace_cumsum_income_by_ctg(
            ctg="会社A",
            income_data_groupby_yearmonth_ctg=income_by_month._income_data_groupby_yearmonth_ctg()
        )

        assert income_by_month._traces_data.trace_len == 1

    def test_add_trace_cumsum_all_income(self, monthly_data):
        income_data = monthly_data[0]["income"]
        income_ctl_data = monthly_data[1]["income"]
        accounting_month = AccountingYear(now_date="2025-01-21")
        income_by_month = IncomeByMonth(
            accounting_time=accounting_month,
            income_ctl_data=income_ctl_data,
            income_data=income_data,
            )
        income_by_month._add_trace_cumsum_all_income(
            plot_data=income_by_month._income_data_groupby_yearmonth_ctg()
        )

        assert income_by_month._traces_data.trace_len == 1

    def test_traces(self, monthly_data):
        income_data = monthly_data[0]["income"]
        income_ctl_data = monthly_data[1]["income"]
        accounting_month = AccountingYear(now_date="2025-01-21")
        traces = IncomeByMonth(
            accounting_time=accounting_month,
            income_ctl_data=income_ctl_data,
            income_data=income_data,
            ).traces()

        assert len(traces) == 11

    def test_layout(self, monthly_data):
        income_data = monthly_data[0]["income"]
        income_ctl_data = monthly_data[1]["income"]
        accounting_month = AccountingYear(now_date="2025-01-21")
        layout = IncomeByMonth(
            accounting_time=accounting_month,
            income_ctl_data=income_ctl_data,
            income_data=income_data,
            ).layout()
        assert layout.title.text == "今年の月毎の給与\u3000\n期間：2024-04-01_2025-04-01"

    def test_buttons(self, monthly_data):
        income_data = monthly_data[0]["income"]
        income_ctl_data = monthly_data[1]["income"]
        accounting_month = AccountingYear(now_date="2025-01-21")
        buttons = IncomeByMonth(
            accounting_time=accounting_month,
            income_ctl_data=income_ctl_data,
            income_data=income_data,
            )._buttons()

        assert len(buttons) == 2

    def test_updatemenus(self, monthly_data):
        income_data = monthly_data[0]["income"]
        income_ctl_data = monthly_data[1]["income"]
        accounting_month = AccountingYear(now_date="2025-01-21")
        updatemenus = IncomeByMonth(
            accounting_time=accounting_month,
            income_ctl_data=income_ctl_data,
            income_data=income_data,
            )._updatemenus()
        assert updatemenus[0]["type"] == "buttons"
        assert updatemenus[0]["direction"] == "right"
        assert len(updatemenus[0]["buttons"]) == 2