from spying import Spy

s = Spy()
s.start_sniffing_from_file("logger")
print("started")
input()
print("stopped")
