import subprocess

def run_python(file_path):
    return subprocess.run(["python", file_path], capture_output=True, text=True).stdout

def compile_cpp(file_path):
    exe = file_path.replace(".cpp", ".exe")
    subprocess.run(["g++", file_path, "-o", exe])
    return subprocess.run([exe], capture_output=True, text=True).stdout
