import gspread

import pandas as pd

from app.models.gspread_workbook import Sheet


class IncomeControlSheet(Sheet):
    """収入管理シートを扱う"""
    def __init__(self, sheet: gspread.worksheet.Worksheet):
        super().__init__(sheet=sheet)
        self._data = self._filter_column_num(data=self._data)

    def _filter_column_num(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        列を左から9行目までにする

        Parameters
        ----------
        data : pd.DataFrame
            修正前のデータ

        Returns
        -------
        pd.DataFrame
            修正後のデータ

        """
        return data.iloc[:, 0:9]

    def get_income_ctg(self) -> list[str]:
        """
        収入カテゴリーのリストを出力する

        Returns
        -------
        list[str]
            収入カテゴリーのリスト

        """
        ctg_list = self._data["収入カテゴリー"].tolist()[:-1]

        return ctg_list

    def get_income_pay_day(self) -> dict[str, str]:
        """
        収入カテゴリーごとの給料日をまとめた辞書を出力する。

        Returns
        -------
        dict[str, str]
            収入カテゴリーごとの給料日をまとめた辞書

        """
        ctg_list = self.get_income_ctg()
        payday_list = self._data["給料日"].tolist()[:-1]
        payday_dict = {ctg : payday for ctg, payday in zip(ctg_list, payday_list)}

        return payday_dict

    def get_income_bonus_day(self) -> dict[str, list[str]]:
        """
        ボーナスの日付を収入カテゴリーごとに辞書型にして出力する。
        ただし、収入カテゴリーシートのボーナス月が'なし'となっている収入カテゴリーは辞書に入れない。

        Returns
        -------
        dict[str, list[str]]
            収入カテゴリーごとのボーナス日。日付は文字で'%d-%m'。
        """
        ctg_list = self.get_income_ctg()
        bonus_day_list = self._data["ボーナス月"].tolist()[:-1]
        bonus_dict = {ctg : bonus_day.split("_") for ctg, bonus_day in zip(ctg_list, bonus_day_list) if bonus_day != "なし"}

        return bonus_dict


class IncomeDataSheet(Sheet):
    """収入データシートを扱う"""
    def __init__(self, sheet: gspread.worksheet.Worksheet):
        super().__init__(sheet=sheet)
        self._time_format = "%Y-%m-%d"
        self._data["time"] = pd.to_datetime(self._data["time"], format=self._time_format)

    @property
    def time_format(self):
        return self._time_format

    def input_income(self, values: list[list]):
        """
        シートに複数行追加する。

        Parameters
        ----------
        values : list
            追加するデータ。二次元のリスト。
        """
        # TODO: マイナスの値は入力できないようにする。
        self._sheet.append_rows(
            values=values,
            insert_data_option="INSERT_ROWS"
        )
