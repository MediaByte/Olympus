#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
  Copyright © 2019 OXYS
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
# Python class for MCC DAQ hardware
from uldaq import get_daq_device_inventory, DaqDevice, AInScanFlag, DaqEventType, WaitType, ScanOption
from uldaq import ScanStatus, InterfaceType, AiInputMode, create_float_buffer, ULException, EventCallbackArgs, Range

# Python standard library modules
from collections import namedtuple
from os import system
from sys import stdout
import queue

# LMDB database
import lmdb

# Custom module
from sample import Sample

"""
Olympus entry point
"""
def main():
    global q
    daq_device = None
    ai_daq_device = None
    low_channel = 0
    high_channel = 9
    samples_per_channel = 1
    rate = 500
    input_mode = AiInputMode.SINGLE_ENDED
    event_types = DaqEventType.ON_DATA_AVAILABLE
    flags = AInScanFlag.DEFAULT
    scan_option = ScanOption.CONTINUOUS
    event_types = DaqEventType.ON_DATA_AVAILABLE | DaqEventType.ON_END_OF_INPUT_SCAN | DaqEventType.ON_INPUT_SCAN_ERROR
    channel_count = high_channel - low_channel + 1
    q = queue.Queue(maxsize=3)
    ScanParams = namedtuple('ScanParams', 'buffer high_chan low_chan')

    try:
        # Test if hardware device is connected to USB
        devices = get_daq_device_inventory(InterfaceType.USB)
        number_of_devices = len(devices)

        if number_of_devices == 0:
            raise Exception('Error: No DAQ devices found')

        print('\nOlympus found', number_of_devices, 'DAQ device(s). Attempting to pair...')

        # Instantiate the DAQ class
        daq_device = DaqDevice(devices[0])
        ai_daq_device = daq_device.get_ai_device()
        if ai_daq_device is None:
            raise Exception('\nError: The DAQ device does not support analog input')

        # Verify that the specified device supports hardware pacing for analog input
        ai_info = ai_daq_device.get_info()
        if not ai_info.has_pacer():
            raise Exception('\nError: The specified DAQ device does not support hardware paced analog input')

        # Establish connection to the hardware
        descriptor = daq_device.get_descriptor()
        print('\nConnecting to ', descriptor.dev_string, '- Paired')
        daq_device.connect()

        print('\nPaired with your device(s)', 'Running...')

        # Allocate a buffer
        daq_data = create_float_buffer(channel_count, samples_per_channel)

        # Store the scan event parameters for use in the callback function.
        scan_event_parameters_daq = ScanParams(daq_data, high_channel, low_channel)

        # Start the event driven acquisition.
        daq_device.enable_event(event_types, channel_count * samples_per_channel, event_callback, scan_event_parameters_daq)
        ai_daq_device.a_in_scan(low_channel, high_channel, input_mode, Range.BIP1VOLTS, samples_per_channel, rate, scan_option, flags, daq_data)

        # Event Loop
        try:
            while True:
                if q.qsize() > 0:

                    data_sample = q.get_nowait()

                    print(data_sample.buffer)


        except KeyboardInterrupt:
            pass

    except Exception as e:
        print('\n', e)

    finally:
        # Stop the acquisition if it is still running.
        if ScanStatus.RUNNING:
            ai_daq_device.scan_stop()
        if daq_device.is_connected():
            daq_device.disconnect()
        daq_device.release()


"""
Pre processed data from the analog to digital 
converter is handled here.
"""
def event_callback(args):
    scan_event_parameters = args.user_data

    sample = Sample('current', scan_event_parameters.buffer)
    
    # Add the data to the Queue
    q.put_nowait(sample)






if __name__ == '__main__':
    main()

