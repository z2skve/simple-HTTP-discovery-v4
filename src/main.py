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


def maximize_open_files():
    """
    Attempts to raise the open file descriptor limit to the maximum allowed by the OS.
    This prevents 'OSError: [Errno 24] Too many open files' during mass scanning.
    Implemented cross-platform:
    - Windows gracefully ignores this as it lacks the 'resource' module (and handles IOCP sockets better).
    - macOS/Linux safely negotiate the limit avoiding 'ValueError' on infinite limits.
    """
    try:
        import resource

        _, hard = resource.getrlimit(resource.RLIMIT_NOFILE)

        if hard == resource.RLIM_INFINITY:
            target_limit = 65535
        else:
            target_limit = min(hard, 65535)

        resource.setrlimit(resource.RLIMIT_NOFILE, (target_limit, hard))
        print(Colors.info(f"[*] Max open files limit raised to {target_limit}"))
    except ImportError:
        pass
    except Exception as e:
        print(Colors.error(f"[!] Could not raise open files limit: {e}"))


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
    ip: str, output_queue: asyncio.Queue, text_content: str, port: int
) -> None:
    """
    Retrieves information if found of a given IP asynchronously.
    """
    domain = await resolve_dns(ip)
    content_preview = text_content[:2000]

    print(Colors.info(f"[*] Processing: {ip}:{port} -> {domain}"))

    await v4logger.queue_data_manager(
        ip=f"{ip}:{port}", data=content_preview, output=output_queue, domain=domain
    )


async def worker(
    target_queue: asyncio.Queue,
    output_queue: asyncio.Queue,
    status_codes: list,
    session: aiohttp.ClientSession,
) -> None:
    """
    Async worker that continuously pulls IPs from the queue and scans them.
    This replaces the gather/semaphore bottleneck with a pure flat-memory pool.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    while True:
        item = await target_queue.get()
        if item is None:
            target_queue.task_done()
            break

        actual_ip, port = item
        scheme = "https" if port == 443 else "http"
        url = f"{scheme}://{actual_ip}:{port}"

        try:
            async with session.get(
                url, headers=headers, timeout=2.0, allow_redirects=True, ssl=False
            ) as response:
                if response.status in status_codes:
                    print(
                        Colors.success(
                            f"UP: {actual_ip}:{port} (Status: {response.status})"
                        )
                    )

                    text_content = await response.text()
                    await process_found_ip(actual_ip, output_queue, text_content, port)

        except asyncio.TimeoutError:
            pass
        except aiohttp.ClientError:
            pass
        except Exception:
            pass
        finally:
            target_queue.task_done()


async def async_main() -> None:
    """
    Main asynchronous function to run the HTTP discovery tool.
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    logs_dir = os.path.join(os.path.dirname(script_dir), "logs")
    filename = os.path.join(logs_dir, "log.txt")
    os.makedirs(logs_dir, exist_ok=True)

    output_queue = asyncio.Queue()

    # Prevents IP generator from overflowing memory
    target_queue = asyncio.Queue(maxsize=5000)

    num_ips_to_print: int = 8192

    start_ip, end_ip, status_codes, ports = v4parser.parse_cli_args()

    decimal_start = v4parser.ip_to_int(start_ip)
    decimal_end = v4parser.ip_to_int(end_ip)

    if decimal_start > decimal_end:
        print("Error: Start IP is greater than End IP.")
        return

    print(Colors.title())
    print(Colors.range_set(start_ip, end_ip))
    print(Colors.accepted_status(status_codes))
    print(f"[*] Ports configured: {ports}")
    print(f"{'-' * 20}\nPress Ctrl+C to stop searching.\n")

    writer_task = asyncio.create_task(
        v4logger.file_writer_worker(output_queue, filename)
    )

    max_concurrent_tasks = 1000
    connector = aiohttp.TCPConnector(limit=max_concurrent_tasks, ssl=False)

    async with aiohttp.ClientSession(connector=connector) as session:
        workers = [
            asyncio.create_task(
                worker(target_queue, output_queue, status_codes, session)
            )
            for _ in range(max_concurrent_tasks)
        ]

        curr = decimal_start

        while curr <= decimal_end:
            current_ip = v4parser.int_to_ip(curr)

            if curr % num_ips_to_print == 0:
                print(Colors.status(f"Progress: Reached subnet [{current_ip}]"))

            for port in ports:
                await target_queue.put((current_ip, port))

            curr += 1

        await target_queue.join()

        for _ in range(max_concurrent_tasks):
            await target_queue.put(None)

        await asyncio.gather(*workers)

    # We send None to stop the log worker and wait
    await output_queue.put(None)
    await writer_task


def main():
    maximize_open_files()
    try:
        asyncio.run(async_main())
    except KeyboardInterrupt:
        print(Colors.error("\nUser interrupted. Stopping..."))


if __name__ == "__main__":
    main()
