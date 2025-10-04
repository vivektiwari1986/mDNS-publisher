#!/usr/bin/env python3
"""
Tests for the mdns_publisher module.
"""
import unittest
from unittest.mock import patch, MagicMock
import subprocess
import sys
import os

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from mdns_publisher import publish_single_alias


class TestMdnsPublisher(unittest.TestCase):
    """Test cases for the mdns_publisher module."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_alias = "test-alias.local"
        self.test_mdns_path = "/opt/venv/bin/mdns-publish-cname"
        self.test_timeout = 120
    
    @patch('mdns_publisher.subprocess.run')
    @patch('builtins.print')
    def test_publish_single_alias_success(self, mock_print, mock_subprocess):
        """Test successful alias publishing."""
        # Mock successful subprocess result
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Published successfully"
        mock_result.stderr = ""
        mock_subprocess.return_value = mock_result
        
        # Call the function
        result = publish_single_alias(self.test_alias)
        
        # Verify subprocess was called correctly
        mock_subprocess.assert_called_once_with(
            [self.test_mdns_path, self.test_alias],
            capture_output=True,
            text=True,
            timeout=self.test_timeout
        )
        
        # Verify result
        expected_result = {
            'alias': self.test_alias,
            'success': True,
            'output': "Published successfully",
            'error': None
        }
        self.assertEqual(result, expected_result)
        
        # Verify print statements
        mock_print.assert_any_call(f"Starting mDNS publishing for alias: {self.test_alias}")
        mock_print.assert_any_call(f"SUCCESS: {self.test_alias} published successfully")
    
    @patch('mdns_publisher.subprocess.run')
    @patch('builtins.print')
    def test_publish_single_alias_with_non_zero_exit_code(self, mock_print, mock_subprocess):
        """Test alias publishing with non-zero exit code (still treated as success)."""
        # Mock subprocess result with non-zero exit code
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = ""
        mock_result.stderr = "Publishing failed"
        mock_subprocess.return_value = mock_result
        
        # Call the function
        result = publish_single_alias(self.test_alias)
        
        # Verify result - should still be success
        expected_result = {
            'alias': self.test_alias,
            'success': True,
            'output': "",
            'error': None
        }
        self.assertEqual(result, expected_result)
        
        # Verify print statements
        mock_print.assert_any_call(f"Starting mDNS publishing for alias: {self.test_alias}")
        mock_print.assert_any_call(f"SUCCESS: {self.test_alias} published successfully")
        mock_print.assert_any_call(f"  Stderr: {mock_result.stderr.strip()}")
    
    @patch('mdns_publisher.subprocess.run')
    @patch('builtins.print')
    def test_publish_single_alias_timeout(self, mock_print, mock_subprocess):
        """Test alias publishing timeout."""
        # Mock timeout exception
        mock_subprocess.side_effect = subprocess.TimeoutExpired(
            cmd=[self.test_mdns_path, self.test_alias],
            timeout=self.test_timeout
        )
        
        # Call the function
        result = publish_single_alias(self.test_alias)
        
        # Verify result
        expected_result = {
            'alias': self.test_alias,
            'success': False,
            'output': '',
            'error': f'Timeout after {self.test_timeout} seconds'
        }
        self.assertEqual(result, expected_result)
        
        # Verify print statements
        mock_print.assert_any_call(f"Starting mDNS publishing for alias: {self.test_alias}")
        mock_print.assert_any_call(f"TIMEOUT: {self.test_alias} publishing timed out after {self.test_timeout} seconds")
    
    @patch('mdns_publisher.subprocess.run')
    @patch('builtins.print')
    def test_publish_single_alias_exception(self, mock_print, mock_subprocess):
        """Test alias publishing with general exception."""
        # Mock general exception
        test_exception = Exception("Test exception")
        mock_subprocess.side_effect = test_exception
        
        # Call the function
        result = publish_single_alias(self.test_alias)
        
        # Verify result
        expected_result = {
            'alias': self.test_alias,
            'success': False,
            'output': '',
            'error': 'Test exception'
        }
        self.assertEqual(result, expected_result)
        
        # Verify print statements
        mock_print.assert_any_call(f"Starting mDNS publishing for alias: {self.test_alias}")
        mock_print.assert_any_call(f"EXCEPTION: {self.test_alias} publishing failed with exception: Test exception")
    
    @patch('mdns_publisher.subprocess.run')
    @patch('builtins.print')
    def test_publish_single_alias_custom_parameters(self, mock_print, mock_subprocess):
        """Test alias publishing with custom parameters."""
        # Mock successful subprocess result
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Custom success"
        mock_result.stderr = ""
        mock_subprocess.return_value = mock_result
        
        custom_path = "/custom/path/mdns-publish-cname"
        custom_timeout = 60
        
        # Call the function with custom parameters
        result = publish_single_alias(
            self.test_alias,
            mdns_publish_path=custom_path,
            timeout=custom_timeout
        )
        
        # Verify subprocess was called with custom parameters
        mock_subprocess.assert_called_once_with(
            [custom_path, self.test_alias],
            capture_output=True,
            text=True,
            timeout=custom_timeout
        )
        
        # Verify result
        expected_result = {
            'alias': self.test_alias,
            'success': True,
            'output': "Custom success",
            'error': None
        }
        self.assertEqual(result, expected_result)
    
    @patch('mdns_publisher.subprocess.run')
    @patch('builtins.print')
    def test_publish_single_alias_with_output_and_stderr(self, mock_print, mock_subprocess):
        """Test alias publishing with both stdout and stderr output."""
        # Mock subprocess result with both stdout and stderr
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Detailed output message\nMultiple lines"
        mock_result.stderr = "Some warning message"
        mock_subprocess.return_value = mock_result
        
        # Call the function
        result = publish_single_alias(self.test_alias)
        
        # Verify print statements include both output and stderr
        mock_print.assert_any_call(f"SUCCESS: {self.test_alias} published successfully")
        mock_print.assert_any_call(f"  Output: {mock_result.stdout.strip()}")
        mock_print.assert_any_call(f"  Stderr: {mock_result.stderr.strip()}")
        
        # Verify result includes output but error is None
        expected_result = {
            'alias': self.test_alias,
            'success': True,
            'output': mock_result.stdout,
            'error': None
        }
        self.assertEqual(result, expected_result)
    
    @patch('mdns_publisher.subprocess.run')
    @patch('builtins.print')
    def test_publish_single_alias_with_stderr(self, mock_print, mock_subprocess):
        """Test alias publishing with stderr output (still treated as success)."""
        # Mock subprocess result with stderr
        mock_result = MagicMock()
        mock_result.returncode = 2
        mock_result.stdout = ""
        mock_result.stderr = "Detailed error message\nMultiple error lines"
        mock_subprocess.return_value = mock_result
        
        # Call the function
        result = publish_single_alias(self.test_alias)
        
        # Verify print statements include stderr
        mock_print.assert_any_call(f"SUCCESS: {self.test_alias} published successfully")
        mock_print.assert_any_call(f"  Stderr: {mock_result.stderr.strip()}")
        
        # Verify result is still success with no error
        expected_result = {
            'alias': self.test_alias,
            'success': True,
            'output': "",
            'error': None
        }
        self.assertEqual(result, expected_result)


if __name__ == '__main__':
    unittest.main()