import time

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


class Sample:
    def __init__(self, name, data):
        self.type_of = name
        self.timestamp = time.time()
        self.buffer = data
        self.length = len(self.buffer)
        self.range_of_data = range(len(self.buffer))

    def raw(self):
        self.formatted_buffer()
        return self.data

    def formatted_buffer(self):
        the_fifo = self.range_of_data
        formatted_samples = list()
        formatted_channels = list()
        for each_sample in the_fifo:
            formatted_channels.append(self.buffer[each_sample])

            if len(self.buffer) == 10:
                formatted_samples += formatted_channels
                formatted_channels = list()

            if len(self.buffer) == 8:
                formatted_samples += formatted_channels
                formatted_channels = list()

        self.data = formatted_samples

        return {'time': self.timestamp, 'data': formatted_samples}

        # return { 'time': str(self.timestamp).encode(), 'data': str(formatted_samples).encode() }
