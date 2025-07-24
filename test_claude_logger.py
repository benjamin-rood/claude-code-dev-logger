#!/usr/bin/env python3
"""
Unit tests for claude_logger_enhanced.py
"""
import unittest
import tempfile
import shutil
import json
import os
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open
from claude_logger_enhanced import ClaudeLogger
import subprocess


class TestClaudeLogger(unittest.TestCase):
    
    def setUp(self):
        """Set up test environment with temporary directory"""
        self.test_dir = tempfile.mkdtemp()
        self.test_logs_dir = Path(self.test_dir) / ".claude-logs"
        
        # Patch the logs directory to use our test directory
        self.logs_dir_patcher = patch.object(ClaudeLogger, '__init__')
        self.mock_init = self.logs_dir_patcher.start()
        
        def mock_logger_init(logger_self):
            logger_self.logs_dir = self.test_logs_dir
            logger_self.logs_dir.mkdir(exist_ok=True)
            logger_self.metadata_file = logger_self.logs_dir / "sessions_metadata.json"
            logger_self.load_metadata()
            # Don't actually init git in tests
        
        self.mock_init.side_effect = mock_logger_init
        
    def tearDown(self):
        """Clean up test environment"""
        self.logs_dir_patcher.stop()
        shutil.rmtree(self.test_dir)
    
    def test_load_metadata_new_file(self):
        """Test loading metadata when file doesn't exist"""
        logger = ClaudeLogger()
        self.assertEqual(logger.metadata, {"sessions": []})
    
    def test_load_metadata_existing_file(self):
        """Test loading metadata from existing file"""
        # Create metadata file
        test_metadata = {"sessions": [{"id": "test123", "project": "test"}]}
        with open(self.test_logs_dir / "sessions_metadata.json", 'w') as f:
            json.dump(test_metadata, f)
        
        logger = ClaudeLogger()
        self.assertEqual(logger.metadata, test_metadata)
    
    def test_save_metadata(self):
        """Test saving metadata to file"""
        logger = ClaudeLogger()
        logger.metadata = {"sessions": [{"id": "test456", "project": "example"}]}
        logger.save_metadata()
        
        # Verify file was written correctly
        with open(logger.metadata_file, 'r') as f:
            saved_data = json.load(f)
        
        self.assertEqual(saved_data, logger.metadata)
    
    @patch('subprocess.run')
    def test_init_git_repo_new(self, mock_subprocess):
        """Test git repository initialization for new directory"""
        # Ensure no .git directory exists
        git_dir = self.test_logs_dir / ".git"
        self.assertFalse(git_dir.exists())
        
        logger = ClaudeLogger()
        logger.init_git_repo()
        
        # Verify git commands were called
        expected_calls = [
            unittest.mock.call(["git", "init"], cwd=self.test_logs_dir, capture_output=True),
            unittest.mock.call(["git", "add", "."], cwd=self.test_logs_dir, capture_output=True),
            unittest.mock.call(["git", "commit", "-m", "Initialize Claude conversation logs"], 
                             cwd=self.test_logs_dir, capture_output=True)
        ]
        
        mock_subprocess.assert_has_calls(expected_calls)
        
        # Verify .gitignore was created
        gitignore = self.test_logs_dir / ".gitignore"
        self.assertTrue(gitignore.exists())
    
    @patch('subprocess.run')
    def test_init_git_repo_existing(self, mock_subprocess):
        """Test git repository initialization when .git already exists"""
        # Create .git directory
        git_dir = self.test_logs_dir / ".git"
        git_dir.mkdir()
        
        logger = ClaudeLogger()
        logger.init_git_repo()
        
        # Verify git commands were NOT called
        mock_subprocess.assert_not_called()
    
    @patch('subprocess.run')
    def test_git_commit_session(self, mock_subprocess):
        """Test git commit of session with metadata"""
        logger = ClaudeLogger()
        
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
        
        # Verify return value
        self.assertEqual(result, "abc1234")
        
        # Verify git commands were called correctly
        self.assertEqual(mock_subprocess.call_count, 3)
    
    @patch('claude_logger_enhanced.Path.cwd')
    def test_create_session_log_no_methodology_file(self, mock_cwd):
        """Test session log creation when no methodology file exists"""
        # Mock current working directory
        mock_project_dir = MagicMock()
        mock_project_dir.name = "test-project"
        mock_project_dir.__truediv__ = lambda self, other: MagicMock(exists=lambda: False)
        mock_cwd.return_value = mock_project_dir
        
        logger = ClaudeLogger()
        
        # Mock args
        args = MagicMock()
        args.claude_args = ["test", "command"]
        
        with patch('claude_logger_enhanced.datetime') as mock_datetime:
            mock_datetime.now.return_value.strftime.return_value = "20240724_143000"
            mock_datetime.now.return_value.isoformat.return_value = "2024-07-24T14:30:00"
            
            log_file, session_info = logger.create_session_log(args)
            
            # Verify methodology detection
            self.assertEqual(session_info["methodology"], "unknown")
            self.assertEqual(session_info["project"], "test-project")
            self.assertEqual(session_info["command"], "claude test command")
    
    @patch('claude_logger_enhanced.Path.cwd')
    def test_create_session_log_with_context_driven(self, mock_cwd):
        """Test session log creation with context-driven methodology"""
        # Mock current working directory and CLAUDE.md file
        mock_project_dir = MagicMock()
        mock_project_dir.name = "test-project"
        
        # Mock the .claude/CLAUDE.md file existence and content
        claude_md_path = MagicMock()
        claude_md_path.exists.return_value = True
        mock_project_dir.__truediv__.return_value = claude_md_path
        
        mock_cwd.return_value = mock_project_dir
        
        logger = ClaudeLogger()
        
        args = MagicMock()
        args.claude_args = ["test"]
        
        # Mock file reading
        with patch('builtins.open', mock_open(read_data="# Context-Driven Spec Development\n")):
            with patch('claude_logger_enhanced.datetime') as mock_datetime:
                mock_datetime.now.return_value.strftime.return_value = "20240724_143000"
                mock_datetime.now.return_value.isoformat.return_value = "2024-07-24T14:30:00"
                
                log_file, session_info = logger.create_session_log(args)
                
                self.assertEqual(session_info["methodology"], "context-driven")
    
    def test_get_creative_energy_valid_input(self):
        """Test creative energy input with valid values"""
        logger = ClaudeLogger()
        
        with patch('builtins.input', side_effect=['2']):
            energy = logger.get_creative_energy()
            self.assertEqual(energy, 2)
    
    def test_get_creative_energy_invalid_then_valid(self):
        """Test creative energy input with invalid then valid input"""
        logger = ClaudeLogger()
        
        with patch('builtins.input', side_effect=['4', 'invalid', '1']):
            with patch('builtins.print'):  # Suppress print output
                energy = logger.get_creative_energy()
                self.assertEqual(energy, 1)
    
    def test_get_creative_energy_keyboard_interrupt(self):
        """Test creative energy input with keyboard interrupt"""
        logger = ClaudeLogger()
        
        with patch('builtins.input', side_effect=KeyboardInterrupt()):
            with patch('builtins.print'):  # Suppress print output
                energy = logger.get_creative_energy()
                self.assertIsNone(energy)


