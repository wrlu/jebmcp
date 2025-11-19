import platform
import os
import time
import socket
import subprocess
# JEB 5.33.0 has removed the `--script` parameter.
DEMO_JEB_PATH = os.path.join(os.path.expanduser("~") , "Applications", "JEB-5.30.0", "jeb_linux.sh")
jeb_start_cmd = DEMO_JEB_PATH

jeb_run_script_cmd = [
    jeb_start_cmd, "-c", "--srv2", 
    "--script=" + os.path.join(os.path.dirname(os.path.abspath(__file__)), "jeb-mcp", "src", "jeb_mcp", "MCP.py")
]

def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.settimeout(1)
            s.connect(('localhost', port))
            return True
        except (ConnectionRefusedError, OSError):
            return False

def main():
    port = 16161
    check_interval = 5
    while True:
        if not is_port_in_use(port):
            environ = os.environ.copy()
            environ.update({
                "JEB_MCP_DAEMON": "1"
            })
            subprocess.run(jeb_run_script_cmd, env=environ)
        time.sleep(check_interval)

if __name__ == "__main__":
    main()
