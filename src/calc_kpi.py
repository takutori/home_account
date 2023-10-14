import numpy as np
import pandas as pd

from datetime import datetime

from handle_spreadsheet import BuyControlSheet, BuyDataSheet, IncomeControlSheet, IncomeDataSheet, ThisMonth

import pdb

class CalcKPI:
    def __init__(self):
        self.saving_amount = 110000 # 後で、ボーナス月にも対応した貯金額を取得できるようにする。
        # 今月の日時情報を取得
        this_month = ThisMonth()
        self.date_format = this_month.get_date_format()
        self.now_date = this_month.get_now_date()
        self.date_interval = this_month.get_date_interval()

        # 購入データ
        buy_data_sheet = BuyDataSheet()
        self.buy_df = buy_data_sheet.get_buy_df()
        self.buy_df["time"] = pd.to_datetime(self.buy_df["time"], format=self.date_format)
        self.buy_df = self.buy_df.loc[
            (self.date_interval[0] <= self.buy_df["time"]) & (self.buy_df["time"] < self.date_interval[1])
            ]
        self.buy_df["amount"] = self.buy_df["amount"].astype(int)

        # 収入データ
        income_data_sheet = IncomeDataSheet()
        self.income_df = income_data_sheet.get_income_df()
        self.income_df["time"] = pd.to_datetime(self.income_df["time"], format=self.date_format)
        self.income_df = self.income_df.loc[
            (self.date_interval[0] <= self.income_df["time"]) & (self.income_df["time"] < self.date_interval[1])
        ]
        self.income_df["income"] = self.income_df["income"].astype(int)
        self.income_df["residual_income"] = self.income_df["residual_income"].astype(int)

    def calc_residual_income(self):
        # 貯金額を引いた可処分所得を計算
        return np.sum(self.income_df["residual_income"]) - self.saving_amount

    def calc_amount(self):
        # 支出額の合計を計算
        return np.sum(self.buy_df["amount"])

    def calc_fixed_cost(self):
        # 固定費を計算
        return np.sum(self.buy_df.loc[self.buy_df["fix_variable"] == "固定", "amount"])

    def calc_variable_cost(self):
        # 変動費を計算
        return np.sum(self.buy_df.loc[self.buy_df["fix_variable"] == "変動", "amount"])

    def calc_family_cost(self):
        return np.sum(self.buy_df.loc[self.buy_df["category1"] == "家族費", "amount"])

    def calc_amount_avoid_family(self):
        # 家族費を除いた支出額を計算
        return np.sum(self.buy_df.loc[self.buy_df["category1"] != "家族費", "amount"])

    def calc_work_book_cost(self):
        # 仕事カテゴリーの本の合計金額を計算
        work_book_cost = np.sum(self.buy_df.loc[
            (self.buy_df["category1"] == "仕事費") &
            (self.buy_df["category2"] == "本")
        , "amount"])
        return work_book_cost

    def calc_engel_coefficient(self):
        # 食費が「家族費を除いた支出額」の何割かを計算
        male_cost = np.sum(self.buy_df.loc[self.buy_df["category1"] == "食費", "amount"])
        return male_cost / self.calc_amount_avoid_family()

    def calc_extraordinary_cost(self):
        return np.sum(self.buy_df.loc[self.buy_df["category1"] == "臨時費", "amount"])



