from bpwahk import BPWAHK, hexdump


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Talk to BPWin AHK server')
    parser.add_argument('--host', type=str, default=None)
    parser.add_argument('--port', type=int, default=None)
    parser.add_argument('command')
    parser.add_argument('args', nargs='*')
    args = parser.parse_args()

    bp = BPWAHK(host=args.host, port=args.port)
    # bp.version()

    if args.command == "version":
        print("Version %s" % bp.version())
    elif args.command == "nop":
        bp.nop()
    elif args.command == "reload":
        bp.reload()
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
