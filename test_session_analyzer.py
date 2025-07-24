#!/usr/bin/env python3
"""
Unit tests for session_analyzer.py
"""
import unittest
import tempfile
import shutil
import json
from pathlib import Path
from unittest.mock import patch, mock_open
from session_analyzer import SessionAnalyzer


class TestSessionAnalyzer(unittest.TestCase):
    
    def setUp(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.test_logs_dir = Path(self.test_dir) / ".claude-logs"
        self.test_logs_dir.mkdir()
        
        # Patch the logs directory
        self.logs_dir_patcher = patch.object(SessionAnalyzer, '__init__')
        self.mock_init = self.logs_dir_patcher.start()
        
        def mock_analyzer_init(analyzer_self):
            analyzer_self.logs_dir = self.test_logs_dir
            analyzer_self.metadata_file = analyzer_self.logs_dir / "sessions_metadata.json"
            analyzer_self.load_metadata()
        
        self.mock_init.side_effect = mock_analyzer_init
        
    def tearDown(self):
        """Clean up test environment"""
        self.logs_dir_patcher.stop()
        shutil.rmtree(self.test_dir)
    
    def test_load_metadata_empty(self):
        """Test loading metadata when file doesn't exist"""
        analyzer = SessionAnalyzer()
        self.assertEqual(analyzer.metadata, {"sessions": []})
    
    def test_load_metadata_with_data(self):
        """Test loading metadata from existing file"""
        test_data = {
            "sessions": [
                {"id": "test1", "methodology": "context-driven"},
                {"id": "test2", "methodology": "command-based"}
            ]
        }
        
        # Create metadata file
        with open(self.test_logs_dir / "sessions_metadata.json", 'w') as f:
            json.dump(test_data, f)
        
        analyzer = SessionAnalyzer()
        self.assertEqual(analyzer.metadata, test_data)
    
    def test_analyze_log_file_basic_patterns(self):
        """Test log file analysis with basic conversation patterns"""
        analyzer = SessionAnalyzer()
        
        # Sample log content with various patterns
        log_content = """
Human: Can you help me with this code?
Assistant: Excellent! I'd be happy to help.

```python
def test_function():
    return "hello"
```

Human: That's not quite what I meant?
Assistant: Let me clarify - as we discussed earlier, you wanted something different.

```bash
echo "great!" 🎉
```

Human: Actually no, wait - hmm, I'm confused.
Assistant: No problem! Love it when we can work through this together.
"""
        
        # Create temporary log file
        log_file = self.test_logs_dir / "test.log"
        with open(log_file, 'w') as f:
            f.write(log_content)
        
        # Analyze the log file
        metrics = analyzer.analyze_log_file(log_file)
        
        # Verify basic counts
        self.assertEqual(metrics["exchanges"], 3)  # 3 Human: entries
        self.assertEqual(metrics["code_blocks"], 2)  # 2 ``` pairs
        self.assertGreater(metrics["questions_asked"], 0)
        self.assertGreater(metrics["enthusiasm_markers"], 0)  # "Excellent!", "great!", "🎉", "Love it"
        self.assertGreater(metrics["confusion_markers"], 0)  # "That's not", "wait", "hmm", "let me clarify"
        self.assertGreater(metrics["compaction_indicators"], 0)  # "as we discussed"
    
    def test_analyze_log_file_no_patterns(self):
        """Test log file analysis with no special patterns"""
        analyzer = SessionAnalyzer()
        
        # Simple content with no special patterns
        log_content = "Just some plain text without any special markers."
        
        log_file = self.test_logs_dir / "simple.log"
        with open(log_file, 'w') as f:
            f.write(log_content)
        
        metrics = analyzer.analyze_log_file(log_file)
        
        # All pattern counts should be zero
        self.assertEqual(metrics["exchanges"], 0)
        self.assertEqual(metrics["code_blocks"], 0)
        self.assertEqual(metrics["enthusiasm_markers"], 0)
        self.assertEqual(metrics["confusion_markers"], 0)
        self.assertEqual(metrics["compaction_indicators"], 0)
    
    def test_compare_methodologies_empty(self):
        """Test methodology comparison with no sessions"""
        analyzer = SessionAnalyzer()
        
        stats = analyzer.compare_methodologies()
        
        # Should return empty defaultdict structure
        self.assertIsInstance(stats, dict)
    
    def test_compare_methodologies_with_data(self):
        """Test methodology comparison with sample session data"""
        # Create test sessions
        test_sessions = [
            {
                "id": "test1",
                "methodology": "context-driven",
                "duration": 120,
                "creative_energy": 3,
                "log_file": str(self.test_logs_dir / "ctx.log")
            },
            {
                "id": "test2", 
                "methodology": "command-based",
                "duration": 90,
                "creative_energy": 2,
                "log_file": str(self.test_logs_dir / "cmd.log")
            }
        ]
        
        # Create metadata file
        with open(self.test_logs_dir / "sessions_metadata.json", 'w') as f:
            json.dump({"sessions": test_sessions}, f)
        
        # Create sample log files
        ctx_content = "Human: Test\nAssistant: Excellent! ```python\ncode\n```\n"
        cmd_content = "Human: Command\nAssistant: OK\n"
        
        with open(self.test_logs_dir / "ctx.log", 'w') as f:
            f.write(ctx_content)
        with open(self.test_logs_dir / "cmd.log", 'w') as f:
            f.write(cmd_content)
        
        analyzer = SessionAnalyzer()
        stats = analyzer.compare_methodologies()
        
        # Verify basic statistics
        self.assertEqual(stats["context-driven"]["sessions"], 1)
        self.assertEqual(stats["command-based"]["sessions"], 1)
        self.assertEqual(stats["context-driven"]["avg_duration"], 120)
        self.assertEqual(stats["command-based"]["avg_duration"], 90)
        self.assertEqual(stats["context-driven"]["avg_energy"], 3)
        self.assertEqual(stats["command-based"]["avg_energy"], 2)
    
    @patch('builtins.print')
    def test_generate_report(self, mock_print):
        """Test report generation"""
        # Create test session data
        test_sessions = [
            {
                "id": "test1",
                "methodology": "context-driven",
                "duration": 120,
                "creative_energy": 3,
                "log_file": str(self.test_logs_dir / "test.log")
            }
        ]
        
        with open(self.test_logs_dir / "sessions_metadata.json", 'w') as f:
            json.dump({"sessions": test_sessions}, f)
        
        # Create sample log file
        with open(self.test_logs_dir / "test.log", 'w') as f:
            f.write("Human: Test\nAssistant: Great!\n```code```\n")
        
        analyzer = SessionAnalyzer()
        analyzer.generate_report()
        
        # Verify that print was called (report was generated)
        self.assertTrue(mock_print.called)
        
        # Check that report contains expected sections
        print_calls = [str(call) for call in mock_print.call_args_list]
        report_text = ' '.join(print_calls)
        
        self.assertIn("ANALYSIS REPORT", report_text)
        self.assertIn("context-driven", report_text.lower())


class TestSessionAnalyzerPatterns(unittest.TestCase):
    """Test specific pattern matching functionality"""
    
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.test_logs_dir = Path(self.test_dir) / ".claude-logs"
        self.test_logs_dir.mkdir()
        
        # Create a minimal analyzer just for pattern testing
        with patch.object(SessionAnalyzer, '__init__', lambda x: None):
            self.analyzer = SessionAnalyzer()
    
    def tearDown(self):
        shutil.rmtree(self.test_dir)
    
    def test_enthusiasm_pattern_matching(self):
        """Test that enthusiasm patterns are correctly identified"""
        test_content = "This is excellent! That's great! I love it! 🎉 fantastic!"
        
        log_file = self.test_logs_dir / "enthusiasm.log"
        with open(log_file, 'w') as f:
            f.write(test_content)
        
        metrics = self.analyzer.analyze_log_file(log_file)
        
        # Should find: excellent!, great!, love it, 🎉, fantastic!
        self.assertGreaterEqual(metrics["enthusiasm_markers"], 5)
    
    def test_confusion_pattern_matching(self):
        """Test that confusion patterns are correctly identified"""
        test_content = "That's not right. Hmm, wait. Actually no. Let me clarify. I meant something else."
        
        log_file = self.test_logs_dir / "confusion.log"
        with open(log_file, 'w') as f:
            f.write(test_content)
        
        metrics = self.analyzer.analyze_log_file(log_file)
        
        # Should find: that's not, hmm, wait, actually no, let me clarify, I meant
        self.assertGreaterEqual(metrics["confusion_markers"], 5)
    
    def test_compaction_pattern_matching(self):
        """Test that compaction patterns are correctly identified"""
        test_content = "As we discussed before, remember when we talked about this? Earlier you said something."
        
        log_file = self.test_logs_dir / "compaction.log"
        with open(log_file, 'w') as f:
            f.write(test_content)
        
        metrics = self.analyzer.analyze_log_file(log_file)
        
        # Should find: as we discussed, remember when, earlier you said
        self.assertGreaterEqual(metrics["compaction_indicators"], 3)
    
    def test_code_block_counting(self):
        """Test that code blocks are correctly counted"""
        test_content = """
```python
print("hello")
```

Some text here.

```bash
echo "world"
```

```
just a plain code block
```
"""
        
        log_file = self.test_logs_dir / "code.log"
        with open(log_file, 'w') as f:
            f.write(test_content)
        
        metrics = self.analyzer.analyze_log_file(log_file)
        
        # Should find 6 ``` markers total (3 code blocks * 2 markers each)
        self.assertEqual(metrics["code_blocks"], 6)


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)