# coding=utf-8
from PyQt5.QtWidgets import QWidget

from TriblerGUI.tribler_request_manager import TriblerRequestManager


class SubscriptionsWidget(QWidget):

    def initialize_with_channel(self, channel):
        self.channel_info = channel

        self.subscribe_button = self.findChild(QWidget, "subscribe_button")
        self.num_subs_label = self.findChild(QWidget, "num_subs_label")

        self.subscribe_button.clicked.connect(self.on_subscribe_button_click)
        self.update_subscribe_button()

    def update_subscribe_button(self):
        if self.channel_info["subscribed"]:
            self.subscribe_button.setText("✓ subscribed")
        else:
            self.subscribe_button.setText("subscribe")

        self.num_subs_label.setText(str(self.channel_info["votes"]))

    def on_subscribe_button_click(self):
        self.request_mgr = TriblerRequestManager()
        if self.channel_info["subscribed"]:
            self.request_mgr.perform_request("channels/subscribed/%s" % self.channel_info['dispersy_cid'], self.on_channel_unsubscribed, method='DELETE')
        else:
            self.request_mgr.perform_request("channels/subscribed/%s" % self.channel_info['dispersy_cid'], self.on_channel_subscribed, method='PUT')

    def on_channel_unsubscribed(self, json_result):
        if json_result["unsubscribed"]:
            self.channel_info["subscribed"] = False
            self.channel_info["votes"] -= 1
            self.update_subscribe_button()

    def on_channel_subscribed(self, json_result):
        if json_result["subscribed"]:
            self.channel_info["subscribed"] = True
            self.channel_info["votes"] += 1
            self.update_subscribe_button()
