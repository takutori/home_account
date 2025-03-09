
import pytest
from datetime import datetime

from app.services.accounting_time import AccountingTime, AccountingMonth, AccountingYear



class TestAccountingTime:

    AccountingTime.__abstractmethods__ = set() # これがないと何故かオーバーライドしろというエラーが出る。

    def test_init(self):
        Accounting_time = AccountingTime(now_date=None)
        assert type(Accounting_time.now_date) == datetime

        Accounting_time = AccountingTime(now_date="2021-01-01")
        assert Accounting_time.now_date == datetime(year=2021, month=1, day=1)

class TestAccountingMonth:
    def test_get_date_interval(self):
        Accounting_month = AccountingMonth(now_date="2000-01-01")
        assert Accounting_month.get_date_interval() == [
            datetime(year=1999, month=12, day=25),
            datetime(year=2000, month=1, day=25)
        ]

        Accounting_month = AccountingMonth(now_date="2000-01-24")
        assert Accounting_month.get_date_interval() == [
            datetime(year=1999, month=12, day=25),
            datetime(year=2000, month=1, day=25)
        ]

        Accounting_month = AccountingMonth(now_date="2000-01-25")
        assert Accounting_month.get_date_interval() == [
            datetime(year=2000, month=1, day=25),
            datetime(year=2000, month=2, day=25)
        ]

        Accounting_month = AccountingMonth(now_date="2000-01-26")
        assert Accounting_month.get_date_interval() == [
            datetime(year=2000, month=1, day=25),
            datetime(year=2000, month=2, day=25)
        ]

        Accounting_month = AccountingMonth(now_date="1999-12-26")
        assert Accounting_month.get_date_interval() == [
            datetime(year=1999, month=12, day=25),
            datetime(year=2000, month=1, day=25)
        ]

        Accounting_month = AccountingMonth(now_date="1999-12-24")
        assert Accounting_month.get_date_interval() == [
            datetime(year=1999, month=11, day=25),
            datetime(year=1999, month=12, day=25)
        ]

    def test_get_days_left(self):
        Accounting_month = AccountingMonth(now_date="2000-01-24")
        assert Accounting_month.get_days_left() == 1

        Accounting_month = AccountingMonth(now_date="1999-12-25")
        assert Accounting_month.get_days_left() == 31

    def test_get_last_day(self):
        Accounting_month = AccountingMonth(now_date="2000-01-24")
        last_day = Accounting_month.get_last_day()
        assert last_day.year == 2000
        assert last_day.month == 1
        assert last_day.day == 31

        Accounting_month = AccountingMonth(now_date="2001-02-24")
        last_day = Accounting_month.get_last_day()
        assert last_day.year == 2001
        assert last_day.month == 2
        assert last_day.day == 28


class TestAccountingYear:
    def test_get_date_interval(self):
        Accounting_year = AccountingYear(now_date="2000-01-01", start_month=1)
        assert Accounting_year.get_date_interval() == [
            datetime(year=2000, month=1, day=1),
            datetime(year=2001, month=1, day=1)
        ]

        with pytest.raises(ValueError) as e:
            Accounting_year = AccountingYear(now_date="2000-01-01", start_month=3)
            assert "3月スタートの会計期間は現状設定できません。" in e.info

        Accounting_year = AccountingYear(now_date="2000-05-01", start_month=4)
        assert Accounting_year.get_date_interval() == [
            datetime(year=2000, month=4, day=1),
            datetime(year=2001, month=4, day=1)
        ]

        Accounting_year = AccountingYear(now_date="2000-03-01", start_month=4)
        assert Accounting_year.get_date_interval() == [
            datetime(year=1999, month=4, day=1),
            datetime(year=2000, month=4, day=1)
        ]