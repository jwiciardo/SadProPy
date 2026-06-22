import argparse
from sadpropy.utility.input_reader import InputReader

def cmd_read(args):
    reader = InputReader(args.file)

    nodes = reader.read_sheet("Nodes")
    elements = reader.read_sheet("Elements")

    print("Nodes:", nodes)
    print("Elements:", elements)

def main():
    parser = argparse.ArgumentParser(prog="sadpropy")
    subparsers = parser.add_subparsers(dest="command")

    # ---------------- RUN ----------------
    run_parser = subparsers.add_parser("read")
    run_parser.add_argument("file")
    run_parser.set_defaults(func=cmd_read)

    args = parser.parse_args()
    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()