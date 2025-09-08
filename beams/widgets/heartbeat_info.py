import datetime

from qtpy.QtWidgets import QComboBox, QDateTimeEdit, QLabel, QSpinBox, QWidget

from beams.service.remote_calls.behavior_tree_pb2 import (
    BehaviorTreeUpdateMessage, TickStatus, TreeStatus)
from beams.widgets.core import DesignerDisplay


class HeartbeatInfo(DesignerDisplay, QWidget):
    filename = "heartbeat_info.ui"

    datetime_edit: QDateTimeEdit

    name_disp_label: QLabel
    uuid_disp_label: QLabel
    tree_status_disp_label: QLabel
    mode_combo_box: QComboBox
    delay_spin_box: QSpinBox

    tip_name_disp_label: QLabel
    tip_status_disp_label: QLabel

    def __init__(
        self,
        *args,
        tree_update: BehaviorTreeUpdateMessage,
        timestamp: datetime.datetime,
        read_only: bool = True,
        **kwargs
    ):
        super().__init__(*args, **kwargs)

        self.timestamp = timestamp
        self.update_msg = tree_update
        self.read_only = read_only
        self.update_from_msg(timestamp, self.update_msg)

    def update_from_msg(
        self,
        timestamp: datetime.datetime,
        msg: BehaviorTreeUpdateMessage
    ):
        self.mode_combo_box.setEnabled(not self.read_only)
        self.delay_spin_box.setEnabled(not self.read_only)

        self.datetime_edit.setDateTime(timestamp)

        self.name_disp_label.setText(msg.tree_id.name)
        self.uuid_disp_label.setText(msg.tree_id.uuid)
        self.tree_status_disp_label.setText(TreeStatus.Name(msg.tree_status))

        self.mode_combo_box.setCurrentIndex(msg.tick_config)
        self.delay_spin_box.setValue(msg.tick_delay_ms)

        self.tip_name_disp_label.setText(msg.node_id.name)
        self.tip_status_disp_label.setText(TickStatus.Name(msg.tick_status))
