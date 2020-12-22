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
        if host is None:
            host = "172.16.190.133"
        if port is None:
            port = 13377
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        self.socketf = self.socket.makefile()

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


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Replay captured USB packets')
    parser.add_argument('--host', type=str, default="192.168.0.247")
    parser.add_argument('--port', type=int, default=13377)
    parser.add_argument('command')
    parser.add_argument('args', nargs='*')
    args = parser.parse_args()

    bp = BPWAHK(host=args.host, port=args.port)
    # bp.version()

    if args.command == "version":
        print("Version %s" % bp.version())
    elif args.command == "nop":
        bp.nop()
    elif args.command == "read":
        bp.read()
    elif args.command == "show":
        bp.show()
    elif args.command == "save":
        bp.save(basename=args.args[0])
    elif args.command == "tx_file":
        hexdump(bp.tx_file(basename=args.args[0]))
    elif args.command == "read_bin":
        hexdump(bp.read_bin())
    else:
        print("Unknown command")


if __name__ == "__main__":
    main()
