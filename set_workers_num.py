import subprocess
import os

def run_command(command):
    try:
        return subprocess.check_output(command, shell=True, text=True).strip()
    except subprocess.CalledProcessError:
        return None

def get_num_cores():
    num_cores = run_command('nproc') or run_command('sysctl -n hw.logicalcpu')
    if num_cores:
        return int(num_cores)
    else:
        raise RuntimeError("Can't determine the number of CPU cores")

def update_env_file(file_path, key, value):
    # Update or append a key-value pair in an environment file.

    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"{file_path} not found")

    updated = False
    with open(file_path, 'r+') as file:
        lines = file.readlines()
        file.seek(0)
        file.truncate()

        for line in lines:
            if line.startswith(f"{key}="):
                line = f"{key}={value}\n"
                updated = True
            file.write(line)

        if not updated:
            file.write(f"{key}={value}\n")

if __name__ == "__main__":
    try:  # to set workers twice as num of CPU cores:
        num_cores = get_num_cores()
        workers = 2 * num_cores
        env_file_path = '.env'
        update_env_file(env_file_path, 'WORKERS', workers)

        print(f"Number of workers to be set: {workers}")
        print("Updated .env file:")
        with open(env_file_path, 'r') as file:
            print(''.join([line for line in file if line.startswith("WORKERS=")]))

    except Exception as e:
        print(f"Error: {e}")
        exit(1)