class TestClaudeLoggerIntegration(unittest.TestCase):
    """Integration tests for the complete logging workflow"""
    
    def setUp(self):
        """Set up integration test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.test_logs_dir = Path(self.test_dir) / ".claude-logs"
        self.test_project_dir = Path(self.test_dir) / "test-project"
        self.test_project_dir.mkdir()
        
        # Create a mock .claude/CLAUDE.md file
        claude_dir = self.test_project_dir / ".claude"
        claude_dir.mkdir()
        with open(claude_dir / "CLAUDE.md", 'w') as f:
            f.write("# Context-Driven Spec Development\nTest methodology")
    
    def tearDown(self):
        """Clean up integration test environment"""  
        shutil.rmtree(self.test_dir)
    
    @patch('subprocess.run')
    @patch('claude_logger_enhanced.Path.cwd')
    def test_full_logging_workflow(self, mock_cwd, mock_subprocess):
        """Test the complete logging workflow from start to finish"""
        # Set up mocks
        mock_cwd.return_value = self.test_project_dir
        
        # Mock subprocess calls for git operations
        mock_subprocess.side_effect = [
            # git init
            MagicMock(returncode=0),
            # git add . (for initial setup)
            MagicMock(returncode=0), 
            # git commit (for initial setup)
            MagicMock(returncode=0),
            # script command (simulating claude execution)
            MagicMock(returncode=0),
            # git add (for session commit)
            MagicMock(returncode=0),
            # git commit (for session)
            MagicMock(returncode=0),
            # git rev-parse
            MagicMock(returncode=0, stdout="abc1234\n")
        ]
        
        # Patch ClaudeLogger init to use our test directory
        with patch.object(ClaudeLogger, '__init__') as mock_init:
            def custom_init(logger_self):
                logger_self.logs_dir = self.test_logs_dir
                logger_self.logs_dir.mkdir(exist_ok=True)
                logger_self.metadata_file = logger_self.logs_dir / "sessions_metadata.json"
                logger_self.load_metadata()
                logger_self.init_git_repo()
            
            mock_init.side_effect = custom_init
            
            # Create logger and mock args
            logger = ClaudeLogger()
            args = MagicMock()
            args.claude_args = ["test", "command"]
            args.track_energy = False
            
            # Mock datetime for consistent timestamps
            with patch('claude_logger_enhanced.datetime') as mock_datetime:
                start_time = MagicMock()
                end_time = MagicMock()
                start_time.strftime.return_value = "20240724_143000"
                start_time.isoformat.return_value = "2024-07-24T14:30:00"
                end_time.isoformat.return_value = "2024-07-24T14:32:00"
                
                mock_datetime.now.side_effect = [start_time, start_time, end_time]
                # Mock time difference
                mock_datetime.now.return_value.__sub__.return_value.total_seconds.return_value = 120
                
                # Mock sys.exit to prevent test from actually exiting
                with patch('sys.exit') as mock_exit:
                    logger.run_logged_session(args)
                    
                    # Verify session was logged
                    self.assertEqual(len(logger.metadata["sessions"]), 1)
                    session = logger.metadata["sessions"][0]
                    self.assertEqual(session["methodology"], "context-driven")
                    self.assertEqual(session["project"], "test-project")
                    
                    # Verify sys.exit was called
                    mock_exit.assert_called_once_with(0)


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)