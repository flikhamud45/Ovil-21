from spying import Spy
import time
s = Spy()
s.start_sniffing_to_file("logger.txt")
print("started")
input()
s.stop_sniffing()
print("stopped")
