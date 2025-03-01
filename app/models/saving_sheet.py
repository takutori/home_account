import gspread

import pandas as pd

from app.models.gspread_workbook import Sheet

class SavingControlSheet(Sheet):
    """
    貯金管理シートを扱う。支出のカテゴリーデータもここから。
    """
    def __init__(self, sheet: gspread.worksheet.Worksheet):
        super().__init__(sheet=sheet)

    def get_saving_ctg(self) -> list[str]:
        """
        貯金項目-貯金方法でカテゴリとしたリストを出力

        Returns
        -------
        list[str]
            貯金項目-貯金方法でカテゴリ
        """
        ctg_list = (self._data["貯金項目"] + "-" + self._data["貯金方法"]).tolist()

        return ctg_list


class SavingDataSheet(Sheet):
    """
    貯金データシートを扱う
    """
    def __init__(self, sheet: gspread.worksheet.Worksheet):
        super().__init__(sheet=sheet)
        self._time_format = "%Y-%m-%d"
        self._data["time"] = pd.to_datetime(self._data["time"], format=self._time_format)

    @property
    def time_format(self):
        return self._time_format

    def input_saving(self, date, ctg, how_to_save, amount):
        # make inserted data
        insert_data = [date, ctg, how_to_save, amount]
        # insert data
        index = len(self.sheet.get_all_values())
        self.sheet.insert_row(insert_data, index + 1)
