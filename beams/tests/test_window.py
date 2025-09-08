from unittest.mock import MagicMock, patch

from pytestqt.qtbot import QtBot

from beams.widgets.window import MainWindow


def test_main_window(qtbot: QtBot):
    with patch('beams.service.rpc_client.RPCClient.from_config') as mock_from_config:
        mock_from_config.return_value = MagicMock()
        window = MainWindow()
        qtbot.add_widget(window)

        # basic introspection for now.  This may change in the future
        # opens with an edit tab open
        assert window.tab_widget.count() == 1
