
import pytest
from datetime import datetime

from app.services.accounting_interval import ThisTime, ThisMonth, ThisYear



class TestThisTime:

    ThisTime.__abstractmethods__ = set() # これがないと何故かオーバーライドしろというエラーが出る。

    def test_init(self):
        this_time = ThisTime(now_date=None)
        assert type(this_time.now_date) == datetime

        this_time = ThisTime(now_date="2021-01-01")
        assert this_time.now_date == datetime(year=2021, month=1, day=1)

class TestThisMonth:
    def test_get_date_interval(self):
        this_month = ThisMonth(now_date="2000-01-01")
        assert this_month.get_date_interval() == [
            datetime(year=1999, month=12, day=25),
            datetime(year=2000, month=1, day=25)
        ]

        this_month = ThisMonth(now_date="2000-01-24")
        assert this_month.get_date_interval() == [
            datetime(year=1999, month=12, day=25),
            datetime(year=2000, month=1, day=25)
        ]

        this_month = ThisMonth(now_date="2000-01-25")
        assert this_month.get_date_interval() == [
            datetime(year=2000, month=1, day=25),
            datetime(year=2000, month=2, day=25)
        ]

        this_month = ThisMonth(now_date="2000-01-26")
        assert this_month.get_date_interval() == [
            datetime(year=2000, month=1, day=25),
            datetime(year=2000, month=2, day=25)
        ]

        this_month = ThisMonth(now_date="1999-12-26")
        assert this_month.get_date_interval() == [
            datetime(year=1999, month=12, day=25),
            datetime(year=2000, month=1, day=25)
        ]

        this_month = ThisMonth(now_date="1999-12-24")
        assert this_month.get_date_interval() == [
            datetime(year=1999, month=11, day=25),
            datetime(year=1999, month=12, day=25)
        ]

    def test_get_days_left(self):
        this_month = ThisMonth(now_date="2000-01-24")
        assert this_month.get_days_left() == 1

        this_month = ThisMonth(now_date="1999-12-25")
        assert this_month.get_days_left() == 31

class TestThisYear:
    def test_get_date_interval(self):
        this_year = ThisYear(now_date="2000-01-01", start_month=1)
        assert this_year.get_date_interval() == [
            datetime(year=2000, month=1, day=1),
            datetime(year=2001, month=1, day=1)
        ]

        with pytest.raises(ValueError) as e:
            this_year = ThisYear(now_date="2000-01-01", start_month=3)
            assert "3月スタートの会計期間は現状設定できません。" in e.info

        this_year = ThisYear(now_date="2000-05-01", start_month=4)
        assert this_year.get_date_interval() == [
            datetime(year=2000, month=4, day=1),
            datetime(year=2001, month=4, day=1)
        ]

        this_year = ThisYear(now_date="2000-03-01", start_month=4)
        assert this_year.get_date_interval() == [
            datetime(year=1999, month=4, day=1),
            datetime(year=2000, month=4, day=1)
        ]