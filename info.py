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

def get_git_version():
    try:
        return subprocess.check_output(['git', '--version'], text=True).strip()
    except FileNotFoundError:
        return "Git not installed"

def get_python_version():
    return sys.version.split()[0]  # Get just the version number (e.g., '3.8.10')

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
    # 3. Check if Git is installed and get its version
    print("\n[Git Information]")
    # 4. Fetching Git version using subprocess to run 'git --version' command
    print("Checking for Git installation and version...")
    print("Running 'git --version' command...")
    print("This will help us determine if Git is installed and which version is available.")
    print("If Git is not installed, we will see a message indicating that.")
    # 5. Fetching user info that would be sent to GitHub using 'git config' commands
    print("\n[Git User Configuration]")
    print("Fetching Git user name and email configuration...")
    print("This will show us the user name and email that Git is configured to use for commits and interactions with GitHub.") 
    # 6. Displaying the results
    print("\n[Results]")
    print("\n" + "=" * 40)

    # Check if Git is installed and get its version using the helper function       
    try:
        git_version = subprocess.check_output(['git', '--version'], text=True).strip()
        print(f"Git Version:   {git_version}")
    except FileNotFoundError:
        print("Git Version:   Git is not installed")

    # Fetching user info that would be sent to GitHub
    user_name = get_git_config('user.name')
    user_email = get_git_config('user.email')
    github_user = get_git_config('github.user')

    print(f"Git User Name: {user_name}")
    print(f"Git Email:     {user_email}")
    print(f"GitHub User:   {github_user}")
    
    print("\n" + "=" * 40)

if __name__ == "__main__":
    main()
