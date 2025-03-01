import gspread

import pandas as pd

from app.models.gspread_workbook import Sheet



### 支出 ##################################################################
class BuyControlSheet(Sheet):
    """支出管理シートを扱う"""
    def __init__(self, sheet: gspread.worksheet.Worksheet):
        super().__init__(sheet=sheet)
        self._data = self._filter_column_num(data=self._data)

    def _filter_column_num(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        列を左から5行目までにする

        Parameters
        ----------
        data : pd.DataFrame
            修正前のデータ

        Returns
        -------
        pd.DataFrame
            修正後のデータ
        """
        return data.iloc[:, 0:5]

    def get_ctg_dict(self) -> dict[str, list[str]]:
        """
        支出カテゴリのカテゴリー1に対応する複数のカテゴリー2の値をリストにした辞書型を出力する。
        dict[カテゴリー1: [カテゴリー2, カテゴリー2, ....]]のイメージ。

        Returns
        -------
        dict
            カテゴリー1に対応する複数のカテゴリー2の値をリストにした辞書型を出力
        """
        return self._data.groupby("カテゴリー1")["カテゴリー2"].apply(list).to_dict()


class BuyDataSheet(Sheet):
    """支出データシートを扱う"""
    def __init__(self, sheet: gspread.worksheet.Worksheet):
        super().__init__(sheet=sheet)
        self._time_format = "%Y-%m-%d"
        self._data["time"] = pd.to_datetime(self._data["time"], format=self._time_format)

    @property
    def time_format(self):
        return self._time_format

    def input_buy(self, values: list):
        """
        シートに複数行追加する。

        Parameters
        ----------
        values : list
            追加するデータ。二次元のリスト。
        """
        self._sheet.append_rows(
            values=values,
            insert_data_option="INSERT_ROWS"
        )