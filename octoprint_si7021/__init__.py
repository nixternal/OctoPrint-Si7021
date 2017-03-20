# coding=utf-8

from __future__ import absolute_import
from octoprint.util import RepeatedTimer
from subprocess import Popen, PIPE, STDOUT
import octoprint.plugin
import re
import sys

__author__ = "Rich JOHNSON <nixternal@gmail.com>"
__license__ = 'The Unlicense http://unlicense.org/'
__copyright__ = "Copyright (C) 2017 Rich JOHNSON"
__github__ = 'https://www.github.com/nixternal/OctoPrint-Si7021'


class Si7021Plugin(octoprint.plugin.StartupPlugin,
                   octoprint.plugin.TemplatePlugin,
                   octoprint.plugin.AssetPlugin,
                   octoprint.plugin.SettingsPlugin):
    def __init__(self):
        self.isRaspi = False
        self.displaySi7021 = True
        self._checkTimer = None

    def on_after_startup(self):
        self.displaySi7021 = self._settings.get(['displaySi7021'])

        if sys.platform == 'linux2':
            with open('/proc/cpuinfo', 'r') as infile:
                cpuinfo = infile.read()
            match = re.search('^Hardware\s+:\s+(\w+)$',
                              cpuinfo,
                              flags=re.MULTILINE | re.IGNORECASE)
            if match.group(1) == 'BCM2708' or match.group(1) == 'BCM2709':
                self.isRaspi = True
            else:
                self.isRaspi = False

            if self.isRaspi and self.displaySi7021:
                self.startTimer(30.0)

        if not self.isRaspi:
            self._logger.info('This is not a Raspberry Pi - Plugin halted')
            sys.exit(1)

    def startTimer(self, interval):
        self._checkTimer = RepeatedTimer(
            interval,
            self.checkSi7021,
            None,
            None,
            True
        )
        self._checkTimer.start()

    def checkSi7021(self):
        data = Popen(
            ['/home/pi/myscripts/rhandtemp.py'],
            stdout=PIPE,
            stderr=STDOUT
        )
        h, c, f = data.communicate()[0].strip().split(' ')
        if h and c and f:
            self._plugin_manager.send_plugin_message(
                self._identifier,
                dict(israspi=self.isRaspi, rh=h, tc=c, tf=f)
            )
        else:
            self._logger.info('Si7021 detection failed !!')

    def get_settings_defaults(self):
        return dict(displaySi7021=self.displaySi7021)

    def on_settings_save(self, data):
        octoprint.plugin.SettingsPlugin.on_settings_save(self, data)

        self.displaySi7021 = self._settings_get(['displaySi7021'])

        if self.displaySi7021:
            interval = 30.0
            self.startTimer(interval)
        else:
            if self._checkTimer is not None:
                try:
                    self._checkTimer.cancel()
                except:
                    pass
            self._plugin_manager.send_plugin_message(self._identifier, dict())

    def get_template_configs(self):
        if self.isRaspi:
            return [
                dict(type='settings',
                     template='si7021_settings_raspi.jinja2')
            ]
        else:
            return []

    def get_assets(self):
        return {
            'js': ['js/si7021.js'],
            'css': ['css/roomtemp.css']
        }

    def get_update_information(self):
        return dict(
            si7021=dict(
                displayName='Si7021 Sensor Plugin',
                displayVersion=self._plugin_version,
                type='github_release',
                user='nixternal',
                repo='OctoPrint-Si7021',
                current=self._plugin_version,
                pip='%s/archive/{target_version}.zip' % __github__
            )
        )

__plugin_name__ = 'Si7021 Sensor Plugin'


def __plugin_load__():
    global __plugin_implementation__
    __plugin_implementation__ = Si7021Plugin()
    global __plugin_hooks__
    __plugin_hooks__ = {
        'octoprint.plugin.softwareupdate.check_config': __plugin_implementation__.get_update_information
    }
