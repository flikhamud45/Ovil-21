from spying.portforwardlib import forwardPort


from typing import Tuple, List



def open_port(port) -> List[Tuple[str, bool, str]]:
    """
    return a list of every router it tryed. each item is a tuple of router ip, whether succeeded and error message.
    """
    forwardPort(port, port, None, None, False, "TCP", 0, "Ovil-21", True)
    ans = []
    return ans


if __name__ == "__main__":
    open_port(5678)
