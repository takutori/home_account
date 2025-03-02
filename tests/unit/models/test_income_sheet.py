
import pandas as pd
import pytest
from app.models.gspread_workbook import WorkBook
from app.models.income_sheet import IncomeControlSheet, IncomeDataSheet




class TestIncomeControlSheet:
    @pytest.mark.parametrize("mock_sheet", ["収入カテゴリー"], indirect=True)
    def test_init(self, mock_sheet):
        buy_control_sheet = IncomeControlSheet(sheet=mock_sheet)
        assert buy_control_sheet.sheet_name == "収入カテゴリー"
        assert buy_control_sheet.data.columns.tolist() == [
            "収入カテゴリー",
            "給料日",
            "月収",
            "月手取り",
            "ボーナス月",
            "ボーナス",
            "ボーナス手取り",
            "年収",
            "手取り年収"
            ]

    @pytest.mark.parametrize("mock_sheet", ["収入カテゴリー"], indirect=True)
    def test_get_income_ctg(self, mock_sheet):
        buy_control_sheet = IncomeControlSheet(sheet=mock_sheet)
        income_ctg = buy_control_sheet.get_income_ctg()
        assert income_ctg[3:] == ["Homepage", "その他"]

    @pytest.mark.parametrize("mock_sheet", ["収入カテゴリー"], indirect=True)
    def test_get_income_pay_day(self, mock_sheet):
        buy_control_sheet = IncomeControlSheet(sheet=mock_sheet)
        payday_dict = buy_control_sheet.get_income_pay_day()

        assert payday_dict["Homepage"] == "臨時"
        assert payday_dict["その他"] == "臨時"
        assert len(payday_dict) == 5

    @pytest.mark.parametrize("mock_sheet", ["収入カテゴリー"], indirect=True)
    def test_get_income_bonus_day(self, mock_sheet):
        buy_control_sheet = IncomeControlSheet(sheet=mock_sheet)
        bonus_dict = buy_control_sheet.get_income_bonus_day()

        assert len(bonus_dict) == 1

class TestIncomeDataSheet:
    @pytest.mark.parametrize("mock_sheet", ["収入データ"], indirect=True)
    def test_init(self, mock_sheet):
        buy_data_sheet = IncomeDataSheet(sheet=mock_sheet)
        assert buy_data_sheet.sheet_name == "収入データ"
        assert buy_data_sheet.data.columns.tolist() == ["time", "category", "income_type", "income", "residual_income"]

    @pytest.mark.skip(reason="APIを使用するため基本はスキップ")
    def test_input_buy(self):
        workbook = WorkBook()
        buy_data_sheet = IncomeDataSheet(sheet=workbook.sheet("支出データ"))
        values = [
            ["3000-01-25", "ホームページ", "月給", 577124, 438986],
            ["3000-01-02", "その他", "臨時", 4000, 3000],
        ]

        buy_data_sheet.input_buy(values=values)
