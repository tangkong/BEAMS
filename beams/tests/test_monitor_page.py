import uuid
from unittest.mock import MagicMock, PropertyMock, patch

import pytest
from google.protobuf.timestamp_pb2 import Timestamp
from pytestqt.qtbot import QtBot
from qtpy.QtCore import Qt

from beams.service.remote_calls.behavior_tree_pb2 import (
    BehaviorTreeUpdateMessage, TreeDetails,
    NodeId, TickStatus, TreeStatus)
from beams.service.remote_calls.heartbeat_pb2 import HeartBeatReply
from beams.widgets.monitor import MonitorPage

# Some constants for our tests
TREE_ID_UUID = str(uuid.uuid4())
TREE_ID_NAME = "test_tree"
ROOT_NODE_UUID = str(uuid.uuid4())
ROOT_NODE_NAME = "root_node"
CHILD_NODE_UUID = str(uuid.uuid4())
CHILD_NODE_NAME = "child_node"


@pytest.fixture
def tree_id():
    """Fixture for a sample NodeId."""
    return NodeId(uuid=TREE_ID_UUID, name=TREE_ID_NAME)


@pytest.fixture
def mock_rpc_client(tree_id):
    """Fixture to create a mock RPCClient."""
    client = MagicMock()

    # Mock get_heartbeat response
    heartbeat = HeartBeatReply()
    timestamp = Timestamp()
    timestamp.GetCurrentTime()
    heartbeat.reply_timestamp.CopyFrom(timestamp)
    tree_update = heartbeat.behavior_tree_update.add()
    tree_update.tree_id.CopyFrom(tree_id)
    tree_update.tree_status = TreeStatus.IDLE
    tree_update.tick_status = TickStatus.SUCCESS
    tree_update.node_id.name = ROOT_NODE_NAME
    tree_update.node_id.uuid = ROOT_NODE_UUID
    client.get_heartbeat.return_value = heartbeat

    # Mock get_detailed_update response
    def get_new_details(*args, **kwargs):
        tree_details = TreeDetails()
        tree_details.tree_id.CopyFrom(tree_id)
        tree_details.tree_status = TreeStatus.IDLE
        root_node = tree_details.node_info
        root_node.id.uuid = ROOT_NODE_UUID
        root_node.id.name = ROOT_NODE_NAME
        root_node.status = TickStatus.SUCCESS
        root_node.type = "Sequence"
        child_node = root_node.children.add()
        child_node.id.uuid = CHILD_NODE_UUID
        child_node.id.name = CHILD_NODE_NAME
        child_node.status = TickStatus.SUCCESS
        child_node.type = "SetPVAction"
        return tree_details

    client.get_detailed_update.side_effect = get_new_details

    return client


@pytest.fixture
def monitor_page(qtbot: QtBot, tree_id, mock_rpc_client):
    """Fixture to create a MonitorPage widget."""
    widget = MonitorPage(tree_id=tree_id, client=mock_rpc_client)
    qtbot.add_widget(widget)
    return widget


def test_monitor_page_creation(monitor_page: MonitorPage):
    """Test that the MonitorPage widget can be created."""
    assert monitor_page is not None
    assert monitor_page.tree_id.uuid == TREE_ID_UUID
    assert monitor_page.tick_history == []


@patch('beams.widgets.monitor.MonitorPage.update_node_status')
def test_grab_tick(mock_update, monitor_page: MonitorPage, mock_rpc_client: MagicMock):
    """Test that grab_tick fetches data and updates the history."""
    assert len(monitor_page.tick_history) == 0

    monitor_page.grab_tick()

    assert len(monitor_page.tick_history) == 1
    mock_rpc_client.get_heartbeat.assert_called_once()
    mock_rpc_client.get_detailed_update.assert_called_once()

    # Check that the snapshot was created correctly
    snapshot = monitor_page.tick_history[0]
    assert snapshot.tree_update.tree_id.uuid == TREE_ID_UUID
    assert snapshot.tree_item.name == TREE_ID_NAME

    # Check that the UI is updated
    assert monitor_page.num_counts_label.text() == "/ 1"
    assert monitor_page.tick_slider.minimum() == 0
    assert monitor_page.tick_slider.maximum() == 0
    assert monitor_page.tick_spin_box.minimum() == 1
    assert monitor_page.tick_spin_box.maximum() == 1


