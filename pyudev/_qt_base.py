# -*- coding: utf-8 -*-
# Copyright (C) 2010, 2011 Sebastian Wiesner <lunaryorn@googlemail.com>

# This library is free software; you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as published by the
# Free Software Foundation; either version 2.1 of the License, or (at your
# option) any later version.

# This library is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License
# for more details.

# You should have received a copy of the GNU Lesser General Public License
# along with this library; if not, write to the Free Software Foundation,
# Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301 USA


"""
    pyudev._qt_base
    ===============

    Base mixin class for Qt4 support.

    .. moduleauthor::  Sebastian Wiesner  <lunaryorn@googlemail.com>
"""


from __future__ import (print_function, division, unicode_literals,
                        absolute_import)


class QUDevMonitorObserverMixin(object):

    def _setup_notifier(self, monitor, notifier_class):
        self.monitor = monitor
        self.notifier = notifier_class(
            monitor.fileno(), notifier_class.Read, self)
        self.notifier.activated[int].connect(self._process_udev_event)
        self._action_signal_map = {
            'add': self.deviceAdded, 'remove': self.deviceRemoved,
            'change': self.deviceChanged, 'move': self.deviceMoved,
        }

    def _process_udev_event(self):
        """
        Attempt to receive a single device event from the monitor, process
        the event and emit corresponding signals.

        Called by ``QSocketNotifier``, if data is
        available on the udev monitoring socket.
        """
        event = self.monitor.receive_device()
        if event:
            action, device = event
            self.deviceEvent.emit(action, device)
            self._action_signal_map[action].emit(device)
