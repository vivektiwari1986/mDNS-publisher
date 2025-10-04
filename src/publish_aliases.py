#!/usr/bin/env python3
import os
import sys

# Version information
__version__ = "1.0.0"

# Force unbuffered output so logs appear immediately
sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)

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



def main():
    """Main function to publish all aliases using execv"""
    aliases = parse_aliases_from_csv_arg()
    
    if not aliases:
        print("No aliases found")
        sys.exit(1)
    
    print(f"Found {len(aliases)} aliases to publish:")
    for alias in aliases:
        print(f"  - {alias}")
    
    # Prepare command for execv - pass all aliases as arguments
    cmd = ['/opt/venv/bin/mdns-publish-cname'] + aliases
    print(f"Executing: {' '.join(cmd)}")
    
    # Replace current process with mdns-publish-cname
    os.execv('/opt/venv/bin/mdns-publish-cname', cmd)

if __name__ == '__main__':
    main()