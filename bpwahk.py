#!/usr/bin/env python3

import socket
import json
import binascii

class BPWAHK:
    def __init__(self, host="172.16.190.133", port=1337):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        self.socketf = self.socket.makefile()

    def tx(self, j):
        self.socket.sendall(json.dumps(j).encode("ascii") + b'\r\n')

    def rx(self):
        l = self.socketf.readline()
        return json.loads(l)

    def cmd(self, **kwargs):
        self.tx(kwargs)
        ret = self.rx()
        assert ret.get("error", 0) == 0
        return ret

    def about(self):
        reply = self.cmd(command="about")
        return reply["about"]

    def version(self):
        """
        V5.33.0 (7/16/2013)
        Algo DB Rev. 0
        Copyright © 2013, BPM Microsystems
        OK
        """
        about = self.about()
        return about.split("\n")[0].split()[0][1:]

    def reset(self):
        self.cmd(command="reset")

    def read(self):
        self.cmd(command="read")

    def show(self):
        self.cmd(command="show")

    def save(self, basename):
        self.cmd(command="save", basename=basename)

    def tx_file(self, fn):
        res = self.cmd(command="tx_file", file=fn)
        return binascii.unhexlify(res["hex"])

    def read_bin(self):
        self.read()
        fn = self.save(self, "tmp.bin")["file"]
        self.tx_file(fn)

# bp = BPWAHK(host="localhost")
bp = BPWAHK()
print("Version %s" % bp.version())
