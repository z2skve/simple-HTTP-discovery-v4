######################################################################
#                            v4logger                                #
######################################################################
from queue import Queue


def queue_data_manager(ip: str, data: str, output: Queue, domain: str = "[None]") -> None:
    """
    Saves data in a queue for later processing. 

    Args:
            ip: The IP address as a string.
            data: The content to be saved.
            domain: The domain name, if available.
            output: A queue.Queue object to store formatted results.
    """

    payload = (
        f"Domain : {domain}\n"
        f"IP : {ip}\n"
        f"GET :\n\n"
        f"{'-'*20}\n"
        f"{data}\n"
        f"{'-'*20}\n\n"
    )

    output.put(payload)