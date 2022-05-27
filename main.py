# import os
from network.server import Server
from network import consts
from spying import Spy
import time
s = Server()
s.wait_for_client()
s = Spy()
# s.start_sniffing_on_net("127.0.0.1", consts.MITM_DEFAULT_PORT)
#s.start_sniffing_to_file("logger.txt", "127.0.0.1", consts.MITM_DEFAULT_PORT)
# if __name__ == "__main__":
#     os.system("python service.py install --startup")
