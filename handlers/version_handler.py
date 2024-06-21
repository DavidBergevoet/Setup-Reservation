import subprocess

def retrieve_hash():
    return subprocess.check_output(['git', 'rev-parse', 'HEAD']).decode('ascii').strip()

def update():
    subprocess.check_output(['git', 'pull'])