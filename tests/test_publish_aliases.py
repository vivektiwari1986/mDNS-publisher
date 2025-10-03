#!/usr/bin/env python3
"""
Tests for the publish_aliases module.
"""
import unittest
from unittest.mock import patch, MagicMock, call
import sys
import os
from concurrent.futures import Future
from io import StringIO

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
    
    @patch('time.sleep')
    @patch('publish_aliases.publish_single_alias')
    @patch('publish_aliases.ThreadPoolExecutor')
    @patch('builtins.print')
    def test_main_success_all_aliases(self, mock_print, mock_executor_class, mock_publish, mock_sleep):
        """Test main function with all aliases succeeding."""
        # Mock successful results
        successful_results = [
            {'alias': 'alias1.local', 'success': True, 'output': 'Success 1', 'error': None},
            {'alias': 'alias2.local', 'success': True, 'output': 'Success 2', 'error': None},
            {'alias': 'alias3.local', 'success': True, 'output': 'Success 3', 'error': None}
        ]
        
        # Mock ThreadPoolExecutor
        mock_executor = MagicMock()
        mock_executor_class.return_value.__enter__.return_value = mock_executor
        
        # Mock futures
        mock_futures = []
        for i, result in enumerate(successful_results):
            future = MagicMock(spec=Future)
            future.result.return_value = result
            mock_futures.append(future)
        
        # Mock submit and as_completed
        mock_executor.submit.side_effect = mock_futures
        
        # Make sleep raise KeyboardInterrupt on first call to exit the infinite loop
        mock_sleep.side_effect = KeyboardInterrupt()
        
        with patch('publish_aliases.as_completed', return_value=mock_futures):
            csv_string = ','.join(self.test_aliases)
            with patch.object(sys, 'argv', ['script_name', csv_string]):
                with self.assertRaises(SystemExit) as cm:
                    publish_aliases.main()
                
                # Should exit with code 0 due to KeyboardInterrupt handling
                self.assertEqual(cm.exception.code, 0)
        
        # Verify executor was called correctly
        self.assertEqual(mock_executor.submit.call_count, len(self.test_aliases))
        
        # Verify print statements
        mock_print.assert_any_call(f"Found {len(self.test_aliases)} aliases to publish:")
        for alias in self.test_aliases:
            mock_print.assert_any_call(f"  - {alias}")
        mock_print.assert_any_call("\nStarting parallel alias publishing...")
        mock_print.assert_any_call("\n=== Alias Publishing Summary ===")
        mock_print.assert_any_call(f"Total aliases processed: {len(self.test_aliases)}")
        mock_print.assert_any_call(f"Successful: {len(successful_results)}")
        mock_print.assert_any_call("Failed: 0")
        mock_print.assert_any_call("\nReceived interrupt signal, shutting down...")
    
    @patch('time.sleep')
    @patch('publish_aliases.publish_single_alias')
    @patch('publish_aliases.ThreadPoolExecutor')
    @patch('builtins.print')
    def test_main_mixed_results(self, mock_print, mock_executor_class, mock_publish, mock_sleep):
        """Test main function with mixed success and failure results."""
        # Mock mixed results
        mixed_results = [
            {'alias': 'alias1.local', 'success': True, 'output': 'Success 1', 'error': None},
            {'alias': 'alias2.local', 'success': False, 'output': '', 'error': 'Failed to publish'},
            {'alias': 'alias3.local', 'success': True, 'output': 'Success 3', 'error': None}
        ]
        
        # Mock ThreadPoolExecutor
        mock_executor = MagicMock()
        mock_executor_class.return_value.__enter__.return_value = mock_executor
        
        # Mock futures
        mock_futures = []
        for i, result in enumerate(mixed_results):
            future = MagicMock(spec=Future)
            future.result.return_value = result
            mock_futures.append(future)
        
        # Mock submit and as_completed
        mock_executor.submit.side_effect = mock_futures
        
        # Make sleep raise KeyboardInterrupt on first call to exit the infinite loop
        mock_sleep.side_effect = KeyboardInterrupt()
        
        with patch('publish_aliases.as_completed', return_value=mock_futures):
            csv_string = ','.join(self.test_aliases)
            with patch.object(sys, 'argv', ['script_name', csv_string]):
                with self.assertRaises(SystemExit) as cm:
                    publish_aliases.main()
                
                # Should exit with code 0 due to KeyboardInterrupt handling
                self.assertEqual(cm.exception.code, 0)
        
        # Verify print statements include failed aliases
        mock_print.assert_any_call("Successful: 2")
        mock_print.assert_any_call("Failed: 1")
        mock_print.assert_any_call("\nFailed aliases:")
        mock_print.assert_any_call("  - alias2.local: Failed to publish")
        mock_print.assert_any_call("\nReceived interrupt signal, shutting down...")
    
    @patch('publish_aliases.publish_single_alias')
    @patch('publish_aliases.ThreadPoolExecutor')
    @patch('builtins.print')
    def test_main_all_failures(self, mock_print, mock_executor_class, mock_publish):
        """Test main function with all aliases failing."""
        # Mock all failed results
        failed_results = [
            {'alias': 'alias1.local', 'success': False, 'output': '', 'error': 'Error 1'},
            {'alias': 'alias2.local', 'success': False, 'output': '', 'error': 'Error 2'},
            {'alias': 'alias3.local', 'success': False, 'output': '', 'error': 'Error 3'}
        ]
        
        # Mock ThreadPoolExecutor
        mock_executor = MagicMock()
        mock_executor_class.return_value.__enter__.return_value = mock_executor
        
        # Mock futures
        mock_futures = []
        for i, result in enumerate(failed_results):
            future = MagicMock(spec=Future)
            future.result.return_value = result
            mock_futures.append(future)
        
        # Mock submit and as_completed
        mock_executor.submit.side_effect = mock_futures
        
        with patch('publish_aliases.as_completed', return_value=mock_futures):
            csv_string = ','.join(self.test_aliases)
            with patch.object(sys, 'argv', ['script_name', csv_string]):
                with self.assertRaises(SystemExit) as cm:
                    publish_aliases.main()
                
                self.assertEqual(cm.exception.code, 1)
        
        # Verify print statements
        mock_print.assert_any_call("Successful: 0")
        mock_print.assert_any_call("Failed: 3")
        mock_print.assert_any_call("\nError: All alias publishing attempts failed")
    
    @patch('time.sleep')
    @patch('publish_aliases.ThreadPoolExecutor')
    @patch('builtins.print')
    def test_main_future_exception(self, mock_print, mock_executor_class, mock_sleep):
        """Test main function when a future raises an exception."""
        # Mock ThreadPoolExecutor
        mock_executor = MagicMock()
        mock_executor_class.return_value.__enter__.return_value = mock_executor
        
        # Mock futures - one successful, one with exception
        future1 = MagicMock(spec=Future)
        future1.result.return_value = {'alias': 'alias1.local', 'success': True, 'output': 'Success 1', 'error': None}
        
        future2 = MagicMock(spec=Future)
        future2.result.side_effect = Exception("Future exception")
        
        mock_futures = [future1, future2]
        mock_executor.submit.side_effect = mock_futures
        
        # Make sleep raise KeyboardInterrupt on first call to exit the infinite loop
        mock_sleep.side_effect = KeyboardInterrupt()
        
        with patch('publish_aliases.as_completed', return_value=mock_futures):
            with patch.object(sys, 'argv', ['script_name', 'alias1.local,alias2.local']):
                with self.assertRaises(SystemExit) as cm:
                    publish_aliases.main()
                
                # Should exit with code 0 due to KeyboardInterrupt handling
                self.assertEqual(cm.exception.code, 0)
        
        # Verify exception handling print statement
        mock_print.assert_any_call("EXCEPTION: alias2.local generated an exception: Future exception")
        mock_print.assert_any_call("\nReceived interrupt signal, shutting down...")
    
    @patch('time.sleep')
    @patch('publish_aliases.ThreadPoolExecutor')
    @patch('builtins.print')
    def test_main_keyboard_interrupt(self, mock_print, mock_executor_class, mock_sleep):
        """Test main function handles KeyboardInterrupt gracefully."""
        # Mock ThreadPoolExecutor
        mock_executor = MagicMock()
        mock_executor_class.return_value.__enter__.return_value = mock_executor
        
        # Mock successful results to reach the sleep loop
        successful_results = [
            {'alias': alias, 'success': True, 'output': f'Success {alias}', 'error': None}
            for alias in self.test_aliases
        ]
        
        mock_futures = []
        for result in successful_results:
            future = MagicMock(spec=Future)
            future.result.return_value = result
            mock_futures.append(future)
        
        mock_executor.submit.side_effect = mock_futures
        
        # Mock sleep to raise KeyboardInterrupt
        mock_sleep.side_effect = KeyboardInterrupt()
        
        with patch('publish_aliases.as_completed', return_value=mock_futures):
            csv_string = ','.join(self.test_aliases)
            with patch.object(sys, 'argv', ['script_name', csv_string]):
                with self.assertRaises(SystemExit) as cm:
                    publish_aliases.main()
                
                self.assertEqual(cm.exception.code, 0)
                mock_print.assert_any_call("\nReceived interrupt signal, shutting down...")


if __name__ == '__main__':
    unittest.main()