#!/usr/bin/env python3

from bpwahk import BPWAHK, hexdump


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description='Read remotely and store / display')
    parser.add_argument('--host', type=str, default="192.168.0.247")
    parser.add_argument('--port', type=int, default=13377)
    parser.add_argument('fn_out', nargs='?')
    args = parser.parse_args()

    bp = BPWAHK(host=args.host, port=args.port)
    buf = bp.read_bin()
    if args.fn_out:
        open(args.fn_out, "wb").write(buf)
    else:
        hexdump(buf)


if __name__ == "__main__":
    main()
