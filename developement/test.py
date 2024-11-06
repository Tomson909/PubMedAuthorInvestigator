from multiprocessing import Process
from time import sleep
import os

# Define a long-running function (replace with your computation function)
def heavy_computation():
    print("Starting heavy computation...")
    # Simulate a heavy computation that runs indefinitely
    while True:
        pass

# Run the computation with a time limit
def run_with_timeout(timeout):
    # Create and start the process for the heavy computation
    process = Process(target=heavy_computation)
    process.start()
    
    # Wait for the specified timeout
    process.join(timeout=timeout)

    # Check if the process is still running after the timeout
    if process.is_alive():
        print("Time limit exceeded. Terminating the computation.")
        process.terminate()  # Forcefully terminate the process
        process.join()       # Ensure the process has finished
    else:
        print("Computation completed within the time limit.")

# Set the timeout (in seconds) and run
timeout_seconds = 2  # Adjust as needed
run_with_timeout(timeout_seconds)
