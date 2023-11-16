import subprocess
import os

def is_openssl_installed():
    try:
        subprocess.run(["openssl", "version"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def install_openssl():
    print("Installing OpenSSL...")
    subprocess.run(["sudo", "apt-get", "install", "openssl"], check=True)

def generate_env_variables(file_path, variable_names):
    """Generate new variables and add or update them in the .env file."""
    env_updates = {}

    for variable_name in variable_names:
        result = subprocess.run(["openssl", "rand", "-hex", "32"], check=True, capture_output=True, text=True)
        variable_value = result.stdout.strip()
        env_updates[variable_name] = variable_value

    if os.path.exists(file_path):
        with open(file_path, 'r+') as file:
            lines = file.readlines()
            file.seek(0)
            for line in lines:
                if any(line.startswith(f"{var}=") for var in variable_names):
                    key = line.split('=')[0]
                    file.write(f"{key}={env_updates[key]}\n")
                else:
                    file.write(line)
            for var, value in env_updates.items():
                if not any(line.startswith(f"{var}=") for line in lines):
                    file.write(f"{var}={value}\n")
            file.truncate()
    else:
        with open(file_path, 'w') as file:
            for var, value in env_updates.items():
                file.write(f"{var}={value}\n")

if __name__ == "__main__":
    env_file = ".env"
    variable_names = ["KEY", "SALT"]

    if not is_openssl_installed():
        install_openssl()

    generate_env_variables(env_file, variable_names)
    print(f"Variables updated in {env_file}.")
