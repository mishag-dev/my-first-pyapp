import platform
import subprocess
import sys

def get_git_config(config_key):
    """Helper function to run git config commands safely."""
    try:
        # subprocess allows us to run terminal commands from within Python
        return subprocess.check_output(['git', 'config', config_key], text=True).strip()
    except subprocess.CalledProcessError:
        return "Not configured"
    except FileNotFoundError:
        return "Git not installed"

def main():
    print("=" * 40)
    print("   MY FIRST PYTHON APP - ENVIRONMENT INFO")
    print("=" * 40)

    # 1. Local Debian/WSL Environment Information
    print("\n[Local System Information]")
    # platform.system() returns the OS name (e.g., Linux)
    print(f"OS Type:       {platform.system()}")
    # platform.release() often contains 'WSL' in the name on Windows Subsystem for Linux
    print(f"Kernel/Release:{platform.release()}")
    # sys.version gives us the specific version of Python running
    print(f"Python Version:{sys.version.split()[0]}")

    # 2. Git/GitHub Environment Information
    print("\n[Git/GitHub Configuration]")
    
    try:
        git_version = subprocess.check_output(['git', '--version'], text=True).strip()
        print(f"Git Version:   {git_version}")
    except FileNotFoundError:
        print("Git Version:   Git is not installed")

    # Fetching user info that would be sent to GitHub
    user_name = get_git_config('user.name')
    user_email = get_git_config('user.email')

    print(f"Git User:      {user_name}")
    print(f"Git Email:     {user_email}")
    
    print("\n" + "=" * 40)

if __name__ == "__main__":
    main()

