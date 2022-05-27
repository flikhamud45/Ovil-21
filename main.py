# import os
from network.server import Server
from spying import Spy
import time
s = Server()
s.wait_for_client()
# if __name__ == "__main__":
#     os.system("python service.py install --startup")
