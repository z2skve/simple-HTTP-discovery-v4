######################################################################
#                               main                                 #
######################################################################

import os
import asyncio
import socket
import aiohttp

import v4logger
import v4parser
from v4colors import Colors

# General timeout adjustment for basic network operations
socket.setdefaulttimeout(3.0)


async def resolve_dns(ip: str) -> str:
    """
    Resolves the domain asynchronously using background threads
    to avoid blocking the main event loop.
    """
    try:
        loop = asyncio.get_running_loop()
        domain_info = await loop.run_in_executor(None, socket.gethostbyaddr, ip)
        return domain_info[0]
    except socket.herror:
        return "[No Domain Resolved]"
    except Exception:
        return "[DNS Error]"


async def process_found_ip(
    ip: str, output_queue: asyncio.Queue, text_content: str
) -> None:
    """
    Retrieves information if found of a given IP asynchronously.
    """
    domain = await resolve_dns(ip)
    content_preview = text_content[:2000]

    print(Colors.info(f"[*] Processing: {ip} -> {domain}"))

    await v4logger.queue_data_manager(
        ip=ip, data=content_preview, output=output_queue, domain=domain
    )


async def get_request(
    actual_ip: str,
    output_queue: asyncio.Queue,
    status_codes: list,
    session: aiohttp.ClientSession,
    semaphore: asyncio.Semaphore,
) -> None:
    """
    Asynchronous function to check if a URL is available.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    url = f"http://{actual_ip}"

    async with semaphore:
        try:
            async with session.get(
                url, headers=headers, timeout=2.0, allow_redirects=True
            ) as response:
                if response.status in status_codes:
                    print(
                        Colors.success(f"UP: {actual_ip} (Status: {response.status})")
                    )

                    text_content = await response.text()
                    await process_found_ip(actual_ip, output_queue, text_content)

        except asyncio.TimeoutError:
            pass
        except aiohttp.ClientError:
            pass
        except Exception:
            pass


async def async_main() -> None:
    """
    Main asynchronous function to run the HTTP discovery tool.
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    logs_dir = os.path.join(os.path.dirname(script_dir), "logs")
    filename = os.path.join(logs_dir, "log.txt")
    os.makedirs(logs_dir, exist_ok=True)

    output_queue = asyncio.Queue()
    num_ips_to_print: int = 256

    start_ip, end_ip, status_codes = v4parser.parse_cli_args()

    decimal_start = v4parser.ip_to_int(start_ip)
    decimal_end = v4parser.ip_to_int(end_ip)

    if decimal_start > decimal_end:
        print("Error: Start IP is greater than End IP.")
        return

    print(Colors.title())
    print(Colors.range_set(start_ip, end_ip))
    print(Colors.accepted_status(status_codes))
    print(f"{'-' * 20}\nPress Ctrl+C to stop searching.\n")

    writer_task = asyncio.create_task(
        v4logger.file_writer_worker(output_queue, filename)
    )

    # Maximum number of simultaneous connections.
    max_concurrent_tasks = 1000
    semaphore = asyncio.Semaphore(max_concurrent_tasks)

    connector = aiohttp.TCPConnector(limit=max_concurrent_tasks)

    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = []
        curr = decimal_start

        while curr <= decimal_end:
            current_ip = v4parser.int_to_ip(curr)

            if curr % num_ips_to_print == 0:
                print(Colors.status(f"Targeting: [{current_ip}]"))

            task = asyncio.create_task(
                get_request(current_ip, output_queue, status_codes, session, semaphore)
            )
            tasks.append(task)
            curr += 1

            if len(tasks) >= 5000:
                await asyncio.gather(*tasks)
                tasks = []

        if tasks:
            await asyncio.gather(*tasks)

    # We send None to stop the log worker and wait
    await output_queue.put(None)
    await writer_task


def main():
    try:
        asyncio.run(async_main())
    except KeyboardInterrupt:
        print(Colors.error("\nUser interrupted. Stopping..."))


if __name__ == "__main__":
    main()
