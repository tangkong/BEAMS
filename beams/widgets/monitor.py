"""
Widget for viewing the status of a Behavior Tree, updated with information
from the BEAMS service
"""

import dataclasses
import logging
from datetime import datetime
from functools import partial
from typing import List, Optional

from qtpy import QtWidgets
from qtpy.QtGui import QColor
from qtpynodeeditor import FlowView, Node

from beams.service.remote_calls.behavior_tree_pb2 import (
    BehaviorTreeUpdateMessage, NodeId)
from beams.service.rpc_client import RPCClient
from beams.widgets.core import DesignerDisplay, insert_widget
from beams.widgets.heartbeat_info import HeartbeatInfo
from beams.widgets.node_models import create_editor_view
from beams.widgets.qt_models import (TICK_STATUS_COLOR_MAP,
                                     TREE_STATUS_COLOR_MAP, BehaviorTreeModel,
                                     QtBTreeItem, create_scene_nodes)

logger = logging.getLogger(__name__)


@dataclasses.dataclass
class TreeSnapshot:
    """
    Simple container holding the relevant information for a snapshot of a
    tree in time.
    """
    timestamp: datetime
    # holds configuration information and the tip node
    tree_update: BehaviorTreeUpdateMessage
    # holds node status and identification information for all nodes
    tree_item: QtBTreeItem


