#!/usr/bin/env python
from bpwahk import BPWAHK, hexdump
from bpwahk import default_date_dir, mkdir_p
import os
import json
import binascii
import hashlib
import subprocess


def buff2hash8(buff):
    return binascii.hexlify(hashlib.md5(buff).digest())[0:8]


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Replay captured USB packets')
    parser.add_argument('--shell', type=str, default=None, help="Run custom command after each run")
    parser.add_argument('--host', type=str, default=None, help="AHK server host")
    parser.add_argument('--port', type=int, default=None, help="AHK server port")
    parser.add_argument('--postfix', help="Log dir postfix")
    parser.add_argument('--out-dir')
    args = parser.parse_args()

    bp = BPWAHK(host=args.host, port=args.port)

    outdir = args.out_dir
    if not outdir:
        outdir = default_date_dir("out", "", args.postfix)
    if not os.path.exists(outdir):
        mkdir_p(outdir)

    itern = 0
    while True:
        itern += 1
        prefix = os.path.join(outdir, "%03u" % itern)
        print("")
        print("")
        print("")
        try:
            buf = bp.read_bin()
            print("")
            hexdump(buf, indent='  ', label='Code')
            hexdump(buf[0:0x40], indent='  ', label='Code start')
            print((buff2hash8(buf)))
            if outdir:
                out_fn = prefix + "_code.bin"
                open(out_fn, "wb").write(buf)
                if args.shell:
                    subprocess.check_call(args.shell + " " + out_fn, shell=True)
        except Exception as e:
            print("ERROR")
            print(e)
        print(itern)

if __name__ == "__main__":
    main()
