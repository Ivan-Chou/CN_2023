import threading

# ===============

# global var.

lock_print = threading.Lock() # mutex for print()

# ===============

# ===============

# func

def atomic_print(string: str):
	
	with lock_print:
		print(string, flush=True)

	return
# ===============
