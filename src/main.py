######################################################################
#                               main                                 #
######################################################################

import os
import queue
import threading
import concurrent.futures
import requests
import socket

import v4logger
import v4parser
from v4colors import Colors

socket.setdefaulttimeout(3.0)

def process_found_ip(ip: str, output_queue: queue.Queue, response_obj) -> None:
    """
    Retrieves information if found of a given IP.
    """
    
    try:
        domain = socket.gethostbyaddr(ip)[0]
    except socket.herror:
        domain = "[No Domain Resolved]"
    except Exception:
        domain = "[DNS Error]"

    content_preview = response_obj.text[:2000] 
    
    print(Colors.info(f"[*] Procesando: {ip} -> {domain}"))

    v4logger.queue_data_manager(
        ip=ip, 
        data=content_preview, 
        output=output_queue, 
        domain=domain
    )


def get_request(actual_ip: str, output_queue: queue.Queue, status_codes: list) -> str | None:
    """
    Simple function to retrieve if a URL is available.
    """

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        response = requests.get(
            f'http://{actual_ip}', 
            timeout=2, 
            headers=headers,
            allow_redirects=True
        )

        if response.status_code in status_codes:
            print(Colors.success(f"UP: {actual_ip} (Status: {response.status_code})"))
            process_found_ip(actual_ip, output_queue, response)

    except requests.exceptions.ConnectTimeout:
        pass
    except requests.exceptions.RequestException:
        pass


def main() -> None:
    """
    Main function to run the HTTP discovery tool.
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    logs_dir = os.path.join(os.path.dirname(script_dir), "logs")
    filename = os.path.join(logs_dir, "log.txt")
    os.makedirs(logs_dir, exist_ok=True)

    output_queue: queue = queue.Queue()
    num_ips_to_print: int = 256

    start_ip: str 
    end_ip: str
    status_codes: list[int]

    start_ip, end_ip, status_codes = v4parser.parse_cli_args()

    decimal_start = v4parser.ip_to_int(start_ip)
    decimal_end = v4parser.ip_to_int(end_ip)

    if decimal_start > decimal_end:
        print("Error: Start IP is greater than End IP.")
        return

    print(Colors.title())

    print(Colors.range_set(start_ip, end_ip))
    print(Colors.accepted_status(status_codes))

    print(f"{'-'*20}\nPress Ctrl+C to stop searching.\n")

    writer_thread = threading.Thread(
        target=v4logger.file_writer_worker, 
        args=(output_queue, filename)
    )

    writer_thread.daemon = True
    writer_thread.start()

    def ip_generator():
        curr = decimal_start
        while curr <= decimal_end:
            current_ip = v4parser.int_to_ip(curr)

            if curr % num_ips_to_print == 0 : 
                print(Colors.status(f"Targeting: [{current_ip}]"))

            yield current_ip
            curr += 1

    max_threads = 100
    max_queue_size = max_threads * 2 

    semaphore = threading.BoundedSemaphore(value=max_queue_size)
    executor = concurrent.futures.ThreadPoolExecutor(max_workers=max_threads)

    def task_done_callback(_):
        semaphore.release()

    try:
        for current_ip in ip_generator():
            
            semaphore.acquire()
            future = executor.submit(get_request, current_ip, output_queue, status_codes)
            future.add_done_callback(task_done_callback)

    except KeyboardInterrupt:
        print(Colors.error("User interrupted. Stopping..."))
        executor.shutdown(wait=False, cancel_futures=True)

    finally:
        output_queue.put(None)
        writer_thread.join(timeout=5)

if __name__ == "__main__":
    main()
