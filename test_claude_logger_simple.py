#!/usr/bin/env python3
"""
Simplified unit tests for claude_logger_enhanced.py
"""
import unittest
import tempfile
import shutil
import json
import os
from pathlib import Path
import subprocess
from unittest.mock import patch, MagicMock


class TestClaudeLoggerSimple(unittest.TestCase):
    """Simplified tests that don't require complex mocking"""
    
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
        from claude_logger_enhanced import ClaudeLogger
        
        # Test that class exists and has expected methods
        self.assertTrue(hasattr(ClaudeLogger, 'load_metadata'))
        self.assertTrue(hasattr(ClaudeLogger, 'save_metadata'))
        self.assertTrue(hasattr(ClaudeLogger, 'create_session_log'))
        self.assertTrue(hasattr(ClaudeLogger, 'get_creative_energy'))
    
    def test_metadata_operations_real(self):
        """Test metadata loading and saving with real files"""
        from claude_logger_enhanced import ClaudeLogger
        
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
        from claude_logger_enhanced import ClaudeLogger
        
        logger = ClaudeLogger()
        energy = logger.get_creative_energy()
        
        self.assertEqual(energy, 2)
        self.assertTrue(mock_print.called)  # Verify prompt was displayed
    
    @patch('subprocess.run')
    def test_git_operations_mocked(self, mock_subprocess):
        """Test git operations with subprocess mocked"""
        from claude_logger_enhanced import ClaudeLogger
        
        # Mock successful subprocess calls
        mock_subprocess.return_value = MagicMock(returncode=0, stdout="abc123\n")
        
        logger = ClaudeLogger()
        
        # Test git commit (this will use mocked subprocess)
        session_info = {
            "id": "test123",
            "project": "test",
            "methodology": "context-driven",
            "command": "claude test",
            "duration": 60
        }
        
        log_file = MagicMock()
        log_file.name = "test.log"
        
        commit_hash = logger.git_commit_session(session_info, log_file)
        
        # Verify subprocess was called for git operations
        self.assertTrue(mock_subprocess.called)
        self.assertEqual(commit_hash, "abc123")


class TestSessionAnalyzerSimple(unittest.TestCase):
    """Simplified tests for session analyzer"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.original_home = os.environ.get('HOME')
        os.environ['HOME'] = self.test_dir
        
    def tearDown(self):
        """Clean up test environment"""
        if self.original_home:
            os.environ['HOME'] = self.original_home
        else:
            del os.environ['HOME']
        shutil.rmtree(self.test_dir)
    
    def test_import_and_structure(self):
        """Test that session analyzer imports and has expected structure"""
        from session_analyzer import SessionAnalyzer
        
        self.assertTrue(hasattr(SessionAnalyzer, 'analyze_log_file'))
        self.assertTrue(hasattr(SessionAnalyzer, 'compare_methodologies'))
        self.assertTrue(hasattr(SessionAnalyzer, 'generate_report'))
    
    def test_pattern_analysis_real_file(self):
        """Test pattern analysis with a real temporary file"""
        from session_analyzer import SessionAnalyzer
        
        # Create analyzer (will use our test HOME)
        analyzer = SessionAnalyzer()
        
        # Create a test log file with known patterns
        logs_dir = Path(self.test_dir) / ".claude-logs"
        logs_dir.mkdir(exist_ok=True)
        
        test_content = """Human: Can you help me?
        Assistant: Excellent! I'd love to help.
        
        ```python
        def hello():
            return "world"
        ```
        
        Human: That's not quite right?
        Assistant: Let me clarify - as we discussed before, you wanted something different.
        """
        
        test_log = logs_dir / "test.log"
        with open(test_log, 'w') as f:
            f.write(test_content)
        
        # Analyze the file
        metrics = analyzer.analyze_log_file(test_log)
        
        # Verify basic pattern detection
        self.assertGreater(metrics["exchanges"], 0)  # Should find Human: entries
        self.assertGreater(metrics["code_blocks"], 0)  # Should find ``` markers
        self.assertGreater(metrics["enthusiasm_markers"], 0)  # Should find "Excellent!"
        self.assertGreater(metrics["confusion_markers"], 0)  # Should find "That's not"
        self.assertGreater(metrics["compaction_indicators"], 0)  # Should find "as we discussed"
    
    @patch('builtins.print')
    def test_generate_report_with_data(self, mock_print):
        """Test report generation with some sample data"""
        from session_analyzer import SessionAnalyzer
        
        # Create analyzer
        analyzer = SessionAnalyzer()
        
        # Create sample metadata
        logs_dir = Path(self.test_dir) / ".claude-logs"
        logs_dir.mkdir(exist_ok=True)
        
        sample_sessions = {
            "sessions": [
                {
                    "id": "test1",
                    "methodology": "context-driven", 
                    "duration": 120,
                    "creative_energy": 3,
                    "log_file": str(logs_dir / "test1.log")
                }
            ]
        }
        
        # Save metadata
        with open(logs_dir / "sessions_metadata.json", 'w') as f:
            json.dump(sample_sessions, f)
        
        # Create a simple log file
        with open(logs_dir / "test1.log", 'w') as f:
            f.write("Human: Test\nAssistant: Great!\n")
        
        # Generate report
        analyzer.generate_report()
        
        # Verify print was called (report was generated)
        self.assertTrue(mock_print.called)


if __name__ == '__main__':
    unittest.main(verbosity=2)