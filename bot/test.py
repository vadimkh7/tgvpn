import subprocess

def get_active_users():
    res = subprocess.run(
        ['bash', '/bot/bash_scripts/getusers.sh'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    print(res.stderr)
    all_users = str(res.stdout).split('\n')
    print(all_users)
    telegram_users = []
    for u in all_users:
        try:
            int(u)
            telegram_users.append(u)
        except ValueError:
            continue
    return telegram_users
print(get_active_users())
