######################################################################
#                            v4parser                                #
######################################################################

import argparse

def int_to_ip(ip_int: int) -> str:
    """
    Transforms an integer IP address into a string representation.
    """
    return (f"{(ip_int >> 24) & 0xff}.{(ip_int >> 16) & 0xff}."
            f"{(ip_int >> 8) & 0xff}.{ip_int & 0xff}")

def ip_to_int(ip_str: str) -> int:
    """
    Transforms the string IP address into its decimal value.
    """
    o = [int(x) for x in ip_str.split('.')]
    return (o[0] << 24) + (o[1] << 16) + (o[2] << 8) + o[3]


def parse_cli_args() -> list:
    """
    Parse command-line arguments for the HTTP discovery tool.
    """
    parser = argparse.ArgumentParser(
        description=
            """
            Attempts a POST request over HTTP to ports within the specified
            range for the given IP addresses and returns the results along
            with additional relevant information.\n
            """
    )

    parser.add_argument(
        '-s',
        '--status-code',
        type=int,
        default=[200],
        nargs='+',
        help='List of acceptable status codes. Default is 200.'
    )
    parser.add_argument(
        '--start-ip',
        default="0.0.0.0",
        help="The starting IP address of the range"
    )
    parser.add_argument(
        '--end-ip',
        default="255.255.255.255",
        help="The ending IP address of the range"
    )

    args = parser.parse_args()

    arguments_tuple = (args.start_ip, args.end_ip, args.status_code)
    return arguments_tuple