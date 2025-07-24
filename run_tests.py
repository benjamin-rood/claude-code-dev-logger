#!/usr/bin/env python3
"""
Test runner for claude-code-dev-logger
"""
import sys
import unittest
import os
from pathlib import Path

# Add the current directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent))

def discover_and_run_tests():
    """Discover and run all tests"""
    
    # Set up test discovery
    loader = unittest.TestLoader()
    start_dir = Path(__file__).parent
    
    # Discover all test files (test_*.py)
    suite = loader.discover(
        start_dir=str(start_dir),
        pattern='test_*.py',
        top_level_dir=str(start_dir)
    )
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(
        verbosity=2,
        stream=sys.stdout,
        descriptions=True,
        failfast=False
    )
    
    print("=" * 70)
    print("CLAUDE CODE DEV LOGGER - TEST SUITE")
    print("=" * 70)
    print()
    
    result = runner.run(suite)
    
    print()
    print("=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    if result.wasSuccessful():
        print(f"✅ All tests passed! ({result.testsRun} tests)")
        return 0
    else:
        print(f"❌ {len(result.failures)} failures, {len(result.errors)} errors out of {result.testsRun} tests")
        
        if result.failures:
            print("\nFAILURES:")
            for test, traceback in result.failures:
                print(f"  - {test}: {traceback.splitlines()[-1]}")
        
        if result.errors:
            print("\nERRORS:")
            for test, traceback in result.errors:
                print(f"  - {test}: {traceback.splitlines()[-1]}")
        
        return 1

def run_specific_test(test_name):
    """Run a specific test file or test case"""
    
    try:
        if test_name.endswith('.py'):
            # Remove .py extension
            test_name = test_name[:-3]
        
        # Try to import and run the specific test
        suite = unittest.TestLoader().loadTestsFromName(test_name)
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        
        return 0 if result.wasSuccessful() else 1
        
    except Exception as e:
        print(f"Error running test '{test_name}': {e}")
        return 1

def check_dependencies():
    """Check if required dependencies are available"""
    
    print("Checking dependencies...")
    
    missing_modules = []
    
    # Check for main modules
    try:
        import claude_logger_enhanced
        print("✅ claude_logger_enhanced.py found")
    except ImportError:
        print("❌ claude_logger_enhanced.py not found")
        missing_modules.append("claude_logger_enhanced.py")
    
    try:
        import session_analyzer
        print("✅ session_analyzer.py found")
    except ImportError:
        print("❌ session_analyzer.py not found")
        missing_modules.append("session_analyzer.py")
    
    # Check for standard library modules used in tests
    required_stdlib = [
        'unittest', 'tempfile', 'shutil', 'json', 
        'pathlib', 'subprocess', 'os', 'sys'
    ]
    
    for module in required_stdlib:
        try:
            __import__(module)
        except ImportError:
            print(f"❌ Required module '{module}' not available")
            missing_modules.append(module)
    
    if missing_modules:
        print(f"\n❌ Missing dependencies: {', '.join(missing_modules)}")
        return False
    else:
        print("\n✅ All dependencies available")
        return True

def main():
    """Main test runner function"""
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--check-deps":
            # Check dependencies only
            success = check_dependencies()
            return 0 if success else 1
        elif sys.argv[1] == "--help":
            print("Claude Code Dev Logger Test Runner")
            print()
            print("Usage:")
            print("  python run_tests.py                    - Run all tests")
            print("  python run_tests.py --check-deps       - Check dependencies")
            print("  python run_tests.py <test_name>        - Run specific test")
            print("  python run_tests.py --help             - Show this help")
            print()
            print("Examples:")
            print("  python run_tests.py test_claude_logger")
            print("  python run_tests.py test_session_analyzer.TestSessionAnalyzer")
            return 0
        else:
            # Run specific test
            return run_specific_test(sys.argv[1])
    else:
        # Check dependencies first
        if not check_dependencies():
            return 1
        
        # Run all tests
        return discover_and_run_tests()

if __name__ == "__main__":
    sys.exit(main())