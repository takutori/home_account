import pytest
import numpy as np

from app.services.accounting_time import AccountingYear
from app.services.plot.saving_by_month import SavingByMonth




class TestSavingByMonth:
    def test_init(self, monthly_data):
        saving_data = monthly_data[0]["saving"]
        saving_ctl_data = monthly_data[1]["saving"]

        accounting_month = AccountingYear(now_date="2025-01-21")

        saving_data["time"] = saving_data["time"].dt.strftime(date_format="%Y-%m-%d")
        with pytest.raises(ValueError) as e:
            SavingByMonth(
                accounting_time=accounting_month,
                saving_ctl_data=saving_ctl_data,
                saving_data=saving_data
                )
        assert "time列がpd.Timestamp型になっていません" in str(e.value)

    def test_create(self, monthly_data):
        saving_data = monthly_data[0]["saving"]
        saving_ctl_data = monthly_data[1]["saving"]

        accounting_month = AccountingYear(now_date="2025-03-01", start_month=4)

        fig = SavingByMonth(
            accounting_time=accounting_month,
            saving_ctl_data=saving_ctl_data,
            saving_data=saving_data
            ).create()

        fig.write_html("tests/out_plot/unit_plot/TestSavingByMonth.html")

    def test_get_ctg_list(self, monthly_data):
        saving_data = monthly_data[0]["saving"]
        saving_ctl_data = monthly_data[1]["saving"]

        accounting_month = AccountingYear(now_date="2025-03-01", start_month=4)

        saving_by_month = SavingByMonth(
            accounting_time=accounting_month,
            saving_ctl_data=saving_ctl_data,
            saving_data=saving_data
            )
        ctg_list = saving_by_month._get_ctg_list()
        assert len(ctg_list) == 4

    def test_get_how_list(self, monthly_data):
        saving_data = monthly_data[0]["saving"]
        saving_ctl_data = monthly_data[1]["saving"]

        accounting_month = AccountingYear(now_date="2025-03-01", start_month=4)

        saving_by_month = SavingByMonth(
            accounting_time=accounting_month,
            saving_ctl_data=saving_ctl_data,
            saving_data=saving_data
            )
        how_list = saving_by_month._get_how_list()
        assert len(how_list) == 2

    def test_get_ctg_how_list(self, monthly_data):
        saving_data = monthly_data[0]["saving"]
        saving_ctl_data = monthly_data[1]["saving"]

        accounting_month = AccountingYear(now_date="2025-03-01", start_month=4)

        saving_by_month = SavingByMonth(
            accounting_time=accounting_month,
            saving_ctl_data=saving_ctl_data,
            saving_data=saving_data
            )
        ctg_how_list = saving_by_month._get_ctg_how_list()
        assert len(ctg_how_list) == 6

    def test_add_first_data_and_now_data(self, monthly_data):
        saving_data = monthly_data[0]["saving"]
        saving_ctl_data = monthly_data[1]["saving"]

        accounting_month = AccountingYear(now_date="2025-03-01", start_month=4)

        saving_by_month = SavingByMonth(
            accounting_time=accounting_month,
            saving_ctl_data=saving_ctl_data,
            saving_data=saving_data
            )
        data = saving_by_month._add_first_data_and_now_data(saving_data)
        assert len(data) == 45

    def test_get_saving_monthly_data(self, monthly_data):
        saving_data = monthly_data[0]["saving"]
        saving_ctl_data = monthly_data[1]["saving"]

        accounting_month = AccountingYear(now_date="2025-03-01", start_month=4)

        saving_by_month = SavingByMonth(
            accounting_time=accounting_month,
            saving_ctl_data=saving_ctl_data,
            saving_data=saving_data
            )
        data = saving_by_month._get_saving_monthly_data()
        assert len(data) == 42

    def test_add_trace_saving_ctg_how(self, monthly_data):
        saving_data = monthly_data[0]["saving"]
        saving_ctl_data = monthly_data[1]["saving"]

        accounting_month = AccountingYear(now_date="2025-03-01", start_month=4)

        # all
        saving_by_month = SavingByMonth(
            accounting_time=accounting_month,
            saving_ctl_data=saving_ctl_data,
            saving_data=saving_data
            )
        saving_by_month._add_trace_saving_ctg_how(
            saving_monthly_data=saving_by_month._get_saving_monthly_data(),
            ctg_or_how="all"
        )
        assert saving_by_month._traces_data.trace_len == 1

        # ctg
        saving_by_month._add_trace_saving_ctg_how(
            saving_monthly_data=saving_by_month._get_saving_monthly_data(),
            ctg_or_how="ctg",
            condition_str="家族貯金"
        )
        assert saving_by_month._traces_data.trace_len == 2

        # how
        saving_by_month._add_trace_saving_ctg_how(
            saving_monthly_data=saving_by_month._get_saving_monthly_data(),
            ctg_or_how="how",
            condition_str="積立NISA"
        )
        assert saving_by_month._traces_data.trace_len == 3

    def test_traces(self, monthly_data):
        saving_data = monthly_data[0]["saving"]
        saving_ctl_data = monthly_data[1]["saving"]

        accounting_month = AccountingYear(now_date="2025-03-01", start_month=4)

        saving_by_month = SavingByMonth(
            accounting_time=accounting_month,
            saving_ctl_data=saving_ctl_data,
            saving_data=saving_data
            )
        traces = saving_by_month.traces()
        assert len(traces) == 7

    def test_layout(self, monthly_data):
        saving_data = monthly_data[0]["saving"]
        saving_ctl_data = monthly_data[1]["saving"]

        accounting_month = AccountingYear(now_date="2025-03-01", start_month=4)

        saving_by_month = SavingByMonth(
            accounting_time=accounting_month,
            saving_ctl_data=saving_ctl_data,
            saving_data=saving_data
            )
        layout = saving_by_month.layout()
        assert layout.title.text == '貯金結果 期間：2024-04-01_2025-04-01'

    def test_buttons(self, monthly_data):
        saving_data = monthly_data[0]["saving"]
        saving_ctl_data = monthly_data[1]["saving"]

        accounting_month = AccountingYear(now_date="2025-03-01", start_month=4)

        saving_by_month = SavingByMonth(
            accounting_time=accounting_month,
            saving_ctl_data=saving_ctl_data,
            saving_data=saving_data
            )
        buttons = saving_by_month._buttons()
        assert len(buttons) == 2

    def test_updatemenus(self, monthly_data):
        saving_data = monthly_data[0]["saving"]
        saving_ctl_data = monthly_data[1]["saving"]

        accounting_month = AccountingYear(now_date="2025-03-01", start_month=4)

        saving_by_month = SavingByMonth(
            accounting_time=accounting_month,
            saving_ctl_data=saving_ctl_data,
            saving_data=saving_data
            )
        updatemenus = saving_by_month._updatemenus()
        assert updatemenus[0]["type"] == "buttons"
        assert len(updatemenus[0]["buttons"]) == 2