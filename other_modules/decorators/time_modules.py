import time


def run_time(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        return_value = func(*args, **kwargs)
        print("Total time process: %.6f seconds" % (time.time() - start_time))
        return return_value

    return wrapper
