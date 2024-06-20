import socket
import requests.packages.urllib3.util.connection as urllib3_cn  # type: ignore

urllib3_cn.allowed_gai_family = lambda: socket.AF_INET
