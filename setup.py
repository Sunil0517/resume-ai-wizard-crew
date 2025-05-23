#!/usr/bin/env python3
"""
Setup script for resume-ai-wizard-crew project.
This script automates the frontend setup process by:
1. Installing frontend dependencies if needed
2. Building the React application
3. Creating a frontend symlink to the dist directory for FastAPI
"""

import os
import subprocess
import sys
from pathlib import Path

def run_command(command, cwd=None):
    """
    Run a shell command and print its output.
    
    Args:
        command: The command to execute
        cwd: Current working directory for the command (optional)
        
    Returns:
        The exit code of the command
    """
    print(f"Running: {command}")
    process = subprocess.Popen(
        command, 
        shell=True, 
        stdout=subprocess.PIPE, 
        stderr=subprocess.PIPE,
        universal_newlines=True,
        cwd=cwd
    )
    
    stdout, stderr = process.communicate()
    
    if stdout:
        print(stdout)
    
    if stderr:
        print(stderr, file=sys.stderr)
    
    return process.returncode

def main():
    """Set up the frontend build and create necessary symlinks."""
    # Get the current directory
    project_root = os.path.dirname(os.path.abspath(__file__))
    os.chdir(project_root)
    
    # Check if frontend dependencies are installed
    if not os.path.exists('node_modules'):
        print("Installing frontend dependencies...")
        run_command('npm install')
    
    # Build the React frontend
    print("Building frontend...")
    run_command('npm run build')
    
    # Make sure the dist directory is accessible to FastAPI
    dist_dir = os.path.join(project_root, 'dist')
    if os.path.exists(dist_dir):
        print("Frontend build successful.")
        
        # Create a symlink to the dist directory for FastAPI to serve
        frontend_symlink = os.path.join(project_root, 'frontend')
        if not os.path.exists(frontend_symlink):
            print(f"Creating symlink from {dist_dir} to {frontend_symlink}")
            # For Windows
            if os.name == 'nt':
                import ctypes
                kdll = ctypes.windll.LoadLibrary("kernel32.dll")
                kdll.CreateSymbolicLinkA(frontend_symlink.encode(), dist_dir.encode(), 1)
            # For Unix-like systems (macOS, Linux)
            else:
                os.symlink(dist_dir, frontend_symlink)
    else:
        print("Frontend build failed or dist directory not found.")
    
    print("\nSetup completed successfully.")
    print("\nTo start the application, run:")
    print("    python app.py")

if __name__ == "__main__":
    main() 