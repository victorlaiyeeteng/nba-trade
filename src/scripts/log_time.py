from datetime import datetime
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../../"))
log_file = os.path.join(project_root, "logs", "time_logs_test.txt")
os.makedirs(os.path.dirname(log_file), exist_ok=True)

with open(log_file, "a") as f:
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    f.write(f"{now}\n")


print(f"Logged current time: {now}")

