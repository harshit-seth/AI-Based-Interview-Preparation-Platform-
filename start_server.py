import subprocess, time, sys

proc = subprocess.Popen(
    ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"],
    cwd=r"C:\Users\HARSHIT SETH\interview-prep",
)
print(f"Server started with PID: {proc.pid}")
# Keep running
try:
    while True:
        time.sleep(60)
except KeyboardInterrupt:
    proc.terminate()
    print("Server stopped")
