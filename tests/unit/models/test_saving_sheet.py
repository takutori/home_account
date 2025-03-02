
import pandas as pd
import pytest
from app.models.gspread_workbook import WorkBook
from app.models.saving_sheet import SavingControlSheet, SavingDataSheet




class TestSavingControlSheet:
    @pytest.mark.parametrize("mock_sheet", ["貯金カテゴリー"], indirect=True)
    def test_init(self, mock_sheet):
        saving_ctl_sheet = SavingControlSheet(sheet=mock_sheet)
        assert saving_ctl_sheet.sheet_name == "貯金カテゴリー"
        assert saving_ctl_sheet.data.columns.tolist() == [
            "貯金項目",
            "貯金方法",
            "目標額",
            "貯金額/月",
            "ボーナス6月分",
            "ボーナス12月分",
            "貯金額合計/1年",
            "貯金年数",
            "年利",
            "貯金額合計",
            "貯金達成度",
            "過貯金",
            "過貯金/1年"
        ]

    @pytest.mark.parametrize("mock_sheet", ["貯金カテゴリー"], indirect=True)
    def test_get_saving_ctg(self, mock_sheet):
        saving_ctl_sheet = SavingControlSheet(sheet=mock_sheet)
        ctg = saving_ctl_sheet.get_saving_ctg()
        assert ctg == ['老後貯金-積立NISA', '家族貯金-預金', '家族貯金-積立NISA', '臨時出費貯金-預金', '結婚貯金-積立NISA', '結婚貯金-預金']


class TestSavingDataSheet:
    @pytest.mark.parametrize("mock_sheet", ["貯金データ"], indirect=True)
    def test_init(self, mock_sheet):
        buy_data_sheet = SavingDataSheet(sheet=mock_sheet)
        assert buy_data_sheet.sheet_name == "貯金データ"
        assert buy_data_sheet.data.columns.tolist() == ["time", "category", "how_to_save", "amount"]

    @pytest.mark.skip(reason="APIを使用するため基本はスキップ")
    def test_input_buy(self):
        workbook = WorkBook()
        buy_data_sheet = SavingDataSheet(sheet=workbook.sheet("貯金データ"))
        values = [
            ["3000-01-01", "臨時出費貯金", "預金", 48000],
            ["3000-01-02", "老後貯金", "積立NISA",  3000],
        ]

        buy_data_sheet.input_buy(values=values)
