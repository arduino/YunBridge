import time


def try_bind(socket, address, port, timeout=30):
    start_time = time.time()
    while (time.time() - start_time) < timeout:
        try:
            return socket.bind((address, port))
        except:
            time.sleep(1)
            # try one last time, just to throw up an exception...
    return socket.bind((address, port))
