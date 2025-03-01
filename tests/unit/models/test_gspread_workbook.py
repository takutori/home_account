import pytest
import gspread
from app.models.gspread_workbook import SpreadSheetConector, WorkBook


class TestSpreadSheetConnec:
    """
    google spread sheetの接続テスト。
    APIの回数制限があるため、test_connectで接続できるかだけをテストする。
    """
    def test_init(self):
        spread_sheet_connector = SpreadSheetConector()
        assert spread_sheet_connector.status == "Not Connected"
        assert spread_sheet_connector.workbook is None

    @pytest.mark.skip(reason="APIを使用するため基本はスキップ")
    def test_connect(self):
        spread_sheet_connector = SpreadSheetConector()
        spread_sheet_connector.connect()
        assert spread_sheet_connector.status == "Connected"
        assert spread_sheet_connector.workbook is None


class TestWorkBook:
    @pytest.mark.skip(reason="APIを使用するため基本はスキップ")
    def test_sheet(self):
        workbook = WorkBook()
        sheet = workbook.sheet(sheet_name="支出データ")
        import pdb; pdb.set_trace()
        assert type(sheet) == gspread.worksheet.Worksheet

