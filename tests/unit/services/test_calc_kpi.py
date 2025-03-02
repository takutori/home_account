
import pandas as pd
from datetime import datetime
import pytest
from app.services.calc_kpi import AccountingMonthKPI, AccountingYearKPI, AccountingUntilNowKPI


@pytest.fixture
def buy_data():
    return pd.read_csv("../../data/buy_data.csv")




class TestAccountingMonthKPI:
    @pytest.fixture(scope="module")
    def data(self):
        excel_name = "test_2024-12-25_2024-01-25_household_account.xlsx"
        buy_data = pd.read_excel("tests/data/" + excel_name, sheet_name="支出データ")
        buy_data["time"] = pd.to_datetime(buy_data["time"], format="%Y-%m-%d")

        income_data = pd.read_excel("tests/data/" + excel_name, sheet_name="収入データ")
        income_data["time"] = pd.to_datetime(income_data["time"], format="%Y-%m-%d")

        saving_data = pd.read_excel("tests/data/" + excel_name, sheet_name="貯金データ")
        saving_data["time"] = pd.to_datetime(saving_data["time"], format="%Y-%m-%d")

        return buy_data, income_data, saving_data

    def test_kpi_2024_12_25_2025_01_25(self, data):
        buy_data = data[0]
        income_data = data[1]
        saving_data = data[2]

        accounting_month_kpi = AccountingMonthKPI(
            buy_data=buy_data,
            income_data=income_data,
            saving_data=saving_data
        )

        assert accounting_month_kpi.calc_residual_income() == 300900
        assert accounting_month_kpi.calc_saving() == 10000
        assert accounting_month_kpi.calc_residual_income_minus_saving() == 300900 - 10000
        assert accounting_month_kpi.calc_amount() == 206037
        assert accounting_month_kpi.calc_fixed_cost() == 75514
        assert accounting_month_kpi.calc_variable_cost() == 130523
        assert accounting_month_kpi.calc_amount_avoid_family() == 194082
        assert accounting_month_kpi.calc_work_book_cost() == 3240
        assert accounting_month_kpi.calc_engel_coefficient() == 11914 / 194082
        assert accounting_month_kpi.calc_extraordinary_cost() == 0


class TestAccountingYearKPI:
    @pytest.fixture(scope="module")
    def data(self):
        excel_name = "test_2024_2025_household_account.xlsx"
        buy_data = pd.read_excel("tests/data/" + excel_name, sheet_name="支出データ")
        buy_data["time"] = pd.to_datetime(buy_data["time"], format="%Y-%m-%d")

        income_data = pd.read_excel("tests/data/" + excel_name, sheet_name="収入データ")
        income_data["time"] = pd.to_datetime(income_data["time"], format="%Y-%m-%d")

        saving_data = pd.read_excel("tests/data/" + excel_name, sheet_name="貯金データ")
        saving_data["time"] = pd.to_datetime(saving_data["time"], format="%Y-%m-%d")

        return buy_data, income_data, saving_data

    def test_kpi_2024_2025(self, data):
        buy_data = data[0]
        income_data = data[1]
        saving_data = data[2]

        accounting_year_kpi = AccountingYearKPI(
            buy_data=buy_data,
            income_data=income_data,
            saving_data=saving_data
        )
        assert accounting_year_kpi.calc_income() == 5156110
        assert accounting_year_kpi.calc_residual_income() == 4110815
        assert accounting_year_kpi.calc_saving() == 225000

class TestAccountingUntilNowKPI:
    def test_calc_pred_income_start4(self, income_data):
        accounting_until_now_kpi = AccountingUntilNowKPI(
            income_data=income_data,
        )
        accounting_start_month = 4
        accounting_interval = [
            datetime(year=2024, month=accounting_start_month, day=1),
            datetime(year=2025, month=accounting_start_month, day=1)
        ]
        pred_income = accounting_until_now_kpi.calc_pred_income(
            accounting_interval=accounting_interval,
            accounting_start_month=accounting_start_month,
            bonus_days=["06-10", "12-10"]
            )
        # now_income + remaining_month_income + remaining_bonus_income
        # 5156110 + 370000 + 0
        assert pred_income == 5526110

    def test_calc_pred_income_start1(self, income_data):
        income_data["time"] = income_data["time"] - pd.DateOffset(months=3)

        accounting_until_now_kpi = AccountingUntilNowKPI(
            income_data=income_data,
        )
        accounting_start_month = 1
        accounting_interval = [
            datetime(year=2024, month=accounting_start_month, day=1),
            datetime(year=2025, month=accounting_start_month, day=1)
        ]
        pred_income = accounting_until_now_kpi.calc_pred_income(
            accounting_interval=accounting_interval,
            accounting_start_month=accounting_start_month,
            bonus_days=["06-10", "12-10"]
            )
        assert pred_income == 5526110

    def test_calc_pred_income_until_1bonus(self, income_data):
        data = income_data.loc[income_data["time"] <= datetime(year=2024, month=8, day=1)]
        accounting_until_now_kpi = AccountingUntilNowKPI(
            income_data=data,
        )
        accounting_start_month = 4
        accounting_interval = [
            datetime(year=2024, month=accounting_start_month, day=1),
            datetime(year=2025, month=accounting_start_month, day=1)
        ]
        pred_income = accounting_until_now_kpi.calc_pred_income(
            accounting_interval=accounting_interval,
            accounting_start_month=accounting_start_month,
            bonus_days=["06-10", "12-10"]
            )
        assert pred_income == 5160000

    def test_calc_pred_income_no_until_income(self, income_data):
        data = income_data.loc[income_data["time"] <= datetime(year=2024, month=4 ,day=1)]
        accounting_until_now_kpi = AccountingUntilNowKPI(
            income_data=data,
        )
        accounting_start_month = 4
        accounting_interval = [
            datetime(year=2023, month=accounting_start_month, day=1),
            datetime(year=2024, month=accounting_start_month, day=1)
        ]
        pred_income = accounting_until_now_kpi.calc_pred_income(
            accounting_interval=accounting_interval,
            accounting_start_month=accounting_start_month,
            bonus_days=["06-10", "12-10"]
            )
        assert pred_income == 5190000