class MonitorPage(DesignerDisplay, QtWidgets.QWidget):
    """
    TODO:
    - generate nodes
    - color nodes based on status at each tick
    - determine how to collapse nodes?
    - disable delete/add widgets
    """
    filename = "monitor_page.ui"

    tree_view: QtWidgets.QTreeView

    # tree info
    hb_info_placeholder: QtWidgets.QWidget
    hb_info_widget: Optional[HeartbeatInfo] = None

    # editor view
    node_widget: QtWidgets.QWidget
    node_editor: FlowView
    auto_arrange_button: QtWidgets.QPushButton
    update_button: QtWidgets.QPushButton

    # history slider
    next_step_button: QtWidgets.QToolButton
    prev_step_button: QtWidgets.QToolButton
    num_counts_label: QtWidgets.QLabel
    tick_spin_box: QtWidgets.QSpinBox
    tick_count_label: QtWidgets.QLabel
    tick_slider: QtWidgets.QSlider

    client: RPCClient
    tree_id: NodeId

    tick_history: List[TreeSnapshot]

    def __init__(
        self,
        *args,
        tree_id: NodeId,
        client: Optional[RPCClient] = None,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        if client is None:
            self.client = RPCClient()
        else:
            self.client = client

        self.tree_id = tree_id
        self.hb_info_widget = None
        self.tick_history = []
        self._setup_editor_widget()
        self._setup_callbacks()

    def _setup_editor_widget(self) -> None:
        self.node_editor = create_editor_view()
        insert_widget(self.node_editor, self.node_widget)

    def _setup_callbacks(self) -> None:
        self.update_button.clicked.connect(self.grab_tick)
        self.next_step_button.clicked.connect(self.incrememt_tick)
        self.prev_step_button.clicked.connect(self.decrememt_tick)
        self.tick_slider.valueChanged.connect(
            partial(self.update_display_for_tick, zero_indexed=True)
        )
        self.tick_spin_box.valueChanged.connect(
            partial(self.update_display_for_tick, zero_indexed=False)
        )
        self.auto_arrange_button.clicked.connect(self.auto_arrange_nodes)

    def auto_arrange_nodes(self, *args, **kwargs) -> None:
        """Auto-arrange the nodes in the node editor using a pygraphviz layout"""
        try:
            self.node_editor.scene.auto_arrange(layout="pygraphviz", prog="dot")
        except ImportError:
            logger.debug("pygraphviz not available to run auto arrange routine")

    def grab_tick(self) -> None:
        """
        Grab and cache tick information.
        Update the tick label and range
        """
        heartbeat = self.client.get_heartbeat()
        update_msg = [msg for msg in heartbeat.behavior_tree_update
                      if msg.tree_id == self.tree_id][0]
        snapshot = TreeSnapshot(
            timestamp=heartbeat.reply_timestamp.ToDatetime(),
            tree_update=update_msg,
            tree_item=QtBTreeItem.from_tree_details(
                self.client.get_detailed_update(tree_uuid=self.tree_id.uuid)
            )
        )

        self.tick_history.append(snapshot)
        self.update_tick_widget_ranges()

    def update_tick_widget_ranges(self):
        # update ui elements
        self.num_counts_label.setText(f"/ {len(self.tick_history)}")
        self.tick_slider.setRange(0, len(self.tick_history) - 1)
        self.tick_spin_box.setMaximum(len(self.tick_history))
        self.tick_spin_box.setMinimum(1)

    def update_display_for_tick(self, tick_num: int, zero_indexed: bool = True) -> None:
        """
        tick_num here is indexed on the tick history list
        tick_slider: 0, len(tick_history)-1
        tick_spinbox: 1, len(tick_history)
        """
        if zero_indexed:
            spin_tick_num = tick_num + 1
        else:
            spin_tick_num = tick_num
            tick_num -= 1

        if not (0 <= tick_num < len(self.tick_history)):
            return

        self.tick_slider.blockSignals(True)
        self.tick_slider.setValue(tick_num)
        self.tick_slider.blockSignals(False)

        self.tick_spin_box.blockSignals(True)
        self.tick_spin_box.setValue(spin_tick_num)
        self.tick_spin_box.blockSignals(False)

        tick_snapshot = self.tick_history[tick_num]

        # update tree view and heartbeat widget
        self.tree_model = BehaviorTreeModel(
            tree=tick_snapshot.tree_item
        )
        self.tree_view.setModel(self.tree_model)
        self.tree_view.expandAll()

        if self.hb_info_widget is None:
            self.hb_info_widget = HeartbeatInfo(
                tree_update=tick_snapshot.tree_update,
                timestamp=tick_snapshot.timestamp,
            )
            insert_widget(self.hb_info_widget, self.hb_info_placeholder)
        else:
            self.hb_info_widget.update_from_msg(
                timestamp=tick_snapshot.timestamp,
                msg=tick_snapshot.tree_update
            )

        self.update_node_status(tick_num)

        if not self.node_editor.scene.nodes:
            self.construct_nodes()
            self.auto_arrange_nodes()

    def incrememt_tick(self):
        curr_tick = self.tick_slider.value()
        self.tick_slider.setValue(curr_tick + 1)

    def decrememt_tick(self):
        curr_tick = self.tick_slider.value()
        self.tick_slider.setValue(curr_tick - 1)

    def construct_nodes(self):
        """construct nodes based on loaded tree"""
        if len(self.tick_history) == 0:
            self.grab_tick()

        tree = self.tick_history[0]
        create_scene_nodes(self.node_editor.scene, tree.tree_item)

    def update_node_status(self, tick_idx: int):
        """
        Update node color to reflect statuses from tick index tick_idx.
        Color the node backgrounds using STATUS_COLOR_MAP.
        Node colors are adjusted using each node's style.
        Updates nodes in place based on uuid reported from server.
        """
        if not (0 <= tick_idx < len(self.tick_history)):
            return
        tree_item = self.tick_history[tick_idx].tree_item
        scene = self.node_editor.scene

        if not scene.nodes:
            return

        for item in tree_item.walk_tree():
            item_uuid = item.node_id
            if item_uuid is None:
                continue

            node: Node = scene.nodes[str(item_uuid)]

            status = item.status
            # gRPC enums are basically ints, can't isinstance check or use
            # two different enums as keys in one dict without collisions
            if item.parent is None:
                color_name = TREE_STATUS_COLOR_MAP.get(status, 'grey')
            else:
                color_name = TICK_STATUS_COLOR_MAP.get(status, 'grey')
            color_rgb = QColor(color_name).getRgb()
            # Set NodeStyle colors for visual feedback
            new_grad_colors = []
            # replace existing colors, keeping original gradient settings
            for i, (grad_extent, _) in enumerate(node.style.gradient_colors):
                rgb = tuple(max(val - 30 * i, 0) for val in color_rgb[:-1])
                new_grad_colors.append((grad_extent, QColor(*rgb)))

            node.style.gradient_colors = tuple(new_grad_colors)
            if node.graphics_object:
                node.graphics_object.update()
