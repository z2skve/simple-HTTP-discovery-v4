######################################################################
#                            v4logger                                #
######################################################################
import asyncio


async def file_writer_worker(output_queue: asyncio.Queue, filename: str) -> None:
    """
    Asynchronous worker task to write output data to a file.
    """
    with open(filename, "a", encoding="utf-8") as f:
        while True:
            item = await output_queue.get()
            if item is None:
                output_queue.task_done()
                break

            try:
                # Escribimos a disco.
                f.write(item)
                f.flush()
            except Exception as e:
                print(f"[!] Error writing log: {e}")
            finally:
                output_queue.task_done()


async def queue_data_manager(
    ip: str, data: str, output: asyncio.Queue, domain: str = "[None]"
) -> None:
    """
    Saves data in an async queue for later processing.
    """
    payload = (
        f"Domain : {domain}\nIP : {ip}\nGET :\n\n{'-' * 20}\n{data}\n{'-' * 20}\n\n"
    )
    await output.put(payload)
