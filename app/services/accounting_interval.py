from abc import ABCMeta, abstractmethod
from typing import Literal
from datetime import datetime
from dateutil.relativedelta import relativedelta

class ThisTime(metaclass=ABCMeta):
    def __init__(self, now_date: str | None=None):
        """
        now_dateは現在注目している日付。この注目している日付をもとに会計期間を計算する。

        Parameters
        ----------
        now_date : str | None, optional
            現在注目している日付。Noneの場合は現在時刻
        """
        self._date_format = '%Y-%m-%d'
        if now_date is None:
            # 現在の日時
            self._now_date = datetime.now()
        else:
            self._now_date = datetime.strptime(now_date, self._date_format)

    @property
    def date_format(self) -> str:
        return self._date_format

    @property
    def now_date(self) -> datetime:
        return self._now_date

    @abstractmethod
    def get_date_interval(self) -> list[datetime]:
        raise NotImplementedError



class ThisMonth(ThisTime):
    def __init__(self, now_date=None):
        super().__init__(now_date=now_date)

    def get_date_interval(self) -> list[datetime]:
        """
        今月の会計期間を算出。
        基本的には24日〆とし、25日から次の会計期間に移行するものとする。

        Returns
        -------
        list[datetime]
            今月の会計期間。left <= 会計期間 < rightであることに注意。
        """

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
        date_interval = [start_date, finish_date]
        return date_interval

    def get_days_left(self) -> datetime:
        """
        月の残りの日を数える

        Returns
        -------
        datetime
            残りの日
        """
        date_interval = self.get_date_interval()
        return (date_interval[1] - self._now_date).days

    def get_last_day(self) -> datetime:
        """
        今月の最終日を出力する

        Returns
        -------
        datetime
            今月の最終日
        """
        next_month_first_date = self._now_date + relativedelta(months=1)
        next_month_first_date = next_month_first_date.replace(day=1)
        this_month_last_date = next_month_first_date + relativedelta(days=-1)

        return this_month_last_date


class ThisYear(ThisTime):
    def __init__(self, now_date=None, start_month: Literal[1, 4]=4):
        """
        初期化

        Parameters
        ----------
        now_date : _type_, optional
            現在注目している日付。Noneの場合は現在時刻
        start_month : Literal[1, 4], optional
            会計期間のスタート月。1であれば今年。4であれば今年度。

        Raises
        ------
        ValueError
            1, 4以外の会計スタート月はエラーとして対応しない。

        """
        super().__init__(now_date=now_date)
        if (start_month == 1) or (start_month == 4):
            self._start_month = start_month
        else:
            raise ValueError(f"{start_month}月スタートの会計期間は現状設定できません。")

    def get_date_interval(self) -> list[datetime]:
        if self._start_month == 1:
            start_date = datetime(year=self.now_date.year, month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            finish_date = datetime(year=self.now_date.year+1, month=1, day=1, hour=0, minute=0, second=0, microsecond=0)

            return [start_date, finish_date]
        elif self._start_month == 4:
            if self.now_date.month <= 3:
                start_date = datetime(year=self.now_date.year-1, month=4, day=1, hour=0, minute=0, second=0, microsecond=0)
                finish_date = datetime(year=self.now_date.year, month=4, day=1, hour=0, minute=0, second=0, microsecond=0)
            else:
                start_date = datetime(year=self.now_date.year, month=4, day=1, hour=0, minute=0, second=0, microsecond=0)
                finish_date = datetime(year=self.now_date.year+1, month=4, day=1, hour=0, minute=0, second=0, microsecond=0)

            return [start_date, finish_date]

    def get_month_left(self):
        """
        今月を含まず、残り何ヶ月あるか計算
        """
        return (self.date_interval[1].year - self.now_date.year) * 12 + self.date_interval[1].month - self.now_date.month - 1