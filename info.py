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
    print("\n[Git Information]")
    git_version = get_git_version()

    if "Not installed" in git_version:
        print(f"  Version:       {git_version}")
        return

    print(f"  Version:       {git_version}")
    
    local_branches = get_git_branches(remote=False)
    remote_branches = get_git_branches(remote=True)
    
    if local_branches:
        print(f"  Local Branches:  {', '.join(local_branches)}")
    if remote_branches:
        print(f"  Remote Branches: {', '.join(remote_branches)}")

    print(f"  User Name:     {get_git_config('user.name')}")
    print(f"  User Email:    {get_git_config('user.email')}")
    print(f"  GitHub User:   {get_git_config('github.user')}")

def print_kubernetes_info():
    """Prints Kubernetes environment and health status."""
    print("\n[Kubernetes Environment]")
    try:
        context = subprocess.check_output(
            ['kubectl', 'config', 'current-context'], 
            text=True, 
            stderr=subprocess.DEVNULL
        ).strip()
        print(f"  Current Context: {context}")

        cluster_info = subprocess.check_output(
            ['kubectl', 'cluster-info'], 
            text=True, 
            stderr=subprocess.DEVNULL
        ).strip().split('\n')[0] # Display only the first line of cluster-info
        print(f"  Cluster Info:    {cluster_info}")

        pod_status_output = subprocess.check_output(
            ['kubectl', 'get', 'pods', '--all-namespaces', '-o', 'jsonpath={.items[*].status.conditions[?(@.type=="Ready")].status}'],
            text=True,
            stderr=subprocess.DEVNULL
        ).strip()
        if pod_status_output:
            statuses = pod_status_output.split()
            ready_pods = statuses.count('True')
            total_pods = len(statuses)
            health_summary = f"{ready_pods}/{total_pods} pods ready"
        else:
            health_summary = "No pods found"
        print(f"  Health Status:   {health_summary}")

    except (subprocess.CalledProcessError, FileNotFoundError):
        print("  kubectl not found or not configured.")

def main():
    """Prints formatted environment information."""
    print("=" * 40)
    print("      ENVIRONMENT INFORMATION")
    print("=" * 40)

    print_linux_info()
    print_python_info()
    print_git_info()
    print_kubernetes_info()

    print("\n" + "=" * 40)

if __name__ == "__main__":
    main()