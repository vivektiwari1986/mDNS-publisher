#!/usr/bin/env python3
import os
import sys
import subprocess
import signal
import time

# Version information
__version__ = "1.0.0"

# Force unbuffered output so logs appear immediately
sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)

# Global list to track child processes
child_processes = []
shutting_down = False

def parse_aliases_from_csv_arg():
    """Parse aliases from CSV string passed as command-line argument"""
    if len(sys.argv) < 2:
        print("Error: No CSV string provided as command-line argument")
        print("Usage: python3 publish_aliases.py <comma-separated-aliases>")
        sys.exit(1)
    
    # Get CSV string from first command-line argument
    csv_string = sys.argv[1]
    
    if not csv_string.strip():
        print("Error: Empty CSV string provided")
        sys.exit(1)
    
    # Parse comma-separated format to extract aliases
    aliases = []
    empty_entries = 0
    
    # Split the comma-separated string and process each alias
    for alias in csv_string.split(','):
        # Trim whitespace from the alias
        trimmed_alias = alias.strip()
        
        # Validate that the alias is not empty
        if trimmed_alias:
            aliases.append(trimmed_alias)
        else:
            print("Warning: Found empty alias entry, skipping...")
            empty_entries += 1
    
    # Additional validation for completely empty alias list
    if not aliases:
        print("Error: No valid aliases found in CSV string")
        if empty_entries > 0:
            print(f"Found {empty_entries} empty alias entries that were skipped")
        print("Please provide at least one valid alias in comma-separated format")
        sys.exit(1)
    
    if empty_entries > 0:
        print(f"Skipped {empty_entries} empty alias entries")
    
    return aliases



def stop_all_processes():
    """Stop all child processes gracefully"""
    global shutting_down
    shutting_down = True
    
    for process in child_processes:
        if process.poll() is None:  # Process is still running
            try:
                process.terminate()
            except:
                pass
    
    # Wait for all processes to terminate
    for process in child_processes:
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            # Force kill if termination didn't work
            try:
                process.kill()
                process.wait()
            except:
                pass


def signal_handler(signum, frame):
    """Handle SIGTERM and SIGINT by stopping all child processes"""
    print(f"\nReceived signal {signum}, stopping all mdns-publish-cname processes...")
    stop_all_processes()
    sys.exit(0)


def main():
    """Main function to publish all aliases in parallel"""
    global child_processes, shutting_down
    
    # Reset global state
    child_processes = []
    shutting_down = False
    
    # Set up signal handlers
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    
    aliases = parse_aliases_from_csv_arg()
    
    if not aliases:
        print("No aliases found")
        sys.exit(1)
    
    print(f"Found {len(aliases)} aliases to publish:")
    for alias in aliases:
        print(f"  - {alias}")
    
    # Start a separate mdns-publish-cname process for each alias
    print(f"Starting {len(aliases)} mdns-publish-cname processes in parallel...")
    for alias in aliases:
        cmd = ['/opt/venv/bin/mdns-publish-cname', alias]
        print(f"Starting: {' '.join(cmd)}")
        try:
            process = subprocess.Popen(cmd)
            child_processes.append(process)
        except Exception as e:
            print(f"Error starting process for {alias}: {e}")
            stop_all_processes()
            sys.exit(1)
    
    print(f"All {len(child_processes)} processes started")
    
    # Monitor child processes
    try:
        while not shutting_down:
            # Check if any process has exited
            for process in child_processes:
                exit_code = process.poll()
                if exit_code is not None:
                    # A process has exited
                    print(f"Process {process.pid} exited with code {exit_code}")
                    stop_all_processes()
                    sys.exit(exit_code)
            
            # Sleep briefly to avoid busy-waiting
            time.sleep(0.1)
    except KeyboardInterrupt:
        # Handle Ctrl+C
        signal_handler(signal.SIGINT, None)

if __name__ == '__main__':
    main()