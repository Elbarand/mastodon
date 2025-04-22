import subprocess

# 봇 실행 경로
bots = {
    "professor_bot": "python3 professor_bot/professor_bot.py",
    "shop_bot": "python3 shop_bot/shop_bot.py",
    "student_rumors_bot": "python3 student_rumors_bot/npc_rumor_bot.py"
}

processes = []

for name, command in bots.items():
    print(f"Starting {name}...")
    proc = subprocess.Popen(command, shell=True)
    processes.append(proc)

try:
    for proc in processes:
        proc.wait()
except KeyboardInterrupt:
    print("Shutting down all bots...")
    for proc in processes:
        proc.terminate()
