#!/usr/bin/env python3
"""
Consolidated unit tests for claude_logger analyzer module
"""
import unittest
import tempfile
import shutil
import json
import os
from pathlib import Path
from unittest.mock import patch

# Import from the new package structure
from claude_logger.analyzer import SessionAnalyzer


class TestSessionAnalyzer(unittest.TestCase):
    """Test cases for SessionAnalyzer class"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.test_logs_dir = Path(self.test_dir) / ".claude-logs"
        self.test_logs_dir.mkdir()
        
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.test_dir)
    
    def _create_test_analyzer(self):
        """Create an analyzer with test directory setup"""
        with patch('claude_logger.analyzer.Path.home', return_value=Path(self.test_dir)):
            analyzer = SessionAnalyzer()
            return analyzer
    
    def test_load_metadata_empty(self):
        """Test loading metadata when file doesn't exist"""
        analyzer = self._create_test_analyzer()
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
        
        analyzer = self._create_test_analyzer()
        self.assertEqual(analyzer.metadata, test_data)
    
    def test_analyze_log_file_basic_patterns(self):
        """Test log file analysis with basic conversation patterns"""
        analyzer = self._create_test_analyzer()
        
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
        self.assertEqual(metrics["code_blocks"], 4)  # 4 ``` markers
        self.assertGreater(metrics["questions_asked"], 0)
        self.assertGreater(metrics["enthusiasm_markers"], 0)  # "Excellent!", "great!", "🎉", "Love it"
        self.assertGreater(metrics["confusion_markers"], 0)  # "That's not", "wait", "hmm", "let me clarify"
        self.assertGreater(metrics["compaction_indicators"], 0)  # "as we discussed"


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


class TestSessionAnalyzerIntegration(unittest.TestCase):
    """Integration tests using real file operations"""
    
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
        self.assertTrue(hasattr(SessionAnalyzer, 'analyze_log_file'))
        self.assertTrue(hasattr(SessionAnalyzer, 'compare_methodologies'))
        self.assertTrue(hasattr(SessionAnalyzer, 'generate_report'))
    
    def test_pattern_analysis_real_file(self):
        """Test pattern analysis with a real temporary file"""
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