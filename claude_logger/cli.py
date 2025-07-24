#!/usr/bin/env python3
"""
Command-line interface for Claude Code Dev Logger
"""
import argparse
import sys
from pathlib import Path

from .logger import ClaudeLogger
from .analyzer import SessionAnalyzer


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description='Claude CLI with conversation logging',
        usage='%(prog)s [options] [claude arguments]'
    )
    
    parser.add_argument(
        '--track-energy', '-e',
        action='store_true',
        help='Prompt for creative energy level after session'
    )
    
    parser.add_argument(
        '--analyze', '-a',
        action='store_true',
        help='Analyze logged sessions instead of starting new one'
    )
    
    parser.add_argument(
        '--list-sessions', '-l',
        action='store_true',
        help='List all logged sessions'
    )
    
    parser.add_argument(
        '--git-log', '-g',
        action='store_true',
        help='Show git log of sessions'
    )
    
    parser.add_argument(
        '--show-session', '-s',
        metavar='SESSION_ID',
        help='Show a specific session log'
    )
    
    # Capture all remaining arguments for claude
    parser.add_argument(
        'claude_args',
        nargs='*',
        help='Arguments to pass to claude'
    )
    
    args = parser.parse_args()
    logger = ClaudeLogger()
    
    if args.analyze:
        # Run the analyzer
        analyzer = SessionAnalyzer()
        analyzer.generate_report()
    elif args.list_sessions:
        # List sessions with summary
        print("\n=== Logged Claude Sessions ===\n")
        for session in logger.metadata.get("sessions", []):
            print(f"📅 {session['timestamp']}")
            print(f"   Session ID: {session['id']}")
            print(f"   Project: {session['project']}")
            print(f"   Methodology: {session['methodology']}")
            duration_min = session.get('duration', 0) / 60
            print(f"   Duration: {duration_min:.1f} minutes")
            if session.get('creative_energy'):
                print(f"   Energy: {'🔋' * session['creative_energy']}")
            print()
    elif args.git_log:
        # Show git log with nice formatting
        import subprocess
        print("\n=== Git History of Claude Sessions ===\n")
        subprocess.run([
            "git", "-C", str(logger.logs_dir), "log", 
            "--pretty=format:%C(yellow)%h%C(reset) - %C(green)%ad%C(reset) - %C(bold)%s%C(reset)",
            "--date=relative",
            "-20"  # Last 20 commits
        ])
        print("\n")
    elif args.show_session:
        # Show specific session
        session_found = False
        for session in logger.metadata.get("sessions", []):
            if session['id'] == args.show_session:
                session_found = True
                log_file = Path(session['log_file'])
                if log_file.exists():
                    print(f"\n=== Session {args.show_session} ===")
                    print(f"Project: {session['project']}")
                    print(f"Methodology: {session['methodology']}")
                    print(f"Duration: {session.get('duration', 0)/60:.1f} minutes")
                    if session.get('creative_energy'):
                        print(f"Energy: {'🔋' * session['creative_energy']}")
                    print("\n--- Log Content ---\n")
                    
                    # Use less/more for pagination
                    import subprocess
                    subprocess.run(["less", str(log_file)])
                else:
                    print(f"Log file not found: {log_file}")
                break
        
        if not session_found:
            print(f"Session {args.show_session} not found")
    else:
        # Run claude with logging
        logger.run_logged_session(args)


if __name__ == "__main__":
    main()