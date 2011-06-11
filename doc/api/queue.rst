.. currentmodule:: pyudev

:class:`Queue` – interfacing the udev event queue
=================================================

.. autoclass:: Queue

   .. automethod:: __init__

   .. attribute:: context

      The :class:`Context` to which this queue belongs

   .. autoattribute:: is_active

   .. autoattribute:: is_empty

   .. autoattribute:: current_kernel_sequence_number

   .. autoattribute:: current_udev_sequence_number

   .. autoattribute:: current_sequence_numbers

   .. automethod:: queued_events

   .. automethod:: failed_events
