import subprocess

def retrieve_hash():
    return subprocess.check_output(['git', 'rev-parse', 'HEAD']).decode('ascii').strip()

def update():
    process = subprocess.Popen(['git', 'pull'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    process.wait()

    if process.returncode != 0:
        print('Git pull failed.')