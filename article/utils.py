import time

def file_iterators(filename,chunk_size=1024*100, time_interval=1):
    while True:
        c = filename.read(chunk_size)
        if c:
            yield c
            time.sleep(time_interval)
        else:
            break