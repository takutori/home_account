from typing import Literal
from abc import ABC, ABCMeta, abstractmethod

import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

import json


class SpreadSheetConector:
    def __init__(self):
        self.secret_credentials_json_oath = 'app/keys/moneyproject-362103-c609fbcd77b0.json'
        json_open = open('app/keys/spread_url.json', 'r')
        self.spread_url = json.load(json_open)["url"]
        self._status: Literal["Not Connected", "Connected"]  = "Not Connected"
        self._workbook = None

    def connect(self):
        """
        google spread sheetに接続する

        _extended_summary_
        """
        scopes = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
        ]

        credentials = Credentials.from_service_account_file(
            self.secret_credentials_json_oath,
            scopes=scopes
        )
        gc = gspread.authorize(credentials)
        self._workbook = gc.open_by_url(self.spread_url)
        self._status = "Connected"

    @property
    def status(self) -> Literal["Not Connected", "Connected"]:
        return self._status

    @property
    def workbook(self) -> gspread.spreadsheet.Spreadsheet:
        return self._workbook

class WorkBook(SpreadSheetConector):
    def __init__(self):
        super().__init__()
        super().connect()

    def sheet(self, sheet_name: str) -> gspread.worksheet.Worksheet:
        """
        指定されたシート名に一致するシートをAPIで取得する

        Parameters
        ----------
        sheet_name : str
            シート名

        Returns
        -------
        gspread.worksheet.Worksheet
            APIで取得したシート
        """
        return self.workbook.worksheet(sheet_name)

class Sheet(metaclass = ABCMeta):
    def __init__(self, sheet: gspread.worksheet.Worksheet):
        """
        ワークブックを受け取り、データを抽出しておく。

        Parameters
        ----------
        workbook : gspread.spreadsheet.Spreadsheet
            google spread sheet

        """
        self._sheet = sheet
        self._sheet_name = self._sheet._properties["title"]
        # データの読み込み
        self._data = pd.DataFrame(self._sheet.get_all_values())
        self._data = self._shit_first_row_to_column_name(data=self._data)

    def _shit_first_row_to_column_name(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        列名が0, 1, 2, 3,...となっていて、一行目に本当の列名がある問題を修正。
        ただし、indexが0, 1, 2, ...と連番になっていることが前提。
        そうでないと

        Parameters
        ----------
        data : pd.DataFrame
            修正前のデータ

        Returns
        -------
        pd.DataFrame
            修正後のデータ
        """
        data = data.reset_index(drop=True) # index=0が複数あると全て次のdropで消えてしまうため
        columns = data.iloc[0, :].tolist()
        data = data.drop(0, axis=0)
        data.columns = columns

        return data

    @property
    def sheet_name(self) -> str:
        return self._sheet_name

    @property
    def data(self) -> pd.DataFrame:
        return self._data

