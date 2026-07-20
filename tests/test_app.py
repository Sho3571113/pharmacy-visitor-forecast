import importlib.util
import sys
from pathlib import Path
from types import ModuleType
from unittest.mock import MagicMock, patch


def load_app_module():
    streamlit = MagicMock()
    streamlit.session_state = {}
    streamlit.button.return_value = False

    authentication = ModuleType("authentication")
    authentication.authenticate_user = MagicMock()
    db_service = ModuleType("db_service")
    db_service.get_stores = MagicMock(return_value=[])
    db_service.get_visit_data = MagicMock()
    db_service.save_visit_data = MagicMock()
    forecast_service = ModuleType("forecast_service")
    forecast_service.forecast_from_db = MagicMock()
    staffing_service = ModuleType("staffing_service")
    staffing_service.get_staffing = MagicMock()
    staffing_service.save_staffing = MagicMock()

    plotly = ModuleType("plotly")
    plotly_express = MagicMock()
    matplotlib = ModuleType("matplotlib")
    matplotlib_pyplot = MagicMock()

    dependencies = {
        "streamlit": streamlit,
        "pandas": MagicMock(),
        "plotly": plotly,
        "plotly.express": plotly_express,
        "lightgbm": MagicMock(),
        "matplotlib": matplotlib,
        "matplotlib.pyplot": matplotlib_pyplot,
        "authentication": authentication,
        "db_service": db_service,
        "forecast_service": forecast_service,
        "staffing_service": staffing_service,
    }

    app_path = Path(__file__).parents[1] / "app.py"
    spec = importlib.util.spec_from_file_location("app_for_test", app_path)
    app = importlib.util.module_from_spec(spec)

    with patch.dict(sys.modules, dependencies):
        spec.loader.exec_module(app)

    return app


def test_get_staff_suggestion_rounds_up_per_25_visits():
    # Arrange（準備）
    app = load_app_module()

    # Act（実行）
    zero_visits = app.get_staff_suggestion(0)
    one_visit = app.get_staff_suggestion(1)
    twenty_five_visits = app.get_staff_suggestion(25)
    twenty_six_visits = app.get_staff_suggestion(26)

    # Assert（確認）
    assert zero_visits == 0
    assert one_visit == 1
    assert twenty_five_visits == 1
    assert twenty_six_visits == 2
