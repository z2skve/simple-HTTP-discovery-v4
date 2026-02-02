import sys

class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'
    
    L_BLUE   = '\033[94m'
    L_MAGENTA= '\033[95m'

    @staticmethod
    def title() -> None:
        return \
        fr"""{Colors.L_MAGENTA}
_____/\\\\\\\\\\\____/\\\________/\\\__/\\\\\\\\\\\\_____/\\\________/\\\____________/\\\____        
 ___/\\\/////////\\\_\/\\\_______\/\\\_\/\\\////////\\\__\/\\\_______\/\\\__________/\\\\\____       
  __\//\\\______\///__\/\\\_______\/\\\_\/\\\______\//\\\_\//\\\______/\\\_________/\\\/\\\____      
   ___\////\\\_________\/\\\\\\\\\\\\\\\_\/\\\_______\/\\\__\//\\\____/\\\________/\\\/\/\\\____     
    ______\////\\\______\/\\\/////////\\\_\/\\\_______\/\\\___\//\\\__/\\\_______/\\\/__\/\\\____    
     _________\////\\\___\/\\\_______\/\\\_\/\\\_______\/\\\____\//\\\/\\\______/\\\\\\\\\\\\\\\\_   
      __/\\\______\//\\\__\/\\\_______\/\\\_\/\\\_______/\\\______\//\\\\\______\///////////\\\//__  
       _\///\\\\\\\\\\\/___\/\\\_______\/\\\_\/\\\\\\\\\\\\/________\//\\\_________________\/\\\____ 
        ___\///////////_____\///________\///__\////////////___________\///__________________\///_____            
        {Colors.RESET}"""

    @staticmethod
    def range_set(start_ip: str, end_ip: str) -> str:
        return f"{Colors.L_BLUE}[>] Range set to: {start_ip} - {end_ip}{Colors.RESET}"

    @staticmethod
    def accepted_status(status_codes: list[int]) -> str:
        return f"{Colors.L_BLUE}[>] Accepted Status Codes: {status_codes}{Colors.RESET}"

    @staticmethod
    def info(msg: str) -> str:
        return f"{Colors.YELLOW}[*] {Colors.BOLD}{msg}{Colors.RESET}{Colors.RESET}\n"

    @staticmethod
    def status(msg: str) -> str:
        return f"{Colors.CYAN}[=] {Colors.BOLD}{msg}{Colors.RESET}{Colors.RESET}"
        
    @staticmethod
    def success(msg: str) -> str:
        return f"{Colors.GREEN}[+]{Colors.RESET} {Colors.BOLD}{msg}{Colors.RESET}\n"

    @staticmethod
    def error(msg: str) -> str:
        return f"\n{Colors.RED}[!] {Colors.BOLD}{msg}{Colors.RESET}{Colors.RESET}"
