"""Exercise actual Streamlit screens and CSV edge cases without a paid API."""
from pathlib import Path
from unittest.mock import patch
import numpy as np
import pandas as pd
from streamlit.testing.v1 import AppTest

APP = Path(__file__).resolve().parents[1] / 'llm_streamlit' / 'app.py'

def test_all_pages_and_store_filter():
    app = AppTest.from_file(str(APP), default_timeout=60).run()
    assert not app.exception
    assert app.metric[1].value == '45'
    app.sidebar.selectbox[1].set_value('1').run()
    assert app.metric[1].value == '1'
    for page in ['Forecast', 'AI Advisor', 'Data & Method']:
        app.sidebar.radio[0].set_value(page).run()
        assert not app.exception, page
    app.sidebar.radio[0].set_value('Forecast').run()
    app.sidebar.slider[0].set_value(12).run()
    assert not app.exception
    assert len(app.dataframe[0].value) == 12
    assert (app.dataframe[0].value['Predicted_Sales'] >= 0).all()

def fixture_app(frame):
    with patch('pandas.read_csv', return_value=frame.copy()):
        app = AppTest.from_file(str(APP), default_timeout=60).run()
    assert not app.exception
    return app

def test_nonfinite_sales_are_removed():
    frame = pd.DataFrame({'Store':['1']*36, 'Date':pd.date_range('2024-01-05',periods=36,freq='7D'), 'Weekly_Sales':[100.0]*35+[np.inf]})
    app = fixture_app(frame)
    assert app.metric[2].value == '35'
    assert any('1 invalid' in x.value for x in app.warning)

def test_irregular_weeks_disable_forecasting():
    dates = pd.date_range('2024-01-05',periods=36,freq='7D').delete(10)
    app = fixture_app(pd.DataFrame({'Store':['1']*35,'Date':dates,'Weekly_Sales':[100]*35}))
    assert any('Forecast disabled' in x.value for x in app.warning)

def test_invalid_schema_and_empty_data_stop_cleanly():
    for frame in [pd.DataFrame({'Wrong':[1]}), pd.DataFrame({'Store':['1'],'Date':['bad'],'Weekly_Sales':[-1]})]:
        app = fixture_app(frame)
        assert app.error
