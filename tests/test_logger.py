#!/usr/bin/env python3
"""
Consolidated unit tests for claude_logger module
"""
import unittest
import tempfile
import shutil
import json
import os
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open

# Import from the new package structure
from claude_logger.logger import ClaudeLogger


class TestClaudeLogger(unittest.TestCase):
    """Test cases for ClaudeLogger class"""
    
    def setUp(self):
        """Set up test environment with temporary directory"""
        self.test_dir = tempfile.mkdtemp()
        self.test_logs_dir = Path(self.test_dir) / ".claude-logs"
        self.test_logs_dir.mkdir(exist_ok=True)
        
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.test_dir)
    
    def _create_test_logger(self):
        """Create a logger with test directory setup"""
        with patch('claude_logger.logger.Path.home', return_value=Path(self.test_dir)):
            logger = ClaudeLogger()
            return logger
    
    def test_load_metadata_new_file(self):
        """Test loading metadata when file doesn't exist"""
        logger = self._create_test_logger()
        self.assertEqual(logger.metadata, {"sessions": []})
    
    def test_load_metadata_existing_file(self):
        """Test loading metadata from existing file"""
        # Create metadata file first
        test_metadata = {"sessions": [{"id": "test123", "project": "test"}]}
        metadata_file = self.test_logs_dir / "sessions_metadata.json"
        with open(metadata_file, 'w') as f:
            json.dump(test_metadata, f)
        
        logger = self._create_test_logger()
        self.assertEqual(logger.metadata, test_metadata)
    
    def test_save_metadata(self):
        """Test saving metadata to file"""
        logger = self._create_test_logger()
        logger.metadata = {"sessions": [{"id": "test456", "project": "example"}]}
        logger.save_metadata()
        
        # Verify file was written correctly
        with open(logger.metadata_file, 'r') as f:
            saved_data = json.load(f)
        
        self.assertEqual(saved_data, logger.metadata)
    
    @patch('subprocess.run')
    def test_init_git_repo_new(self, mock_subprocess):
        """Test git repository initialization for new directory"""
        # Mock successful git operations
        mock_subprocess.return_value = MagicMock(returncode=0)
        
        logger = self._create_test_logger()
        
        # Verify git commands were called
        expected_calls = [
            unittest.mock.call(["git", "init"], cwd=logger.logs_dir, capture_output=True),
            unittest.mock.call(["git", "add", "."], cwd=logger.logs_dir, capture_output=True),
            unittest.mock.call(["git", "commit", "-m", "Initialize Claude conversation logs"], 
                             cwd=logger.logs_dir, capture_output=True)
        ]
        
        mock_subprocess.assert_has_calls(expected_calls)
        
        # Verify .gitignore was created
        gitignore = logger.logs_dir / ".gitignore"
        self.assertTrue(gitignore.exists())
    
    @patch('subprocess.run')
    def test_git_commit_session(self, mock_subprocess):
        """Test git commit of session with metadata"""
        logger = self._create_test_logger()
        
        # Mock successful git operations
        mock_subprocess.side_effect = [
            # git add
            MagicMock(returncode=0),
            # git commit  
            MagicMock(returncode=0),
            # git rev-parse
            MagicMock(returncode=0, stdout="abc1234\n")
        ]
        
        session_info = {
            "id": "20240724_143000",
            "project": "test-project",
            "methodology": "context-driven",
            "command": "claude test",
            "duration": 120,
            "creative_energy": 3
        }
        
        log_file = MagicMock()
        log_file.name = "test.log"
        
        result = logger.git_commit_session(session_info, log_file)
        
        # Verify return value (should strip newline)
        self.assertEqual(result, "abc1234")
        
        # Verify git commands were called correctly (at least the commit ones)
        commit_calls = [call for call in mock_subprocess.call_args_list 
                       if call[0][0] and "commit" in call[0][0]]
        self.assertGreater(len(commit_calls), 0)
    
    def test_get_creative_energy_valid_input(self):
        """Test creative energy input with valid values"""
        logger = self._create_test_logger()
        
        with patch('builtins.input', return_value='2'):
            with patch('builtins.print'):  # Suppress output
                energy = logger.get_creative_energy()
                self.assertEqual(energy, 2)
    
    def test_get_creative_energy_invalid_then_valid(self):
        """Test creative energy input with invalid then valid input"""
        logger = self._create_test_logger()
        
        with patch('builtins.input', side_effect=['4', 'invalid', '1']):
            with patch('builtins.print'):  # Suppress print output
                energy = logger.get_creative_energy()
                self.assertEqual(energy, 1)
    
    def test_get_creative_energy_keyboard_interrupt(self):
        """Test creative energy input with keyboard interrupt"""
        logger = self._create_test_logger()
        
        with patch('builtins.input', side_effect=KeyboardInterrupt()):
            with patch('builtins.print'):  # Suppress print output
                energy = logger.get_creative_energy()
                self.assertIsNone(energy)


class TestClaudeLoggerIntegration(unittest.TestCase):
    """Integration tests using real file operations"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.original_home = os.environ.get('HOME')
        # Temporarily set HOME to our test directory
        os.environ['HOME'] = self.test_dir
        
    def tearDown(self):
        """Clean up test environment"""
        # Restore original HOME
        if self.original_home:
            os.environ['HOME'] = self.original_home
        else:
            del os.environ['HOME']
        shutil.rmtree(self.test_dir)
    
    def test_import_and_basic_structure(self):
        """Test that the module imports correctly and has expected structure"""
        # Test that class exists and has expected methods
        self.assertTrue(hasattr(ClaudeLogger, 'load_metadata'))
        self.assertTrue(hasattr(ClaudeLogger, 'save_metadata'))
        self.assertTrue(hasattr(ClaudeLogger, 'create_session_log'))
        self.assertTrue(hasattr(ClaudeLogger, 'get_creative_energy'))
    
    def test_metadata_operations_real(self):
        """Test metadata loading and saving with real files"""
        # Create logger (will create .claude-logs in our test HOME)
        logger = ClaudeLogger()
        
        # Test initial empty metadata
        self.assertEqual(logger.metadata, {"sessions": []})
        
        # Add some test session data
        test_session = {
            "id": "test123",
            "project": "test-project",
            "methodology": "context-driven"
        }
        logger.metadata["sessions"].append(test_session)
        
        # Save metadata
        logger.save_metadata()
        
        # Create new logger instance and verify it loads the saved data
        logger2 = ClaudeLogger()
        self.assertEqual(len(logger2.metadata["sessions"]), 1)
        self.assertEqual(logger2.metadata["sessions"][0]["id"], "test123")
    
    @patch('builtins.input', return_value='2')
    @patch('builtins.print')
    def test_creative_energy_input(self, mock_print, mock_input):
        """Test creative energy input with mocked input"""
        logger = ClaudeLogger()
        energy = logger.get_creative_energy()
        
        self.assertEqual(energy, 2)
        self.assertTrue(mock_print.called)  # Verify prompt was displayed


if __name__ == '__main__':
    unittest.main(verbosity=2)