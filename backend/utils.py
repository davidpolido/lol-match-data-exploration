import time


def retry_function(func, p_args, k_args={}, max_attempts=5, reps=2, sleep_timer=None):
    attempt = 1
    rep = 1
    while attempt <= max_attempts:
        try:
            result = func(*p_args, **k_args)
            break
        except Exception as e:
            print(f"Failed!", e)
            max_attempts_reached = attempt == max_attempts
            attempt += 1
            result = None

            if max_attempts_reached and sleep_timer and rep <= reps:
                time.sleep(sleep_timer)
                rep += 1
                attempt = 1

    return result
