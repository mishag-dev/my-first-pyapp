from flask import Flask, Response
import platform
import subprocess
import sys
import os

app = Flask(__name__)

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

def generate_info_text():
    """Generates the environment information as a string."""
    info = []
    info.append("=" * 40)
    info.append("      ENVIRONMENT INFORMATION")
    info.append("=" * 40)
    
    info.append("\n[Linux Environment]")
    info.append(f"  OS Type:       {platform.system()}")
    info.append(f"  Kernel/Release:{platform.release()}")

    info.append("\n[Python Environment]")
    info.append(f"  Version:       {sys.version.split()[0]}")
    info.append(f"  Compiler:      {platform.python_compiler()}")

    info.append("\n[Git Information]")
    git_version = get_git_version()
    info.append(f"  Version:       {git_version}")
    
    if "Not installed" not in git_version:
        local_branches = get_git_branches(remote=False)
        remote_branches = get_git_branches(remote=True)
        
        if local_branches:
            info.append(f"  Local Branches:  {', '.join(local_branches)}")
        if remote_branches:
            info.append(f"  Remote Branches: {', '.join(remote_branches)}")

        info.append(f"  User Name:     {get_git_config('user.name')}")
        info.append(f"  User Email:    {get_git_config('user.email')}")
        info.append(f"  GitHub User:   {get_git_config('github.user')}")

    info.append("\n[Kubernetes Environment]")
    try:
        context = subprocess.check_output(
            ['kubectl', 'config', 'current-context'], 
            text=True, 
            stderr=subprocess.DEVNULL
        ).strip()
        info.append(f"  Current Context: {context}")

        cluster_info = subprocess.check_output(
            ['kubectl', 'cluster-info'], 
            text=True, 
            stderr=subprocess.DEVNULL
        ).strip().split('\n')[0]
        info.append(f"  Cluster Info:    {cluster_info}")

        pod_status_output = subprocess.check_output(
            ['kubectl', 'get', 'pods', '--all-namespaces', '-o', 'jsonpath={.items[*].status.conditions[?(@.type==\"Ready\")].status}'],
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
        info.append(f"  Health Status:   {health_summary}")

    except (subprocess.CalledProcessError, FileNotFoundError):
        info.append("  kubectl not found or not configured.")

    info.append("\n" + "=" * 40)
    return "\n".join(info)

@app.route('/')
def index():
    return Response(generate_info_text(), mimetype='text/plain')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
