#!/usr/bin/env python3
"""
Tests for the publish_aliases module.
"""
import unittest
from unittest.mock import patch, MagicMock, call
import sys
import os
import signal
import subprocess

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
    
    @patch('publish_aliases.time.sleep')
    @patch('publish_aliases.subprocess.Popen')
    @patch('builtins.print')
    def test_main_success(self, mock_print, mock_popen, mock_sleep):
        """Test main function starts separate processes for each alias."""
        csv_string = ','.join(self.test_aliases)
        
        # Create mock processes that never exit (poll returns None)
        mock_processes = []
        for i in range(len(self.test_aliases)):
            mock_proc = MagicMock()
            mock_proc.pid = 1000 + i
            mock_proc.poll.return_value = None  # Still running
            mock_processes.append(mock_proc)
        
        mock_popen.side_effect = mock_processes
        
        # Make sleep raise an exception to break the monitoring loop
        mock_sleep.side_effect = KeyboardInterrupt()
        
        with patch.object(sys, 'argv', ['script_name', csv_string]):
            with patch('publish_aliases.signal.signal'):
                try:
                    publish_aliases.main()
                except (KeyboardInterrupt, SystemExit):
                    pass
            
            # Verify Popen was called once for each alias
            self.assertEqual(mock_popen.call_count, len(self.test_aliases))
            
            # Verify each alias got its own process
            expected_calls = [
                call(['/opt/venv/bin/mdns-publish-cname', alias])
                for alias in self.test_aliases
            ]
            mock_popen.assert_has_calls(expected_calls)
            
            # Verify print statements
            mock_print.assert_any_call(f"Found {len(self.test_aliases)} aliases to publish:")
            for alias in self.test_aliases:
                mock_print.assert_any_call(f"  - {alias}")
            mock_print.assert_any_call(f"Starting {len(self.test_aliases)} mdns-publish-cname processes in parallel...")
    
    @patch('publish_aliases.time.sleep')
    @patch('publish_aliases.subprocess.Popen')
    @patch('builtins.print')
    def test_main_single_alias(self, mock_print, mock_popen, mock_sleep):
        """Test main function with single alias."""
        single_alias = "single.local"
        
        # Create mock process
        mock_proc = MagicMock()
        mock_proc.pid = 1000
        mock_proc.poll.return_value = None
        mock_popen.return_value = mock_proc
        
        # Make sleep raise exception to break loop
        mock_sleep.side_effect = KeyboardInterrupt()
        
        with patch.object(sys, 'argv', ['script_name', single_alias]):
            with patch('publish_aliases.signal.signal'):
                try:
                    publish_aliases.main()
                except (KeyboardInterrupt, SystemExit):
                    pass
            
            # Verify Popen was called once
            mock_popen.assert_called_once_with(['/opt/venv/bin/mdns-publish-cname', single_alias])
            
            # Verify print statements
            mock_print.assert_any_call("Found 1 aliases to publish:")
            mock_print.assert_any_call(f"  - {single_alias}")
            mock_print.assert_any_call("Starting 1 mdns-publish-cname processes in parallel...")
    
    @patch('builtins.print')
    def test_main_no_aliases(self, mock_print):
        """Test main function when no aliases are found."""
        with patch.object(sys, 'argv', ['script_name', '']):
            with self.assertRaises(SystemExit) as cm:
                publish_aliases.main()
            
            self.assertEqual(cm.exception.code, 1)
            mock_print.assert_any_call("Error: Empty CSV string provided")
    
    @patch('publish_aliases.time.sleep')
    @patch('publish_aliases.subprocess.Popen')
    @patch('builtins.print')
    def test_main_empty_aliases_filtered(self, mock_print, mock_popen, mock_sleep):
        """Test main function filters out empty aliases correctly."""
        csv_string = "alias1.local,,alias2.local,,"
        expected_aliases = ["alias1.local", "alias2.local"]
        
        # Create mock processes
        mock_processes = []
        for i in range(len(expected_aliases)):
            mock_proc = MagicMock()
            mock_proc.pid = 1000 + i
            mock_proc.poll.return_value = None
            mock_processes.append(mock_proc)
        
        mock_popen.side_effect = mock_processes
        mock_sleep.side_effect = KeyboardInterrupt()
        
        with patch.object(sys, 'argv', ['script_name', csv_string]):
            with patch('publish_aliases.signal.signal'):
                try:
                    publish_aliases.main()
                except (KeyboardInterrupt, SystemExit):
                    pass
            
            # Verify Popen was called for each valid alias
            self.assertEqual(mock_popen.call_count, len(expected_aliases))
            expected_calls = [
                call(['/opt/venv/bin/mdns-publish-cname', alias])
                for alias in expected_aliases
            ]
            mock_popen.assert_has_calls(expected_calls)
            
            # Verify print statements
            mock_print.assert_any_call("Found 2 aliases to publish:")
            for alias in expected_aliases:
                mock_print.assert_any_call(f"  - {alias}")
            mock_print.assert_any_call("Warning: Found empty alias entry, skipping...")
            mock_print.assert_any_call("Skipped 3 empty alias entries")


    @patch('publish_aliases.time.sleep')
    @patch('publish_aliases.subprocess.Popen')
    @patch('builtins.print')
    def test_main_process_exits(self, mock_print, mock_popen, mock_sleep):
        """Test that when one process exits, all others are stopped and exit code is propagated."""
        csv_string = ','.join(self.test_aliases)
        
        # Create mock processes
        mock_processes = []
        for i in range(len(self.test_aliases)):
            mock_proc = MagicMock()
            mock_proc.pid = 1000 + i
            mock_processes.append(mock_proc)
        
        # Track how many times poll is called on first process
        poll_count = [0]
        def first_process_poll():
            poll_count[0] += 1
            if poll_count[0] == 1:
                return None  # First check: running
            else:
                return 1  # Second check: exited with code 1
        
        mock_processes[0].poll = first_process_poll
        mock_processes[0].terminate = MagicMock()
        mock_processes[0].wait = MagicMock()
        
        # Other processes are still running (always return None for poll)
        for i in range(1, len(self.test_aliases)):
            mock_processes[i].poll.return_value = None
            mock_processes[i].terminate = MagicMock()
            mock_processes[i].wait = MagicMock()
        
        mock_popen.side_effect = mock_processes
        
        with patch.object(sys, 'argv', ['script_name', csv_string]):
            with patch('publish_aliases.signal.signal'):
                with self.assertRaises(SystemExit) as cm:
                    publish_aliases.main()
                
                # Should exit with the same code as the failed process
                self.assertEqual(cm.exception.code, 1)
                
                # Verify other processes were terminated
                for i in range(1, len(self.test_aliases)):
                    mock_processes[i].terminate.assert_called()
    
    @patch('publish_aliases.subprocess.Popen')
    @patch('builtins.print')
    def test_main_sigterm_handler(self, mock_print, mock_popen):
        """Test that SIGTERM stops all child processes."""
        csv_string = ','.join(self.test_aliases)
        
        # Create mock processes
        mock_processes = []
        for i in range(len(self.test_aliases)):
            mock_proc = MagicMock()
            mock_proc.pid = 1000 + i
            mock_proc.poll.return_value = None
            mock_proc.terminate = MagicMock()
            mock_proc.wait = MagicMock()
            mock_processes.append(mock_proc)
        
        mock_popen.side_effect = mock_processes
        
        # Capture the signal handler
        captured_handlers = {}
        def capture_signal(signum, handler):
            captured_handlers[signum] = handler
        
        with patch.object(sys, 'argv', ['script_name', csv_string]):
            with patch('publish_aliases.signal.signal', side_effect=capture_signal):
                with patch('publish_aliases.time.sleep'):
                    # Start main in background by having sleep trigger the signal handler
                    def trigger_sigterm(*args):
                        # Trigger SIGTERM handler
                        if signal.SIGTERM in captured_handlers:
                            try:
                                captured_handlers[signal.SIGTERM](signal.SIGTERM, None)
                            except SystemExit:
                                raise
                    
                    with patch('publish_aliases.time.sleep', side_effect=trigger_sigterm):
                        with self.assertRaises(SystemExit) as cm:
                            publish_aliases.main()
                        
                        # Should exit with code 0
                        self.assertEqual(cm.exception.code, 0)
                        
                        # Verify all processes were terminated
                        for mock_proc in mock_processes:
                            mock_proc.terminate.assert_called()
    
    @patch('publish_aliases.subprocess.Popen')
    @patch('builtins.print')
    def test_main_sigint_handler(self, mock_print, mock_popen):
        """Test that SIGINT stops all child processes."""
        csv_string = ','.join(self.test_aliases)
        
        # Create mock processes
        mock_processes = []
        for i in range(len(self.test_aliases)):
            mock_proc = MagicMock()
            mock_proc.pid = 1000 + i
            mock_proc.poll.return_value = None
            mock_proc.terminate = MagicMock()
            mock_proc.wait = MagicMock()
            mock_processes.append(mock_proc)
        
        mock_popen.side_effect = mock_processes
        
        # Capture the signal handler
        captured_handlers = {}
        def capture_signal(signum, handler):
            captured_handlers[signum] = handler
        
        with patch.object(sys, 'argv', ['script_name', csv_string]):
            with patch('publish_aliases.signal.signal', side_effect=capture_signal):
                with patch('publish_aliases.time.sleep'):
                    def trigger_sigint(*args):
                        if signal.SIGINT in captured_handlers:
                            try:
                                captured_handlers[signal.SIGINT](signal.SIGINT, None)
                            except SystemExit:
                                raise
                    
                    with patch('publish_aliases.time.sleep', side_effect=trigger_sigint):
                        with self.assertRaises(SystemExit) as cm:
                            publish_aliases.main()
                        
                        # Should exit with code 0
                        self.assertEqual(cm.exception.code, 0)
                        
                        # Verify all processes were terminated
                        for mock_proc in mock_processes:
                            mock_proc.terminate.assert_called()
    
    @patch('publish_aliases.subprocess.Popen')
    @patch('builtins.print')
    def test_main_popen_failure(self, mock_print, mock_popen):
        """Test that if Popen fails, existing processes are stopped."""
        csv_string = ','.join(self.test_aliases)
        
        # First process succeeds, second fails
        mock_proc1 = MagicMock()
        mock_proc1.pid = 1000
        mock_proc1.poll.return_value = None
        mock_proc1.terminate = MagicMock()
        mock_proc1.wait = MagicMock()
        
        mock_popen.side_effect = [mock_proc1, Exception("Failed to start process")]
        
        with patch.object(sys, 'argv', ['script_name', csv_string]):
            with patch('publish_aliases.signal.signal'):
                with self.assertRaises(SystemExit) as cm:
                    publish_aliases.main()
                
                # Should exit with code 1
                self.assertEqual(cm.exception.code, 1)
                
                # First process should be terminated
                mock_proc1.terminate.assert_called()
    
    @patch('publish_aliases.time.sleep')
    @patch('publish_aliases.subprocess.Popen')
    @patch('builtins.print')
    def test_all_processes_run_concurrently(self, mock_print, mock_popen, mock_sleep):
        """Test that all processes are started before any monitoring happens."""
        csv_string = ','.join(self.test_aliases)
        
        # Track when Popen is called vs when poll is called
        popen_call_count = [0]
        first_poll_call = [None]
        
        def track_popen(*args):
            popen_call_count[0] += 1
            mock_proc = MagicMock()
            mock_proc.pid = 1000 + popen_call_count[0]
            
            def track_poll():
                if first_poll_call[0] is None:
                    first_poll_call[0] = popen_call_count[0]
                return None
            
            mock_proc.poll = track_poll
            return mock_proc
        
        mock_popen.side_effect = track_popen
        mock_sleep.side_effect = KeyboardInterrupt()
        
        with patch.object(sys, 'argv', ['script_name', csv_string]):
            with patch('publish_aliases.signal.signal'):
                try:
                    publish_aliases.main()
                except (KeyboardInterrupt, SystemExit):
                    pass
        
        # All processes should be created before monitoring starts
        # first_poll_call should equal total number of aliases (all started first)
        self.assertEqual(first_poll_call[0], len(self.test_aliases))
        self.assertEqual(popen_call_count[0], len(self.test_aliases))


if __name__ == '__main__':
    unittest.main()