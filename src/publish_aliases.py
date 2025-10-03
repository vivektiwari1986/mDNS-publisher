#!/usr/bin/env python3
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from mdns_publisher import publish_single_alias

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
    """Main function to publish all aliases in parallel"""
    aliases = parse_aliases_from_csv_arg()
    
    print(f"Found {len(aliases)} aliases to publish:")
    for alias in aliases:
        print(f"  - {alias}")
    
    print("\nStarting parallel alias publishing...")
    
    # Use ThreadPoolExecutor to run alias publishing in parallel
    results = []
    with ThreadPoolExecutor(max_workers=len(aliases)) as executor:
        # Submit all alias publishing tasks
        future_to_alias = {executor.submit(publish_single_alias, alias): alias for alias in aliases}
        
        # Collect results as they complete
        for future in as_completed(future_to_alias):
            alias = future_to_alias[future]
            try:
                result = future.result()
                results.append(result)
            except Exception as exc:
                print(f"EXCEPTION: {alias} generated an exception: {exc}")
                results.append({'alias': alias, 'success': False, 'output': '', 'error': str(exc)})
    
    # Analyze results
    successful = [r for r in results if r['success']]
    failed = [r for r in results if not r['success']]
    
    print("\n=== Alias Publishing Summary ===")
    print(f"Total aliases processed: {len(aliases)}")
    print(f"Successful: {len(successful)}")
    print(f"Failed: {len(failed)}")
    
    if failed:
        print("\nFailed aliases:")
        for result in failed:
            print(f"  - {result['alias']}: {result['error']}")
    
    if successful:
        print(f"\nAt least one alias published successfully. Service will continue running...")
        # Keep the process running indefinitely
        try:
            while True:
                time.sleep(3600)  # Sleep for 1 hour at a time
        except KeyboardInterrupt:
            print("\nReceived interrupt signal, shutting down...")
            sys.exit(0)
    else:
        print("\nError: All alias publishing attempts failed")
        sys.exit(1)

if __name__ == '__main__':
    main()