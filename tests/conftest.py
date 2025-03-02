import pandas as pd

import pytest
from unittest.mock import Mock
import gspread
from app import boot_app

@pytest.fixture
def app():
    app = boot_app()
    yield app

@pytest.fixture
def client(app):
    return app.test_client()

def shift_column_to_first_row(data: pd.DataFrame) -> pd.DataFrame:
    """
    列名を一行目にずらし、列名を0, 1, 2, ...という番号に変更する。

    Parameters
    ----------
    data : pd.DataFrame
        変更前のデータ

    Returns
    -------
    pd.DataFrame
        変更後のデータ
    """
    insert_value = data.columns.tolist()
    insert_dict = {x: [x] for x in insert_value}
    insert_df = pd.DataFrame(insert_dict)

    new_data = pd.concat([insert_df, data], axis=0)
    new_data.columns = range(len(new_data.columns))

    return new_data

@pytest.fixture(scope="function")
def mock_sheet(request):
    sheet_name = request.param
    sheet = Mock(spec=gspread.worksheet.Worksheet)
    data = pd.read_excel("tests/data/test_household_account.xlsx", sheet_name=sheet_name)
    # テスト用のデータは列が列としてDataFrame上で読み込まれるが、spreadsheetの方は列名が0, 1, ...となる。
    # spreadsheetに合わせるために、わざと列名を0, 1, 2...として、元の列名を一行目に挿入する。
    data = shift_column_to_first_row(data)

    sheet._properties = {"title": sheet_name}
    sheet.get_all_values.return_value = data

    return sheet

@pytest.fixture
def income_data():
    excel_name = "test_household_account.xlsx"
    income_data = pd.read_excel("tests/data/" + excel_name, sheet_name="収入データ")
    income_data["time"] = pd.to_datetime(income_data["time"], format="%Y-%m-%d")

    return income_data


