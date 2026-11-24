import os, sys, subprocess

NAME = "KEGE"
FLAGS = ["--onefile", "--windowed", f"--name={NAME}"]
INPUT_MAIN_FILE = "main_window.py"
INPUT_MODULES = ["kege.py", "kege_login.py", "login_form.py",
                 "platform_kege.py", "end.py", "end_form.py", "stop_exam_with_code.py"]

sep = ";" if os.name == "nt" else ":"

cmd = [sys.executable, "-m", "PyInstaller", *FLAGS]
for m in INPUT_MODULES:
    cmd += ["--hidden-import", os.path.splitext(m)[0]]
cmd += [INPUT_MAIN_FILE]

print(" ".join(cmd))
sys.exit(subprocess.run(cmd).returncode)