from abc import ABCMeta, abstractmethod

from datetime import datetime
import pdb


class ThisTime(metaclass=ABCMeta):
    def __init__(self):
        self.date_format = '%Y-%m-%d'
        # 現在の日時
        self.now_date = datetime.now()

    def get_date_format(self):
        return self.date_format

    def get_now_date(self):
        return self.now_date

    @abstractmethod
    def get_date_interval(self):
        raise NotImplementedError



class ThisMonth(ThisTime):
    def __init__(self):
        super().__init__()
        # 今月のKPI対象日時
        if self.now_date.day <= 24:
            if self.now_date.month - 1 <= 0:
                start_date = self.now_date.replace(year=self.now_date.year - 1, month = 12, day=25)
            else:
                start_date = self.now_date.replace(month = self.now_date.month-1, day=25)

            finish_date = self.now_date.replace(day=25)
        else:
            start_date = self.now_date.replace(day=25)

            if self.now_date.month + 1 > 12:
                finish_date = self.now_date.replace(year=self.now_date.year + 1, month=1, day=25)
            else:
                finish_date = self.now_date.replace(month=self.now_date.month+1, day=25)

        start_date = datetime(year=start_date.year, month=start_date.month, day=start_date.day, hour=0, minute=0, second=0, microsecond=0)
        finish_date = datetime(year=finish_date.year, month=finish_date.month, day=finish_date.day, hour=0, minute=0, second=0, microsecond=0)
        self.date_interval = [start_date, finish_date]

    def get_date_interval(self):
        return self.date_interval

    def get_days_left(self):
        return (self.date_interval[1] - self.now_date).days


class ThisYear(ThisTime):
    def __init__(self):
        super().__init__()
        # 現在の日時
        self.now_date = datetime.now()

        # 一年の範囲を取得
        # 今年度の場合
        self.date_interval = self.set_year_interval_with_start_month4()
        # 今年の場合
        #self.date_interval = self.set_year_interval_with_start_month1()

    def set_year_interval_with_start_month4(self):
        if self.now_date.month <= 3:
            start_date = datetime(year=self.now_date.year-1, month=4, day=1, hour=0, minute=0, second=0, microsecond=0)
            finish_date = datetime(year=self.now_date.year, month=4, day=1, hour=0, minute=0, second=0, microsecond=0)
        else:
            start_date = datetime(year=self.now_date.year, month=4, day=1, hour=0, minute=0, second=0, microsecond=0)
            finish_date = datetime(year=self.now_date.year+1, month=4, day=1, hour=0, minute=0, second=0, microsecond=0)

        date_interval = [start_date, finish_date]

        return date_interval

    def set_year_interval_with_start_month1(self):
        start_date = datetime(year=self.now_date.year, month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        finish_date = datetime(year=self.now_date.year+1, month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        date_interval = [start_date, finish_date]

        return date_interval

    def get_date_interval(self):
        return self.date_interval

    def get_month_left(self):
        """
        今月を含まず、残り何ヶ月あるか計算
        """
        return (self.date_interval[1].year - self.now_date.year) * 12 + self.date_interval[1].month - self.now_date.month - 1