@patch('beams.widgets.monitor.MonitorPage.update_node_status')
def test_next_prev_buttons(mock_update, monitor_page: MonitorPage, qtbot: QtBot):
    """Test the next and previous tick buttons."""
    # Add two ticks to the history
    monitor_page.grab_tick()
    monitor_page.grab_tick()

    # Should start at the first tick (index 0)
    monitor_page.update_display_for_tick(0)
    assert monitor_page.tick_slider.value() == 0

    # Click next
    qtbot.mouseClick(monitor_page.next_step_button, Qt.LeftButton)
    assert monitor_page.tick_slider.value() == 1

    # Click next again (should do nothing)
    qtbot.mouseClick(monitor_page.next_step_button, Qt.LeftButton)
    assert monitor_page.tick_slider.value() == 1

    # Click previous
    qtbot.mouseClick(monitor_page.prev_step_button, Qt.LeftButton)
    assert monitor_page.tick_slider.value() == 0

    # Click previous again (should do nothing)
    qtbot.mouseClick(monitor_page.prev_step_button, Qt.LeftButton)
    assert monitor_page.tick_slider.value() == 0


@patch('beams.widgets.monitor.MonitorPage.update_node_status')
def test_slider_interaction(mock_update, monitor_page: MonitorPage, qtbot: QtBot):
    """Test that moving the slider updates the display."""
    # Add three ticks to the history
    monitor_page.grab_tick()
    monitor_page.grab_tick()
    monitor_page.grab_tick()

    # Move slider to the middle position
    monitor_page.tick_slider.setValue(1)
    # The spin box is 1-indexed
    assert monitor_page.tick_spin_box.value() == 2


@patch('beams.widgets.monitor.MonitorPage.update_node_status')
def test_spin_box_interaction(mock_update, monitor_page: MonitorPage, qtbot: QtBot):
    """Test that changing the spin box updates the display."""
    # Add three ticks to the history
    monitor_page.grab_tick()
    monitor_page.grab_tick()
    monitor_page.grab_tick()

    # Set spin box to the second tick
    monitor_page.tick_spin_box.setValue(2)
    # The slider is 0-indexed
    assert monitor_page.tick_slider.value() == 1


def test_auto_arrange_button(monitor_page: MonitorPage, qtbot: QtBot):
    """Test that the auto-arrange button calls the scene's auto-arrange."""
    with patch.object(monitor_page.node_editor.scene, 'auto_arrange') as mock_auto_arrange:
        qtbot.mouseClick(monitor_page.auto_arrange_button, Qt.LeftButton)
        mock_auto_arrange.assert_called_once()


def test_buttons_with_no_history(monitor_page: MonitorPage, qtbot: QtBot):
    """Test that the next/prev buttons do nothing with no history."""
    assert monitor_page.tick_history == []
    # Slider is at 0, let's confirm it doesn't move
    assert monitor_page.tick_slider.value() == 0

    qtbot.mouseClick(monitor_page.next_step_button, Qt.LeftButton)
    assert monitor_page.tick_slider.value() == 0

    qtbot.mouseClick(monitor_page.prev_step_button, Qt.LeftButton)
    assert monitor_page.tick_slider.value() == 0


def test_auto_arrange_no_pygraphviz(monitor_page: MonitorPage, qtbot: QtBot, caplog):
    """Test that auto-arrange handles a missing pygraphviz gracefully."""
    with patch('importlib.import_module', side_effect=ImportError("No module named 'pygraphviz'")):
        with caplog.at_level('DEBUG'):
            monitor_page.auto_arrange_nodes()
            assert "pygraphviz not available" in caplog.text
