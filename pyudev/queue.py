# -*- coding: utf-8 -*-
# Copyright (C) 2011 Sebastian Wiesner <lunaryorn@googlemail.com>

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
    pyudev.queue
    ============

    Queue interface of :mod:`pyudev`

    .. moduleauthor::  Sebastian Wiesner  <lunaryorn@googlemail.com>
"""


from __future__ import (print_function, division, unicode_literals,
                        absolute_import)

from pyudev._util import udev_list_iterate
from pyudev._libudev import libudev
from pyudev.device import Device


__all__ = ['Queue']


class Queue(object):
    """
    Interface to the udev event queue.
    """

    def __init__(self, context):
        """
        Create a new queue interface for the given ``context`` (a
        :class:`pyudev.Context`).
        """
        self.context = context
        self._as_parameter_ = libudev.udev_queue_new(context)

    @property
    def is_active(self):
        """
        ``True``, if udev is active (listening for events), ``False``
        otherwise.

        .. note::

           If this property is ``True``, it simply means, that udev is
           listening for incoming events and handles them.  It does *not* mean,
           that udev is currently processing an event (see :attr:`is_empty`).
        """
        return bool(libudev.udev_queue_get_udev_is_active(self))

    @property
    def is_empty(self):
        """
        ``True``, if the udev event queue is currently empty, ``False``
        otherwise.

        If this property is ``False``, udev currently processes an event.
        Consequently, this propert is likely ``False``, when this class is used
        inside a udev rule script.
        """
        return bool(libudev.udev_queue_get_queue_is_empty(self))

    def is_sequence_number_finished(self, start, end=None):
        if end is None:
            return bool(libudev.udev_queue_get_seqnum_is_finished(self, start))
        else:
            return bool(libudev.udev_queue_get_seqnum_sequence_is_finished(
                self, start, end))

    @property
    def current_kernel_sequence_number(self):
        """
        The current event sequence number of the kernel as integer.

        This is the sequence number as seen by the kernel itself, *not* by the
        udev daemon.
        """
        return libudev.udev_queue_get_kernel_seqnum(self)

    @property
    def current_udev_sequence_number(self):
        """
        The current event sequence number of the udev daemon as integer.
        """
        return libudev.udev_queue_get_udev_seqnum(self)

    @property
    def current_sequence_numbers(self):
        """
        The current event sequence numbers from the udev daemon and the kernel
        as pair ``(udev, kernel)``.  Both components are integers.
        """
        return (self.current_udev_sequence_number,
                self.current_kernel_sequence_number)

    def queued_events(self):
        """
        Iterate over all currently queued events.

        Yield ``(device, sequence_number)`` pairs. ``device`` is a
        :class:`Device` object representing the device, from which the event
        originated.  ``sequence_number`` is the sequence number of the event as
        integer.
        """
        queued = libudev.udev_queue_get_queued_list_entry(self)
        for syspath, seqnum_s in udev_list_iterate(queued):
            yield (Device.from_path(self.context, syspath), int(seqnum_s))

    def failed_events(self):
        """
        Iterate over all failed events.

        Yield :class:`Device` objects representing the devices, for which
        events failed.
        """
        failed = libudev.udev_queue_get_failed_list_entry(self)
        for syspath, _ in udev_list_iterate(failed):
            yield Device.from_path(self.context, syspath)
