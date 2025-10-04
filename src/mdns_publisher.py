#!/usr/bin/env python3
"""
Module for publishing individual mDNS aliases using mdns-publish-cname.
"""
import subprocess


def publish_single_alias(alias, mdns_publish_path='/opt/venv/bin/mdns-publish-cname', timeout=120):
    """
    Publish a single alias using mdns-publish-cname.
    
    Args:
        alias (str): The mDNS alias to publish
        mdns_publish_path (str): Path to the mdns-publish-cname executable
        timeout (int): Timeout in seconds for the publishing process
        
    Returns:
        dict: Result dictionary with keys:
            - alias (str): The alias that was processed
            - success (bool): Whether the publishing succeeded
            - output (str): Standard output from the command
            - error (str): Error message if any, None if successful
    """
    print(f"Starting mDNS publishing for alias: {alias}")
    
    try:
        # Run mdns-publish-cname for this specific alias
        result = subprocess.run(
            [mdns_publish_path, alias],
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        if result.returncode == 0:
            print(f"SUCCESS: {alias} published successfully")
            if result.stdout:
                print(f"  Output: {result.stdout.strip()}")
            return {
                'alias': alias,
                'success': True,
                'output': result.stdout,
                'error': None
            }
        else:
            print(f"FAILED: {alias} publishing failed with exit code {result.returncode}")
            if result.stderr:
                print(f"  Error: {result.stderr.strip()}")
            return {
                'alias': alias,
                'success': False,
                'output': result.stdout,
                'error': result.stderr
            }
            
    except subprocess.TimeoutExpired:
        error_msg = f'Timeout after {timeout} seconds'
        print(f"TIMEOUT: {alias} publishing timed out after {timeout} seconds")
        return {
            'alias': alias,
            'success': False,
            'output': '',
            'error': error_msg
        }
    except Exception as e:
        error_msg = str(e)
        print(f"EXCEPTION: {alias} publishing failed with exception: {e}")
        return {
            'alias': alias,
            'success': False,
            'output': '',
            'error': error_msg
        }