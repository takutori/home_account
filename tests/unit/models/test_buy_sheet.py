
import pandas as pd
import pytest
from app.models.gspread_workbook import WorkBook
from app.models.buy_sheet import BuyControlSheet, BuyDataSheet




class TestBuyControlSheet:
    @pytest.mark.parametrize("mock_sheet", ["支出管理"], indirect=True)
    def test_init(self, mock_sheet):
        buy_control_sheet = BuyControlSheet(sheet=mock_sheet)
        assert buy_control_sheet.sheet_name == "支出管理"
        assert buy_control_sheet.data.columns.tolist() == ["固定変動", "カテゴリー1", "カテゴリー2", "予算", "割合"]

    @pytest.mark.parametrize("mock_sheet", ["支出管理"], indirect=True)
    def test_get_ctg_dict(self, mock_sheet):
        buy_control_sheet = BuyControlSheet(sheet=mock_sheet)
        ctg_dict = buy_control_sheet.get_ctg_dict()
        assert ctg_dict["交際費"] == ["友達", "恋愛"]
        assert ctg_dict["借金"] == ["奨学金"]


class TestBuyDataSheet:
    @pytest.mark.parametrize("mock_sheet", ["支出データ"], indirect=True)
    def test_init(self, mock_sheet):
        buy_data_sheet = BuyDataSheet(sheet=mock_sheet)
        assert buy_data_sheet.sheet_name == "支出データ"
        assert buy_data_sheet.data.columns.tolist() == ["time", "fix_variable", "category1", "category2", "amount"]

    @pytest.mark.skip(reason="APIを使用するため基本はスキップ")
    def test_input_buy(self):
        workbook = WorkBook()
        buy_data_sheet = BuyDataSheet(sheet=workbook.sheet("支出データ"))
        values = [
            ["3000-01-01", "固定", "住居費", "家賃", 118000],
            ["3000-01-02", "変動", "食費", "一人贅沢", 3000],
        ]

        buy_data_sheet.input_buy(values=values)