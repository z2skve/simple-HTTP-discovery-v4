#! /bin/bash/ python
import queue
import argparse
import time
import requests
import pycurl
import socket
import threading
from io import BytesIO


def saveData(ip: str, data: str, domain: str, output: queue) -> None:
    """
    Creates a queue to save the data of each thread individually.
    """
    if not domain:
        domain = "[DOMAIN NOT FOUND]"

    all_data = f"""Domain : {domain}\nIP : {ip}\nGET :
        \n\n {'-'*20}\n {data} \n {'-'*20}\n\n"""
    output.put(all_data)


def reverse_dns(ip: str) -> str | None:
    """
    Retrieves the Domain Name of the IP given
    if possible.
    """

    try:
        domain_name = socket.gethostbyaddr(ip)
        return domain_name[0]
    except socket.herror:
        return None


def requestGET(act_ip4: list, output: queue, status_codes: list) -> str | None:
    """
    Simple function to retrieve if a URL is available.
    """

    try:
        ip = ".".join(map(str, act_ip4))
        response = requests.get(f'http://{ip}', timeout=5)
        if response.status_code in status_codes:
            print(f"\n[SUCCESS] Found URL available {ip}")
            print(cURL_available_ip(ip, output), "\n<", "-"*20, ">")
        else:
            # print(f"[FAIL] URL not available {ip}")
            return None
    except requests.exceptions.RequestException:
        # print(f"An error occurred: {e}")
        return None


def cURL_available_ip(ip: tuple, output: queue) -> str | None:
    """
    Basic function to return the str with the curl
    the webpage which was available.
    """
    packed_text = ""
    buffer = BytesIO()
    cURL = pycurl.Curl()
    cURL.setopt(cURL.URL, f'http://{ip}')
    cURL.setopt(cURL.WRITEDATA, buffer)
    packed_text += f"{'-'*20}\nTrying cURL for {ip}\n"

    try:
        cURL.perform()
        packed_text += f"Connection successful! {ip}{'\n'*2}"

        domain = reverse_dns(ip)

        print(domain, "\n", packed_text, flush=True)
        cURL.close()
        decodedBuffer = buffer.getvalue().decode('utf-8')
        saveData(ip, decodedBuffer, domain, output)
        return decodedBuffer

    except pycurl.error as e:
        print(f"An error occurred: {e}")
        return None


def adjustFirstIP(ip: str = "0.0.0.0") -> list[int]:
    """
    Just transforms the str ipv4 into a list with its
    int numbers.
    """
    ip = list(map(int, ip.split(".")))
    return ip


def adjustSecondIP(ip: str = "255.255.255.255") -> list[int]:
    """
    Just transforms the str ipv4 into a list with its
    int numbers.
    """
    ip = list(map(int, ip.split(".")))
    return ip


def adjustOptions() -> list:
    """
    Adjust the IP ranges by looking into the sys.argv
    introduced, also the response code status wanted.
    """
    parser = argparse.ArgumentParser(
        description="""
        Attempts a POST request over HTTP to ports within the specified
        range for the given IP addresses and returns the results along
        with additional relevant information.

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
        type=adjustFirstIP,
        default=[0, 0, 0, 0],
        help="The starting IP address of the range"
    )
    parser.add_argument(
        '--end-ip',
        type=adjustSecondIP,
        default=[255, 255, 255, 255],
        help="The ending IP address of the range"
    )
    args = parser.parse_args()
    options = [args.start_ip, args.end_ip, args.status_code]

    return options


def main() -> None:
    """
    Initial function which defines each IP.
    """

    threads: list[threading.Thread] = []
    output_queue: queue = queue.Queue()

    start_ip: list = []
    end_ip: list = []
    status: list = []

    start_ip, end_ip, status = adjustOptions()

    ip4_range: list[list] = [start_ip, end_ip]
    act_ip4: list[int] = list(ip4_range[0])
    print("IPv4 range is :", ip4_range)
    print("Accepted Status Code :", status)
    print(f"{'-'*20}\nPress Ctrl+c and wait to finish.")
    try:
        while act_ip4 != list(ip4_range[1]):

            for x in range(ip4_range[0][3], 256):
                act_ip4[3]:  int = x

                if act_ip4 == list(ip4_range[1]):
                    break

                while len(threads) >= 100_000:

                    threads = [
                        thread
                        for thread in threads
                        if thread.is_alive()
                    ]
                    time.sleep(5)

                thread = threading.Thread(
                    target=requestGET,
                    args=(
                        act_ip4,
                        output_queue,
                        status
                    )
                )
                thread.start()
                threads.append(thread)

            if act_ip4 == list(ip4_range[1]):
                print(act_ip4)
                break

            if act_ip4[2] < 255:
                act_ip4[2] += 1
            else:
                act_ip4[2]: int = 0
                act_ip4[1] += 1
                print(act_ip4)

            if not act_ip4[1] <= 255:
                act_ip4[1]: int = 0
                act_ip4[0] += 1
        else:
            print(act_ip4)

    except KeyboardInterrupt:

        print("[DONT QUIT] Saving Data.")

        time.sleep(8)
        results = []
        while not output_queue.empty():
            results.append(output_queue.get())

        with open("dataLogs/log", "a") as file:
            for result in results:
                file.write(result)
                time.sleep(0.2)

        raise BaseException(f"Program Stopped at {act_ip4}")


if __name__ == "__main__":
    main()
