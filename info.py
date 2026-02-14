import platform
import subprocess
import sys
import os

# Set the path to the git repository to ensure commands run in the correct directory
GIT_REPO_PATH = os.path.dirname(os.path.abspath(__file__))

def get_git_config(config_key):
    """Helper function to run git config commands safely."""
    try:
        return subprocess.check_output(
            ['git', 'config', config_key], 
            text=True, 
            stderr=subprocess.DEVNULL, 
            cwd=GIT_REPO_PATH
        ).strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "Not configured"

def get_git_version():
    """Gets the installed Git version."""
    try:
        return subprocess.check_output(
            ['git', '--version'], 
            text=True, 
            stderr=subprocess.DEVNULL, 
            cwd=GIT_REPO_PATH
        ).strip()
    except FileNotFoundError:
        return "Not installed"

def get_git_branches(remote=False):
    """Gets local or remote git branches."""
    command = ['git', 'branch', '--format=%(refname:short)']
    if remote:
        command.append('-r')
    
    try:
        output = subprocess.check_output(
            command, 
            text=True, 
            stderr=subprocess.PIPE, 
            cwd=GIT_REPO_PATH
        )
        if not output:
            return []
        # Clean up branch names, removing remote prefix for display
        branches = [b.strip() for b in output.strip().split('\n')]
        if remote:
            # Handles remote branches like 'origin/main' -> 'main'
            return [b.split('/', 1)[-1] for b in branches if '->' not in b]
        return branches
    except (subprocess.CalledProcessError, FileNotFoundError):
        return []

def print_linux_info():
    """Prints Linux environment information."""
    print("[Linux Environment]")
    print(f"  OS Type:       {platform.system()}")
    print(f"  Kernel/Release:{platform.release()}")

def print_python_info():
    """Prints Python environment information."""
    print("\n[Python Environment]")
    print(f"  Version:       {sys.version.split()[0]}")
    print(f"  Compiler:      {platform.python_compiler()}")

def print_git_info():
    """Prints Git environment and user information."""
    print("\n[Git Environment]")
    git_version = get_git_version()
    
    if not git_version:
        git_version = "Not installed"

    print(f"  Version:       {git_version}")

    if git_version != "Not installed":
        local_branches = get_git_branches(remote=False)
        remote_branches = get_git_branches(remote=True)
        
        if local_branches:
            print(f"  Local Branches:  {', '.join(local_branches)}")
        if remote_branches:
            print(f"  Remote Branches: {', '.join(remote_branches)}")

        print("\n[Git User Information]")
        print(f"  User Name:     {get_git_config('user.name')}")
        print(f"  User Email:    {get_git_config('user.email')}")
        print(f"  GitHub User:   {get_git_config('github.user')}")

def main():
    """Prints formatted environment information."""
    print("=" * 40)
    print("      ENVIRONMENT INFORMATION")
    print("=" * 40)

    print_linux_info()
    print_python_info()
    print_git_info()

    print("\n" + "=" * 40)

if __name__ == "__main__":
    main()