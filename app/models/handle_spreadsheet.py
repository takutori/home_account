import gspread
from google.oauth2.service_account import Credentials

import pandas as pd
import pdb


class HandleSpreadsheet:
    def __init__(self):
        self.secret_credentials_json_oath = 'src/keys/moneyproject-362103-c609fbcd77b0.json'
        self.spread_url = 'https://docs.google.com/spreadsheets/d/1hwEVP5fgU5ohwyRX_oatNmWczx_AJBxmF5DEn2qk4Sw/edit#gid=0'

    def _connect_spreadsheet(self):
        scopes = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
        ]

        credentials = Credentials.from_service_account_file(
            self.secret_credentials_json_oath,
            scopes=scopes
        )
        gc = gspread.authorize(credentials)
        workbook = gc.open_by_url(self.spread_url)

        return workbook

### 支出 ##################################################################
class BuyControlSheet(HandleSpreadsheet):
    """
    支出管理シートを扱う。支出のカテゴリーデータもここから。
    """
    def __init__(self):
        super().__init__()
        self.sheet_name = "支出管理"
        self.workbook = self._connect_spreadsheet()
        self.sheet = self.workbook.worksheet(self.sheet_name)

    def get_buy_ctl_data(self, col_range="ctg"):
        """
        col_range="ctg" -> カテゴリだけを取得
        col_range="ctl" -> 予算までを取得

        Returns
        -------
        _type_
            _description_
        """
        if col_range == "ctg":
            col_range_index = [0, 1, 2]
        elif col_range == "ctl":
            col_range_index = [0, 1, 2, 3, 4]
        data = pd.DataFrame(self.sheet.get_all_values())[col_range_index]
        columns = data.iloc[0, :].tolist()
        data = data.drop(0, axis=0)
        data.columns = columns

        return data

    def get_ctg_dict(self):
        data = self.get_buy_ctl_data()
        columns = data.columns.tolist()
        # data -> dict
        ctg_dict = {} # key : 0 value : {"固定変動" : 固定, "カテゴリー1" : 住居費, "カテゴリー2" : 家賃}
        index = 0
        for data_i in data.index:
            ctg_dict[index] = {col : data[col][data_i] for col in columns}
            index += 1

        return ctg_dict


class BuyDataSheet(HandleSpreadsheet):
    """
    支出データシートを扱う
    """
    def __init__(self):
        super().__init__()
        self.sheet_name = "支出データ"
        self.workbook = self._connect_spreadsheet()
        self.sheet = self.workbook.worksheet(self.sheet_name)

    def input_buy(self, date, ctg, amount):
        # make inserted data
        insert_data = [date]+ ctg.split('-') +[amount]
        # insert data
        index = len(self.sheet.get_all_values())
        self.sheet.insert_row(insert_data, index + 1)

    def get_buy_df(self):
        data = self.sheet.get_all_values()
        columns = data.pop(0)

        return pd.DataFrame(data, columns=columns)


### 収入 ##################################################################
class IncomeControlSheet(HandleSpreadsheet):
    """
    収入管理シートを扱う。支出のカテゴリーデータもここから。
    """
    def __init__(self):
        super().__init__()
        self.sheet_name = "収入カテゴリー"
        self.workbook = self._connect_spreadsheet()
        self.sheet = self.workbook.worksheet(self.sheet_name)

    def get_income_ctl_data(self, col_range="ctg"):
        """
        if col_range == "ctg":
            col_range_index = [0, 1, 2]
        elif col_range == "ctl":
            col_range_index = [0, 1, 2, 3, 4]
        """
        data = pd.DataFrame(self.sheet.get_all_values())
        # 列名を一行目の値に変更
        data.columns = data.iloc[0]
        data = data.drop(data.index[0])

        return data

    def get_income_ctg(self):
        data = self.get_income_ctl_data()
        ctg_list = data["収入カテゴリー"].tolist()[0:-1]

        return ctg_list

    def get_income_pay_day(self):
        data = self.get_income_ctl_data()
        ctg_list = data["収入カテゴリー"].tolist()[0:-1]
        payday_list = data["給料日"].tolist()[0:-1]
        payday_dict = {ctg : payday for ctg, payday in zip(ctg_list, payday_list)}

        return payday_dict

    def get_income_bonus_month(self):
        data = self.get_income_ctl_data()
        ctg_list = data["収入カテゴリー"].tolist()[0:-1]
        bonus_month_list = data["ボーナス月"].tolist()[0:-1]
        bonus_dict = {ctg : bonus_month for ctg, bonus_month in zip(ctg_list, bonus_month_list)}

        return bonus_dict


class IncomeDataSheet(HandleSpreadsheet):
    """
    収入データシートを扱う
    """
    def __init__(self):
        super().__init__()
        self.sheet_name = "収入データ"
        self.workbook = self._connect_spreadsheet()
        self.sheet = self.workbook.worksheet(self.sheet_name)

    def input_income(self, date, ctg, income_type, income, residual_income):
        # make inserted data
        insert_data = [date, ctg, income_type, income, residual_income]
        # insert data
        index = len(self.sheet.get_all_values())
        self.sheet.insert_row(insert_data, index + 1)

    def get_income_df(self):
        data = self.sheet.get_all_values()
        columns = data.pop(0)

        return pd.DataFrame(data, columns=columns)




### 貯金 ##################################################################
class SavingControlSheet(HandleSpreadsheet):
    """
    貯金管理シートを扱う。支出のカテゴリーデータもここから。
    """
    def __init__(self):
        super().__init__()
        self.sheet_name = "貯金カテゴリー"
        self.workbook = self._connect_spreadsheet()
        self.sheet = self.workbook.worksheet(self.sheet_name)

    def get_saving_ctl_data(self, col_range="ctg"):
        data = pd.DataFrame(self.sheet.get_all_values())
        # 列名を一行目の値に変更
        data.columns = data.iloc[0]
        data = data.drop(data.index[0])

        return data

    def get_saving_ctg(self):
        data = self.get_saving_ctl_data()
        ctg_list = (data["貯金項目"] + "-" + data["貯金方法"]).tolist()

        return ctg_list


class SavingDataSheet(HandleSpreadsheet):
    """
    貯金データシートを扱う
    """
    def __init__(self):
        super().__init__()
        self.sheet_name = "貯金データ"
        self.workbook = self._connect_spreadsheet()
        self.sheet = self.workbook.worksheet(self.sheet_name)

    def input_saving(self, date, ctg, how_to_save, amount):
        # make inserted data
        insert_data = [date, ctg, how_to_save, amount]
        # insert data
        index = len(self.sheet.get_all_values())
        self.sheet.insert_row(insert_data, index + 1)

    def get_saving_df(self):
        data = self.sheet.get_all_values()
        columns = data.pop(0)

        return pd.DataFrame(data, columns=columns)









