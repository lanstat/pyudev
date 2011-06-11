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


from __future__ import (print_function, division, unicode_literals,
                        absolute_import)

import sys
from operator import sub

import pytest

from pyudev import Queue

def pytest_funcarg__queue(request):
    context = request.getfuncargvalue('context')
    return Queue(context)

def pytest_funcarg__current_seqnum(request):
    queue = request.getfuncargvalue('queue')
    return queue.current_udev_sequence_number


class TestQueue(object):

    def test_current_sequence_numbers(self, queue):
        kernel_seqnum = queue.current_kernel_sequence_number
        udev_seqnum = queue.current_udev_sequence_number
        seqnums = queue.current_sequence_numbers
        assert kernel_seqnum > 0
        assert udev_seqnum > 0
        assert udev_seqnum == seqnums[0]
        assert kernel_seqnum == seqnums[1]
        # kernel can never generate more events than udev, because udev
        # consumes all kernel events, but may add more events (e.g. additional
        # symlinks or so).
        assert udev_seqnum >= kernel_seqnum

    def test_current_sequence_numbers_growth(self, queue):
        # make sure, dummy module isn't loaded
        pytest.unload_dummy()
        seqnums = queue.current_sequence_numbers
        pytest.load_dummy()
        next_seqnums = queue.current_sequence_numbers
        diff = tuple(map(sub, next_seqnums, seqnums))
        # loading the dummy network module generates four events:
        # - an event for the new module loaded
        # - an event for the new network device
        # - two events for the transmitted and received queues of the new
        #   device
        assert all(d == 4 for d in diff)
        # unload after test
        pytest.unload_dummy()

    @pytest.mark.xfail(reason='how to test?')
    def test_is_sequence_number_finished(self, queue, current_seqnum):
        raise NotImplementedError()

    def test_is_sequence_number_finished_range(self, queue, current_seqnum):
        previous_finished = queue.is_sequence_number_finished(
            current_seqnum-1, current_seqnum)
        next_finished = queue.is_sequence_number_finished(
            current_seqnum, current_seqnum+1)
        assert previous_finished
        assert not next_finished

    def test_is_sequence_number_finished_inverted_range(self, queue,
                                                        current_seqnum):
        small_finished = queue.is_sequence_number_finished(2, 1)
        huge_finished = queue.is_sequence_number_finished(200000, 100000)
        previous_finished = queue.is_sequence_number_finished(
            current_seqnum, current_seqnum-1)
        next_finished = queue.is_sequence_number_finished(
            current_seqnum+1, current_seqnum)
        assert small_finished
        assert huge_finished
        assert previous_finished
        assert next_finished

    def test_is_sequence_number_finished_overflow(self, queue):
        # fallback to a reasonable default  on python3
        maxint = getattr(sys, 'maxint', 2**63)
        with pytest.raises(OverflowError):
            queue.is_sequence_number_finished(1, maxint)
