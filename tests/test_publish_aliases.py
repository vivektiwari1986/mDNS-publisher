#!/usr/bin/env python3
"""
Tests for the publish_aliases module.
"""
import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import publish_aliases


class TestPublishAliases(unittest.TestCase):
    """Test cases for the publish_aliases module."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_aliases = ["alias1.local", "alias2.local", "alias3.local"]
        
    def test_parse_aliases_from_csv_arg_success(self):
        """Test successful parsing of aliases from CSV string."""
        csv_string = ','.join(self.test_aliases)
        with patch.object(sys, 'argv', ['script_name', csv_string]):
            aliases = publish_aliases.parse_aliases_from_csv_arg()
            self.assertEqual(aliases, self.test_aliases)
    
    def test_parse_aliases_from_csv_arg_no_arguments(self):
        """Test parsing when no arguments are provided."""
        with patch.object(sys, 'argv', ['script_name']):
            with patch('builtins.print') as mock_print:
                with self.assertRaises(SystemExit) as cm:
                    publish_aliases.parse_aliases_from_csv_arg()
                
                self.assertEqual(cm.exception.code, 1)
                mock_print.assert_any_call("Error: No CSV string provided as command-line argument")
                mock_print.assert_any_call("Usage: python3 publish_aliases.py <comma-separated-aliases>")
    
    def test_parse_aliases_from_csv_arg_single_alias(self):
        """Test parsing with a single alias."""
        single_alias = "single.local"
        expected = ["single.local"]
        with patch.object(sys, 'argv', ['script_name', single_alias]):
            aliases = publish_aliases.parse_aliases_from_csv_arg()
            self.assertEqual(aliases, expected)
    
    def test_parse_aliases_from_csv_arg_with_whitespace(self):
        """Test parsing CSV string with whitespace around aliases."""
        csv_string = " alias1.local , alias2.local,  alias3.local "
        expected = ["alias1.local", "alias2.local", "alias3.local"]
        with patch.object(sys, 'argv', ['script_name', csv_string]):
            aliases = publish_aliases.parse_aliases_from_csv_arg()
            self.assertEqual(aliases, expected)
    
    def test_parse_aliases_from_csv_arg_with_empty_entries(self):
        """Test parsing CSV string with empty entries."""
        csv_string = "alias1.local,,alias2.local,,"
        expected = ["alias1.local", "alias2.local"]
        with patch.object(sys, 'argv', ['script_name', csv_string]):
            with patch('builtins.print') as mock_print:
                aliases = publish_aliases.parse_aliases_from_csv_arg()
                self.assertEqual(aliases, expected)
                mock_print.assert_any_call("Warning: Found empty alias entry, skipping...")
                mock_print.assert_any_call("Skipped 3 empty alias entries")
    
    def test_parse_aliases_from_csv_arg_empty_string(self):
        """Test parsing with empty CSV string."""
        with patch.object(sys, 'argv', ['script_name', '']):
            with patch('builtins.print') as mock_print:
                with self.assertRaises(SystemExit) as cm:
                    publish_aliases.parse_aliases_from_csv_arg()
                
                self.assertEqual(cm.exception.code, 1)
                mock_print.assert_any_call("Error: Empty CSV string provided")
    
    def test_parse_aliases_from_csv_arg_only_empty_entries(self):
        """Test parsing CSV string with only empty entries."""
        csv_string = ",,, ,"
        with patch.object(sys, 'argv', ['script_name', csv_string]):
            with patch('builtins.print') as mock_print:
                with self.assertRaises(SystemExit) as cm:
                    publish_aliases.parse_aliases_from_csv_arg()
                
                self.assertEqual(cm.exception.code, 1)
                mock_print.assert_any_call("Error: No valid aliases found in CSV string")
                mock_print.assert_any_call("Found 5 empty alias entries that were skipped")
    
    @patch('publish_aliases.os.execv')
    @patch('builtins.print')
    def test_main_success(self, mock_print, mock_execv):
        """Test main function with successful execv call."""
        csv_string = ','.join(self.test_aliases)
        with patch.object(sys, 'argv', ['script_name', csv_string]):
            # execv should be called and not return (it replaces the process)
            publish_aliases.main()
            
            # Verify execv was called with correct arguments
            expected_cmd = ['/opt/venv/bin/mdns-publish-cname'] + self.test_aliases
            mock_execv.assert_called_once_with('/opt/venv/bin/mdns-publish-cname', expected_cmd)
            
            # Verify print statements
            mock_print.assert_any_call(f"Found {len(self.test_aliases)} aliases to publish:")
            for alias in self.test_aliases:
                mock_print.assert_any_call(f"  - {alias}")
            mock_print.assert_any_call(f"Executing: {' '.join(expected_cmd)}")
    
    @patch('publish_aliases.os.execv')
    @patch('builtins.print')
    def test_main_single_alias(self, mock_print, mock_execv):
        """Test main function with single alias."""
        single_alias = "single.local"
        with patch.object(sys, 'argv', ['script_name', single_alias]):
            publish_aliases.main()
            
            # Verify execv was called with correct arguments
            expected_cmd = ['/opt/venv/bin/mdns-publish-cname', single_alias]
            mock_execv.assert_called_once_with('/opt/venv/bin/mdns-publish-cname', expected_cmd)
            
            # Verify print statements
            mock_print.assert_any_call("Found 1 aliases to publish:")
            mock_print.assert_any_call(f"  - {single_alias}")
            mock_print.assert_any_call(f"Executing: {' '.join(expected_cmd)}")
    
    @patch('builtins.print')
    def test_main_no_aliases(self, mock_print):
        """Test main function when no aliases are found."""
        with patch.object(sys, 'argv', ['script_name', '']):
            with self.assertRaises(SystemExit) as cm:
                publish_aliases.main()
            
            self.assertEqual(cm.exception.code, 1)
            mock_print.assert_any_call("Error: Empty CSV string provided")
    
    @patch('publish_aliases.os.execv')
    @patch('builtins.print')
    def test_main_empty_aliases_filtered(self, mock_print, mock_execv):
        """Test main function filters out empty aliases correctly."""
        csv_string = "alias1.local,,alias2.local,,"
        expected_aliases = ["alias1.local", "alias2.local"]
        
        with patch.object(sys, 'argv', ['script_name', csv_string]):
            publish_aliases.main()
            
            # Verify execv was called with filtered aliases
            expected_cmd = ['/opt/venv/bin/mdns-publish-cname'] + expected_aliases
            mock_execv.assert_called_once_with('/opt/venv/bin/mdns-publish-cname', expected_cmd)
            
            # Verify print statements
            mock_print.assert_any_call("Found 2 aliases to publish:")
            for alias in expected_aliases:
                mock_print.assert_any_call(f"  - {alias}")
            mock_print.assert_any_call("Warning: Found empty alias entry, skipping...")
            mock_print.assert_any_call("Skipped 3 empty alias entries")


if __name__ == '__main__':
    unittest.main()