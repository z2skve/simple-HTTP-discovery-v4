######################################################################
#                               main                                 #
######################################################################

import queue
import time
import requests
import pycurl
import socket
import threading

from io import BytesIO  

import v4logger
import v4parser


def reverse_dns(ip: str) -> str | None:
    """
    Retrieves information if found of a given IP.
    """

    try:
        domain_name, alias, addr_list = socket.gethostbyaddr(ip)
        return domain_name
    except socket.herror:
        return None


def get_request(act_ip4: list, output: queue, status_codes: list) -> str | None:
    """
    Simple function to retrieve if a URL is available.
    """

    try:
        ip = ".".join(map(str, act_ip4))
        response = requests.get(f'http://{ip}', timeout=5)

        if response.status_code in status_codes:
            print(f"\n[SUCCESS] Found URL available {ip}")
            print(curl_available_ip(ip, output), "\n<", "-"*20, ">")
        else:
            # print(f"[FAIL] URL not available {ip}")
            return None
    except requests.exceptions.RequestException:
        # print(f"An error occurred: {e}")
        return None


def curl_available_ip(ip: tuple, output: queue) -> str | None:
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
        v4logger.queue_data_manager(ip, decodedBuffer, domain, output)
        return decodedBuffer

    except pycurl.error as e:
        print(f"An error occurred: {e}")
        return None

def main() -> None:
    """
    Main function to run the HTTP discovery tool.
    """

    threads: list[threading.Thread] = []
    output_queue: queue = queue.Queue()

    start_ip: list = []
    end_ip: list = []
    status: list = []

    number_attempts: int = 0

    start_ip, end_ip, status = v4parser.adjust_options()

    ip4_range: list[list] = [start_ip, end_ip]
    act_ip4: list[int] = list(ip4_range[0])
    print("IPv4 Range set to :", ip4_range)
    print("Accept Status Code :", status)
    print(f"{'-'*20}\nPress Ctrl+c to stop searching.")
    try:
        while act_ip4 != list(ip4_range[1]):
            number_attempts += 1

            for x in range(ip4_range[0][3], 256):
                act_ip4[3] = x

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
                    target=get_request,
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
                act_ip4[2] = 0
                act_ip4[1] += 1
                print(act_ip4)

            if not act_ip4[1] <= 255:
                act_ip4[1] = 0
                act_ip4[0] += 1
        else:
            print(act_ip4)

    except KeyboardInterrupt:
        time.sleep(1)
        results = []
        while not output_queue.empty():
            results.append(output_queue.get())

        with open("logs/log.txt", "a") as file:
            for result in results:
                file.write(result)
                time.sleep(0.2)

        raise BaseException(f"Program Stopped at {act_ip4}")


if __name__ == "__main__":
    main()
