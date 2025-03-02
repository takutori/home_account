from typing import Literal
import numpy as np
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta



class AccountingMonthKPI:
    """会計期間を絞った状態のデータを受け取り、各KPIを計算する"""
    def __init__(self, buy_data: pd.DataFrame, income_data: pd.DataFrame, saving_data: pd.DataFrame):
        """
        コンストラクタ

        Parameters
        ----------
        buy_data : pd.DataFrame
            支出データ
        income_data : pd.DataFrame
            収入データ
        saving_data : pd.DataFrame
            貯金データ
        """
        self._buy_data = buy_data
        self._income_data = income_data
        self._saving_data = saving_data

    def calc_residual_income(self) -> int:
        # 手取りを計算
        return int(self._income_data["residual_income"].sum())

    def calc_saving(self) -> int:
        # 貯金額を計算
        return int(self._saving_data.loc[self._saving_data["amount"]>0, "amount"].sum())

    def calc_residual_income_minus_saving(self) -> int:
        # 貯金額を引いた可処分所得を計算
        return self.calc_residual_income() - self.calc_saving()

    def calc_amount(self) -> int:
        # 支出額の合計を計算
        return int(self._buy_data["amount"].sum())

    def calc_fixed_cost(self) -> int:
        # 固定費を計算
        return int(self._buy_data.loc[self._buy_data["fix_variable"] == "固定", "amount"].sum())

    def calc_variable_cost(self) -> int:
        # 変動費を計算
        return int(self._buy_data.loc[self._buy_data["fix_variable"] == "変動", "amount"].sum())

    def calc_family_cost(self) -> int:
        # 家族費を計算
        return int(self._buy_data.loc[self._buy_data["category1"] == "家族費", "amount"].sum())

    def calc_amount_avoid_family(self) -> int:
        # 家族費を除いた支出額を計算
        return int(self._buy_data.loc[self._buy_data["category1"] != "家族費", "amount"].sum())

    def calc_work_book_cost(self) -> int:
        # 仕事カテゴリーの本の合計金額を計算
        work_book_cost = int(self._buy_data.loc[
            (self._buy_data["category1"] == "仕事費") &
            (self._buy_data["category2"] == "本")
        , "amount"].sum())
        return work_book_cost

    def calc_engel_coefficient(self) -> float:
        # 食費が「家族費を除いた支出額」の何割かを計算
        male_cost = int(self._buy_data.loc[self._buy_data["category1"] == "食費", "amount"].sum())
        return male_cost / self.calc_amount_avoid_family()

    def calc_extraordinary_cost(self) -> int:
        # 臨時出費費
        return int(self._buy_data.loc[self._buy_data["category1"] == "臨時費", "amount"].sum())



class AccountingYearKPI:
    """会計期間を絞った状態のデータを受け取り、各KPIを計算する"""
    def __init__(self, buy_data: pd.DataFrame, income_data: pd.DataFrame, saving_data: pd.DataFrame):
        """
        コンストラクタ

        Parameters
        ----------
        buy_data : pd.DataFrame
            支出データ
        income_data : pd.DataFrame
            収入データ
        saving_data : pd.DataFrame
            貯金データ
        """
        self._buy_data = buy_data
        self._income_data = income_data
        self._saving_data = saving_data

    def calc_income(self) -> int:
        return int(self._income_data["income"].sum())

    def calc_residual_income(self) -> int:
        return int(self._income_data["residual_income"].sum())


    def calc_saving(self) -> int:
        # 貯金額を計算
        return int(self._saving_data["amount"].sum())


class AccountingUntilNowKPI:
    def __init__(self, income_data: pd.DataFrame):
        """
        コンストラクタ

        Parameters
        ----------
        buy_data : pd.DataFrame
            支出データ
        income_data : pd.DataFrame
            収入データ
        saving_data : pd.DataFrame
            貯金データ
        """
        self._income_data = income_data

    def calc_pred_income(self, accounting_interval: list[datetime], accounting_start_month: Literal[1, 4], bonus_days: list[str]):
        now_date = self._income_data["time"].max()
        now_income = int(self._income_data.loc[(accounting_interval[0] <= self._income_data["time"]) & (self._income_data["time"] <= now_date), "income"].sum())
        left_month = (accounting_interval[1].year - now_date.year) * 12 + accounting_interval[1].month - now_date.month - 1

        if left_month > 0:
            self._income_data.loc[:, ["year"]] = self._income_data.loc[:, "time"].dt.year
            self._income_data.loc[:, ["month"]] = self._income_data.loc[:, "time"].dt.month
            # 直近の月給
            if now_date.day < 25:
                month_diff = 1
            else:
                month_diff = 0
            latent_month_income = int(self._income_data.loc[
                (self._income_data["year"] == now_date.year) &
                (self._income_data["month"] == now_date.month-month_diff) &
                (self._income_data["income_type"] == "月給")
            , "income"].sum())
            # 残りの累積月給
            remaining_month_income = left_month * latent_month_income
            # まだもらってないbonusの日付を見つける
            if accounting_start_month == 1:
                until_bonus_days = [datetime(year=now_date.year, month=int(bonus_day.split("-")[0]), day=int(bonus_day.split("-")[1])) for bonus_day in bonus_days]
                remaining_bonus_days = [bonus_day for bonus_day in until_bonus_days if now_date < bonus_day]
            elif accounting_start_month == 4:
                until_bonus_days = []
                for bonus_month_day in bonus_days:
                    bonus_month = int(bonus_month_day.split("-")[0])
                    bonus_day = int(bonus_month_day.split("-")[1])
                    if bonus_month < 4:
                        until_bonus_days.append(datetime(year=now_date.year + 1, month=bonus_month_day, day=bonus_day))
                    else:
                        until_bonus_days.append(datetime(year=now_date.year, month=bonus_month, day=bonus_day))
                    remaining_bonus_days = [bonus_day for bonus_day in until_bonus_days if (now_date < bonus_day) & (bonus_day < accounting_interval[1])]
            # もらってないbonusの金額を去年の同じ日にいくらもらっていたかを見て概算する
            if len(remaining_bonus_days) != 0:
                latent_remaining_bonus_days = [bonus_day + relativedelta(years=-1) for bonus_day in remaining_bonus_days]
                remaining_bonus_income = int(self._income_data.loc[self._income_data["time"].isin(latent_remaining_bonus_days), "income"].sum())
            else:
                remaining_bonus_income = 0
            return now_income + remaining_month_income + remaining_bonus_income
        else:
            return now_income
