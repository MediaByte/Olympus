FROM python:3

WORKDIR /usr/src/acquisition

COPY ./ ./

RUN apt-get update && apt-get install -y \ 
    gcc \
    g++ \
    make \
    python3-pip \
    libusb-1.0-0-dev
# lmdb-utils

RUN mkdir -p /srv/oxys/data
# RUN pip3 install lmdb
RUN pip3 install uldaq
RUN wget https://github.com/mccdaq/uldaq/releases/download/v1.1.1/libuldaq-1.1.1.tar.bz2 && tar -xvjf libuldaq-1.1.1.tar.bz2 && cd libuldaq-1.1.1 && ./configure && make && make install

ENV TERM xterm

CMD ["/bin/bash"]