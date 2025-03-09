import pytest
import pandas as pd
from datetime import datetime
import gspread
from app.models.gspread_workbook import SpreadSheetConector, WorkBook, Sheet


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

class TestSheet:
    @pytest.mark.parametrize("mock_sheet", ["支出管理"], indirect=True)
    def test_init(self, mock_sheet):
        """列名がシートの列名になっているかだけ確認"""
        sheet = Sheet(sheet=mock_sheet)
        assert sheet.data.columns.tolist()[:5] == ["固定変動", "カテゴリー1", "カテゴリー2", "予算", "割合"]

    @pytest.mark.parametrize("mock_sheet", ["支出管理"], indirect=True)
    def test_data(self, mock_sheet):
        sheet = Sheet(sheet=mock_sheet)
        assert len(sheet.data) == 38

    @pytest.mark.parametrize("mock_sheet", ["支出管理"], indirect=True)
    def test_sheet_name(self, mock_sheet):
        sheet = Sheet(sheet=mock_sheet)
        assert sheet.sheet_name == "支出管理"

    @pytest.mark.parametrize("mock_sheet", ["支出データ"], indirect=True)
    def test_sheet_name(self, mock_sheet):
        sheet = Sheet(sheet=mock_sheet)
        sheet.to_datetime("time")
        # 時刻の絞り込みでエラーが出なければOKとする。
        assert len(sheet.data.loc[sheet.data["time"] <= datetime(year=2024, month=12, day=31)]) > 0

    @pytest.mark.parametrize("mock_sheet", ["支出データ"], indirect=True)
    def test_accounting_data(self, mock_sheet, mock_accounting_month_20250121):
        sheet = Sheet(sheet=mock_sheet)
        sheet.to_datetime("time")
        accounting_data = sheet.accounting_data(accounting_time=mock_accounting_month_20250121)
        assert len(accounting_data) == 49

    @pytest.mark.parametrize("mock_sheet", ["支出管理"], indirect=True)
    def test_accounting_data_error(self, mock_sheet, mock_accounting_month_20250121):
        sheet = Sheet(sheet=mock_sheet)
        with pytest.raises(KeyError) as e:
            sheet.accounting_data(accounting_time=mock_accounting_month_20250121)
        assert "time列が存在しません" in str(e.value)



