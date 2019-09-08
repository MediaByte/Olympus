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
import csv
import lmdb

class Save:
    def __init__(self, data, path):
        self.data = data
        self.path = path

    def record(self):
        with open(self.path, 'a') as writeFile:
            writer = csv.writer(writeFile)

            if len(self.data['data']) == 10:

                writer.writerow([self.data['time'], self.data['data'][0], self.data['data'][1], self.data['data'][2], self.data['data'][3],
                                 self.data['data'][4], self.data['data'][5], self.data['data'][6], self.data['data'][7], self.data['data'][8], self.data['data'][9]])
            else:
                writer.writerow([self.data['time'], self.data['data'][0], self.data['data'][1], self.data['data'][2], self.data['data'][3],
                                 self.data['data'][4], self.data['data'][5], self.data['data'][6], self.data['data'][7]])

                
    
def push_to_storage(data):
    db = lmdb.open('./data', map_size=99999999)

    with db.begin(write=True, buffers=True) as trx:

        trx.put(data['time'], data['data'])

    db.close()
