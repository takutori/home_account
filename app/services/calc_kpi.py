import numpy as np
import pandas as pd

from datetime import datetime
from dateutil.relativedelta import relativedelta


from app.models.handle_spreadsheet import BuyControlSheet, BuyDataSheet, IncomeControlSheet, IncomeDataSheet, SavingControlSheet, SavingDataSheet
from handle_time import ThisMonth, ThisYear
import pdb

class CalcMonthKPI:
    def __init__(self, now_date: str=None):
        # 今月の日時情報を取得
        this_month = ThisMonth(now_date=now_date)
        self.date_format = this_month.get_date_format()
        self.now_date = this_month.get_now_date()
        self.date_interval = this_month.get_date_interval()

        # 購入データ
        buy_data_sheet = BuyDataSheet()
        self.buy_df = buy_data_sheet.get_buy_df()
        self.buy_df["time"] = pd.to_datetime(self.buy_df["time"], format=self.date_format)
        self.buy_df = self.buy_df.loc[
            (self.date_interval[0] < self.buy_df["time"]) & (self.buy_df["time"] <= self.date_interval[1])
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

        # 貯金データ
        saving_data_sheet = SavingDataSheet()
        self.saving_df = saving_data_sheet.get_saving_df()
        self.saving_df["time"] = pd.to_datetime(self.saving_df["time"], format=self.date_format)
        self.saving_df = self.saving_df.loc[(self.date_interval[0] <= self.saving_df["time"]) & (self.saving_df["time"] < self.date_interval[1])]
        self.saving_df["amount"] = self.saving_df["amount"].astype(int)

    def calc_income(self):
        # 手取りを計算
        return np.sum(self.income_df["residual_income"])

    def calc_saving(self):
        # 貯金額を計算
        return np.sum(self.saving_df.loc[self.saving_df["amount"]>0, "amount"])

    def calc_residual_income(self):
        # 貯金額を引いた可処分所得を計算
        if self.calc_saving() > 0:
            return self.calc_income() - self.calc_saving()
        else: # 貯金額合計がマイナスの場合、貯金が減っているため、この関数の出力は手取りそのまま
            return self.calc_income()

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



class CalcYearKPI:
    def __init__(self, now_date: str=None):
        # 今月の日時情報を取得
        this_year = ThisYear(now_date=now_date)
        self.now_date = this_year.get_now_date()
        self.date_format = this_year.get_date_format()
        self.date_interval = this_year.get_date_interval()
        # 今月を除く残りの月
        self.month_left = this_year.get_month_left()

        # 収入データ
        income_data_sheet = IncomeDataSheet()
        self.all_income_df = income_data_sheet.get_income_df()
        # 日付をdatetime型へ
        self.all_income_df["time"] = pd.to_datetime(self.all_income_df["time"])
        # income, residual_incomeを数値データへ
        self.all_income_df["income"] = self.all_income_df["income"].astype(int)
        self.all_income_df["residual_income"] = self.all_income_df["residual_income"].astype(int)
        # 今年のデータのみにする
        self.income_df = self.all_income_df.loc[
            (self.date_interval[0] <= self.all_income_df["time"]) &
            (self.all_income_df["time"] < self.date_interval[1])
        ]

        # 収入カテゴリを取得
        income_ctl_sheet = IncomeControlSheet()
        self.income_ctg = income_ctl_sheet.get_income_ctg()
        # その他カテゴリを定義
        self.payday_dict = income_ctl_sheet.get_income_pay_day()
        self.permanent_income_ctg = [ctg for ctg in self.payday_dict if self.payday_dict[ctg] != "臨時"] # 恒久的に給与が与えられる会社
        self.bonus_type_dict = income_ctl_sheet.get_income_bonus_month()
        self.bonus_income_ctg = [ctg for ctg in self.bonus_type_dict if self.bonus_type_dict[ctg] != "なし"] # ボーナスのある会社

        # 貯金データ
        saving_data_sheet = SavingDataSheet()
        self.saving_df = saving_data_sheet.get_saving_df()
        self.saving_df["time"] = pd.to_datetime(self.saving_df["time"], format=self.date_format)
        self.saving_df = self.saving_df.loc[(self.date_interval[0] <= self.saving_df["time"]) & (self.saving_df["time"] < self.date_interval[1])]
        self.saving_df["amount"] = self.saving_df["amount"].astype(int)

    def calc_income(self):
        return np.sum(self.income_df["income"])

    def calc_residual_income(self):
        return np.sum(self.income_df["residual_income"])

    def calc_pred_income(self):
        now_income = self.calc_income()
        pred = now_income
        if self.date_interval[1] < datetime.now():
            return now_income
        else:
            # 直近の月給*残りの月を予測値に加える
            for ctg in self.permanent_income_ctg:
                last_payday = self.income_df.loc[(self.income_df["category"] == ctg) & (self.income_df["income_type"] == "月給")]["time"].max()
                if len(self.income_df.loc[(self.income_df["time"] == last_payday) & (self.income_df["category"] == ctg)]["income"]) != 0:
                    last_income = self.income_df.loc[(self.income_df["time"] == last_payday) & (self.income_df["category"] == ctg)]["income"].iloc[-1]
                else:
                    last_income = 0

                this_month_payday = get_this_month_payday(
                    payday=self.payday_dict[ctg],
                    this_year = self.now_date.year,
                    this_month = self.now_date.month
                )
                if self.now_date < this_month_payday: # 今月の給料はまだ
                    pred += (self.month_left + 1) * last_income
                else:
                    pred += self.month_left * last_income

            # 直近一年間のボーナス平均も予測値に加える
            for ctg in self.bonus_income_ctg:
                last_date_interval = [
                    self.now_date - relativedelta(years=1),
                    self.now_date
                ]
                most_recent_1year_income_df = self.all_income_df.loc[
                    (last_date_interval[0] <= self.all_income_df["time"]) &
                    (self.all_income_df["time"] < last_date_interval[1]) &
                    (self.all_income_df["category"] == ctg) &
                    (self.all_income_df["income_type"] == "ボーナス")
                ]
                most_recent_1year_bonus_mean = np.mean(most_recent_1year_income_df["income"])

                bonus_month_day_list = self.bonus_type_dict[ctg].split("_")
                for bonus_month_day in bonus_month_day_list:
                    bonus_month = int(bonus_month_day.split("-")[0])
                    bonus_day = int(bonus_month_day.split("-")[1])

                    bonus_date = datetime(year=self.now_date.year, month=bonus_month, day=bonus_day, hour=0, minute=0, second=0, microsecond=0)
                    if self.now_date < bonus_date: # bunus_dateはまだ来てない
                        pred += most_recent_1year_bonus_mean

            return pred

    def calc_saving(self):
        # 貯金額を計算
        return np.sum(self.saving_df["amount"])


def get_this_month_payday(payday, this_year, this_month):
    """
    入力されたpayday（給料日）から今月の給料日を計算し、datetime型で出力

    Parameters
    ----------
    payday : _type_
        _description_
    this_year : _type_
        _description_
    this_month : _type_
        _description_
    """
    this_month_payday = None
    if payday == "末日":
        this_month_first_date = datetime(year=this_year, month=this_month, day=1, hour=0, minute=0, second=0, microsecond=0)
        next_month_first_date = this_month_first_date + relativedelta(months=1)
        this_month_payday = next_month_first_date - relativedelta(days=1)
    elif payday == "臨時":
        this_month_payday = None
    else:
        this_month_payday = datetime(year=this_year, month=this_month, day=25, hour=0, minute=0, second=0, microsecond=0)

    return this_month_payday

