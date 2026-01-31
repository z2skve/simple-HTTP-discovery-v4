######################################################################
#                            v4parser                                #
######################################################################

import argparse

def parse_ip(ip_str: str, is_final: bool = False) -> list[int]:
    """
    Transforms the string IP into a list[int].
    """

    try:
        ip_parts = [int(part) for part in ip_str.split('.')]
        if len(ip_parts) != 4:
            raise ValueError

    except ValueError:
        raise argparse.ArgumentTypeError(f"Invalid IP: {ip_str}") 

    return ip_parts


def adjust_options() -> list:
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
        type=parse_ip,
        default=[0, 0, 0, 0],
        help="The starting IP address of the range"
    )
    parser.add_argument(
        '--end-ip',
        type=parse_ip,
        default=[255, 255, 255, 255],
        help="The ending IP address of the range"
    )

    args = parser.parse_args()
    return args