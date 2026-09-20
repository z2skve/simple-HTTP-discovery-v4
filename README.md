# simple-HTTP-discovery-v4 (SHDv4) 🚀

A high-performance, asynchronous IPv4 HTTP discovery tool written in Python. Designed to scan massive IP ranges efficiently using a thread-pool executor with backpressure control to keep memory usage flat.

![Python Version](https://img.shields.io/badge/python-3.13+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## ✨ Features

* **DNS Resolution:** Integrated reverse DNS lookups for discovered targets.
* **Real-time Logging:** Asynchronous file writing via a dedicated task.

> ![License](pictures/cap1.png)

## 🛠️ Installation

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/tu-usuario/simple-HTTP-discovery-v4.git](https://github.com/tu-usuario/simple-HTTP-discovery-v4.git)
   cd simple-HTTP-discovery-v4
   ```
Install dependencies:
```bash
pip install aiohttp
```

🚀 Usage

Run the script from the src directory:
```bash
python main.py --start-ip 8.8.8.0 --end-ip 8.8.8.255 --status-code 200 301
```

Arguments:

* `--start-ip`: Starting IPv4 address.
* `--end-ip`: Ending IPv4 address.
* `--status-code`: One or more HTTP status codes to consider as "found" (e.g., 200 301 403).

📁 Project Structure
```plaintext
simple-HTTP-discovery-v4/
├── logs/               # Scan results (log.txt)
├── src/
│   ├── main.py         # Main logic & Async event loop
│   ├── v4colors.py     # ANSI Color constants & formatting
│   ├── v4logger.py     # Async file writer task
│   └── v4parser.py     # CLI argument parsing & IP math
└── README.md
```

⚙️ Technical Architecture

This tool implements an asynchronous producer-consumer pattern using Python's `asyncio` and `aiohttp`.

* **Async Event Loop**: Manages thousands of simultaneous non-blocking network requests.
* **Semaphore**: Controls concurrency limits (e.g., 1000 simultaneous connections).
* **Workers (Tasks)**: Lightweight asynchronous functions process HTTP requests and execute reverse DNS lookups in non-blocking executors.
* **Logger**: An asynchronous background task handles I/O operations to prevent disk-writing from stalling network scanning.

⚠️ Disclaimer

Scanning networks you do not own or have explicit permission to test may be illegal.

📄 License

Distributed under the MIT License.