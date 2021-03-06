"""
  Copyright © 2019
 All rights reserved.
 Redistribution and use in source and binary forms, with or without
 modification, are permitted provided that the following conditions are met:
   a. Redistributions of source code must retain the above copyright notice,
      this list of conditions and the following disclaimer.
   b. Redistributions in binary form must reproduce the above copyright
      notice, this list of conditions and the following disclaimer in the
      documentation and/or other materials provided with the distribution.
   c. Neither the name of Continuum nor the names of its contributors
      may be used to endorse or promote products derived from this software
      without specific prior written permission.
 THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
 AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
 IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
 ARE DISCLAIMED. IN NO EVENT SHALL THE REGENTS OR CONTRIBUTORS BE LIABLE FOR
 ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
 DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
 SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
 CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
 LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
 OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH
 DAMAGE.

 Created by Mario Martin 2019
"""

from os import environ
from collections import namedtuple
from uldaq import get_daq_device_inventory, DaqDevice, AInScanFlag, DaqEventType, WaitType, ScanOption
from uldaq import ScanStatus, InterfaceType, AiInputMode, create_float_buffer, ULException, EventCallbackArgs, Range


class DAQ:
    def __init__(self, options, cb):
        self.serial = options['serial']
        self.rate = int(options['rate'])
        self.samples_per_channel = int(options['samples_per_channel'])
        self.low_channel = int(options['low_channel'])
        self.high_channel = int(options['high_channel'])
        self.channel_count = int(self.high_channel) - int(self.low_channel) + 1
        self.flags = AInScanFlag.DEFAULT
        self.scan_option = ScanOption.CONTINUOUS
        self.event_types = DaqEventType.ON_DATA_AVAILABLE | DaqEventType.ON_END_OF_INPUT_SCAN | DaqEventType.ON_INPUT_SCAN_ERROR
        self.ScanParams = namedtuple('ScanParams', 'buffer high_chan low_chan')
        self.event_callback = cb
        self.status = ScanStatus
        self.daq_device = None
        self.ai_device = None
        self.data = None
        self.input_mode = None
        self.scan_event_parameters_daq = None
        self.range = options['range']

    def configure_mode(self, mode):
        if mode == "DIFFERENTIAL":
            self.input_mode = AiInputMode.DIFFERENTIAL
        elif mode == "SINGLE_ENDED":
            self.input_mode = AiInputMode.SINGLE_ENDED

        if self.range == '1':
            self.range = Range.BIP1VOLTS
        elif self.range == '2':
            self.range = Range.BIP2VOLTS
        elif self.range == '4':
            self.range = Range.BIP4VOLTS
        elif self.range == '5':
            self.range = Range.BIP5VOLTS
        elif self.range == '10':
            self.range = Range.BIP10VOLTS
        elif self.range == '20':
            self.range = Range.BIP20VOLTS
        elif self.range == '15':
            self.range = Range.BIP15VOLTS
        elif self.range == '30':
            self.range = Range.BIP30VOLTS
        elif self.range == '60':
            self.range = Range.BIP60VOLTS

    def initialize(self):
        connected_devices = get_daq_device_inventory(InterfaceType.USB)
        number_of_devices = len(connected_devices)

        if number_of_devices == 0:
            raise Exception(
                'OLYMPUS: RUNTIME ERROR - DAQ DEVICE NOT CONNECTED')

        for daqs in connected_devices:
            if daqs.unique_id == self.serial:
                self.daq_device = DaqDevice(daqs)
                self.ai_device = self.daq_device.get_ai_device()
                self.daq_device.connect()

        self.daq_data = create_float_buffer(
            self.channel_count, self.samples_per_channel)
        self.scan_event_parameters_daq = self.ScanParams(
            self.daq_data, self.high_channel, self.low_channel)

        return True

    def begin_acquisition(self):
        self.daq_device.enable_event(
            self.event_types,
            self.channel_count * self.samples_per_channel,
            self.event_callback,
            self.scan_event_parameters_daq
        )

        self.ai_device.a_in_scan(
            self.low_channel,
            self.high_channel,
            self.input_mode,
            self.range,
            self.samples_per_channel,
            self.rate,
            self.scan_option,
            self.flags,
            self.daq_data
        )
