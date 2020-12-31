#!/usr/bin/env python3

import socket
import json
import binascii
import sys


class BPError(Exception):
    pass


class NoChipInSocket(BPError):
    pass


class NotInsertedCorrectly(BPError):
    pass


class ChipInsertedBackwards(BPError):
    pass


def make_read_error(msg):
    if "There is no chip in the socket." in msg:
        return NoChipInSocket()
    elif "The chip is not inserted in the socket correctly." in msg:
        return NotInsertedCorrectly()
    elif "The chip is inserted backwards." in msg:
        return ChipInsertedBackwards()
    else:
        return BPError(msg)


def tobytes(buff):
    if type(buff) is str:
        #return bytearray(buff, 'ascii')
        return bytearray([ord(c) for c in buff])
    elif type(buff) is bytearray or type(buff) is bytes:
        return buff
    else:
        assert 0, type(buff)


def tostr(buff):
    if type(buff) is str:
        return buff
    elif type(buff) is bytearray or type(buff) is bytes:
        return ''.join([chr(b) for b in buff])
    else:
        assert 0, type(buff)


def hexdump(data, label=None, indent='', address_width=8, f=sys.stdout):
    def isprint(c):
        return c >= ' ' and c <= '~'

    if label:
        print(label)

    bytes_per_half_row = 8
    bytes_per_row = 16
    datab = tobytes(data)
    datas = tostr(data)
    data_len = len(data)

    def hexdump_half_row(start):
        left = max(data_len - start, 0)

        real_data = min(bytes_per_half_row, left)

        f.write(''.join('%02X ' % c for c in datab[start:start + real_data]))
        f.write(''.join('   ' * (bytes_per_half_row - real_data)))
        f.write(' ')

        return start + bytes_per_half_row

    pos = 0
    while pos < data_len:
        row_start = pos
        f.write(indent)
        if address_width:
            f.write(('%%0%dX  ' % address_width) % pos)
        pos = hexdump_half_row(pos)
        pos = hexdump_half_row(pos)
        f.write("|")
        # Char view
        left = data_len - row_start
        real_data = min(bytes_per_row, left)

        f.write(''.join([
            c if isprint(c) else '.'
            for c in str(datas[row_start:row_start + real_data])
        ]))
        f.write((" " * (bytes_per_row - real_data)) + "|\n")


class BPWAHK:
    def __init__(self, host=None, port=None):
        self.host = host
        self.port = port
        if self.host is None:
            self.host = "192.168.0.247"
        if self.port is None:
            self.port = 13377
        self.open()

    def __del__(self):
        self.close()

    def open(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.socket.connect((self.host, self.port))
        except:
            print("Failed to connect to %s:%s" % (self.host, self.port))
            raise
        self.socketf = self.socket.makefile()

    def relaunch(self):
        self.close()
        self.open()

    def close(self):
        if self.socket:
            # Workaround for connection issue
            self.reload()
            # Maybe this is all that is needed
            # nope, keep reload
            self.socket.close()
        self.socket = None
        self.socketf = None

    def tx(self, j):
        self.socket.sendall(json.dumps(j).encode("ascii") + b'\n')

    def rx(self):
        l = self.socketf.readline()
        try:
            return json.loads(l)
        except:
            print("ERROR", l)
            raise

    def cmd(self, **kwargs):
        self.tx(kwargs)
        ret = self.rx()
        # assert ret.get("error", 0) == 0
        return ret

    def about(self):
        reply = self.cmd(command="about")
        return reply["about"]

    def nop(self):
        self.cmd(command="nop")

    def reload(self):
        self.cmd(command="reload")

    def version(self):
        """
        V5.33.0 (7/16/2013)
        Algo DB Rev. 0
        Copyright C 2013, BPM Microsystems
        OK
        """
        about = self.about()
        return about.split("\n")[0].split()[0][1:]

    def reset(self):
        self.cmd(command="reset")

    def read(self):
        res = self.cmd(command="read")
        if res.get("error", 0):
            raise make_read_error(res["message"])

    def show(self):
        self.cmd(command="show", ms=2000)

    def save(self, basename):
        self.cmd(command="save", basename=basename)

    def tx_file(self, basename):
        res = self.cmd(command="tx_file", basename=basename)
        return binascii.unhexlify(res["hex"])

    def read_bin(self):
        self.read()
        basename = "tmp.bin"
        self.save(basename=basename)
        return self.tx_file(basename=basename)
