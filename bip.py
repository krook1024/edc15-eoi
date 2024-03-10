import argparse
from mapfinder import get_bip_maps
from edcmap import Map


def get_args():
    parser = argparse.ArgumentParser(prog="bip calc")
    parser.add_argument(
        "-f", "--filename", action="store", help="specify the filename", required=True
    )
    parser.add_argument(
        "-c",
        "--codeblock",
        action="store",
        help="select codeblock (show available with -l)",
    )
    parser.add_argument(
        "-v",
        "--voltage",
        action="store",
        help="specify voltage (mV). for example 13998",
    )

    return parser.parse_args()


if __name__ == "__main__":
    args = get_args()
    bip1, bip2 = get_bip_maps(args.filename, args.codeblock)
    print("BIP baseline")
    print(bip1)
    print()

    print("BIP correction factor")
    print(bip2)
    print()

    print(
        f"BIP selected from baseline for {args.voltage}mV: {bip1.atX(args.voltage).tolist()}"
    )
    print(f"Expected BIP values calcualted for {args.voltage} mV")
    result = Map(x=bip2.x, y=bip2.y, lines=bip2.np() * bip1.atX(args.voltage).tolist())
    print(result)
