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
from os import system, environ
from sys import stdout
import queue

# Custom module
from sample import Sample
from db import push_to_storage
from daq import DAQ



"""
Pre processed data from the analog to digital 
converter is handled here.
"""
def event_callback(args):
    scan_event_parameters = args.user_data
    sample = Sample('current', scan_event_parameters.buffer)
    
    # Add the data to the Queue
    event_q.put_nowait(sample)



"""
Olympus entry point
"""
def main():
    global event_q
    event_q = queue.Queue(maxsize=500)

    olympus_settings = { 
        "rate": environ.get('rate'), 
        "samples_per_channel": environ.get('samples_per_channel'), 
        "low_channel": environ.get('low_channel'), 
        "high_channel": environ.get('high_channel'), 
        "serial": environ.get('serial') 
    }

    daq = DAQ(olympus_settings, event_callback)

    try:
        
        daq.initialize()

        daq.begin_acquisition()

        # Event Loop
        try:
            while True:
                if event_q.qsize() > 0:

                    data_sample = event_q.get_nowait()

                    push_to_storage(data_sample.formatted_buffer())


        except KeyboardInterrupt:
            pass

    except Exception as e:
        print('\n', e)

    finally:
        # Stop the acquisition if it is still running.
        if daq.status.RUNNING:
            daq.ai_device.scan_stop()
        if daq.daq_device.is_connected():
            daq.daq_device.disconnect()
        daq.daq_device.release()




if __name__ == '__main__':
    main()

