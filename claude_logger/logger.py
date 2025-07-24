#!/usr/bin/env python3
"""
Enhanced Claude CLI wrapper for logging conversations with methodology tracking
"""
import subprocess
import sys
import os
import json
import argparse
from datetime import datetime
from pathlib import Path

class ClaudeLogger:
    def __init__(self):
        self.logs_dir = Path.home() / ".claude-logs"
        self.logs_dir.mkdir(exist_ok=True)
        self.metadata_file = self.logs_dir / "sessions_metadata.json"
        self.load_metadata()
        self.init_git_repo()
    
    def load_metadata(self):
        """Load or initialize session metadata"""
        if self.metadata_file.exists():
            with open(self.metadata_file, 'r') as f:
                self.metadata = json.load(f)
        else:
            self.metadata = {"sessions": []}
    
    def save_metadata(self):
        """Save session metadata"""
        with open(self.metadata_file, 'w') as f:
            json.dump(self.metadata, f, indent=2)
    
    def init_git_repo(self):
        """Initialize git repository for logs if not exists"""
        git_dir = self.logs_dir / ".git"
        if not git_dir.exists():
            print("🔧 Initializing git repository for conversation logs...")
            subprocess.run(["git", "init"], cwd=self.logs_dir, capture_output=True)
            
            # Create .gitignore
            gitignore = self.logs_dir / ".gitignore"
            with open(gitignore, 'w') as f:
                f.write("# Temporary files\n")
                f.write("*.tmp\n")
                f.write("*.swp\n")
                f.write(".DS_Store\n")
            
            # Initial commit
            subprocess.run(["git", "add", "."], cwd=self.logs_dir, capture_output=True)
            subprocess.run(["git", "commit", "-m", "Initialize Claude conversation logs"], 
                         cwd=self.logs_dir, capture_output=True)
    
    def git_commit_session(self, session_info, log_file):
        """Commit session to git with meaningful message"""
        # Add files
        subprocess.run(["git", "add", log_file.name, "sessions_metadata.json"], 
                     cwd=self.logs_dir, capture_output=True)
        
        # Create commit message
        energy_str = ""
        if session_info.get("creative_energy"):
            energy_str = f" | Energy: {'🔋' * session_info['creative_energy']}"
        
        duration_min = session_info.get("duration", 0) / 60
        commit_msg = (
            f"{session_info['methodology']}: {session_info['project']} "
            f"({duration_min:.1f}min){energy_str}\n\n"
            f"Session ID: {session_info['id']}\n"
            f"Command: {session_info['command']}\n"
        )
        
        # Commit
        result = subprocess.run(
            ["git", "commit", "-m", commit_msg], 
            cwd=self.logs_dir, 
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            # Get commit hash
            hash_result = subprocess.run(
                ["git", "rev-parse", "--short", "HEAD"],
                cwd=self.logs_dir,
                capture_output=True,
                text=True
            )
            commit_hash = hash_result.stdout.strip()
            return commit_hash
        return None
    
    def create_session_log(self, args):
        """Create a new session log with metadata"""
        timestamp = datetime.now()
        session_id = timestamp.strftime("%Y%m%d_%H%M%S")
        
        # Determine project and methodology from current directory
        cwd = Path.cwd()
        project_name = cwd.name
        
        # Check for methodology indicators
        methodology = "unknown"
        if (cwd / ".claude" / "CLAUDE.md").exists():
            # Read first line to determine methodology
            with open(cwd / ".claude" / "CLAUDE.md", 'r') as f:
                first_line = f.readline()
                if "Context-Driven" in first_line:
                    methodology = "context-driven"
                elif "Spec-Driven" in first_line:
                    methodology = "command-based"
        
        # Create log file
        log_filename = f"claude_{project_name}_{methodology}_{session_id}.log"
        log_file = self.logs_dir / log_filename
        
        # Create session metadata
        session_info = {
            "id": session_id,
            "timestamp": timestamp.isoformat(),
            "project": project_name,
            "methodology": methodology,
            "working_directory": str(cwd),
            "command": f"claude {' '.join(args.claude_args)}",
            "log_file": str(log_file),
            "duration": None,  # Will be updated at end
            "features_worked_on": [],  # Can be parsed from logs later
            "creative_energy": None  # Can be added via post-session prompt
        }
        
        return log_file, session_info
    
    def run_logged_session(self, args):
        """Run Claude with logging"""
        log_file, session_info = self.create_session_log(args)
        
        # Log session start
        with open(log_file, 'w') as f:
            f.write(f"=== Claude CLI Session Started ===\n")
            f.write(f"Timestamp: {session_info['timestamp']}\n")
            f.write(f"Project: {session_info['project']}\n")
            f.write(f"Methodology: {session_info['methodology']}\n")
            f.write(f"Working Directory: {session_info['working_directory']}\n")
            f.write(f"Command: {session_info['command']}\n")
            f.write("=" * 50 + "\n\n")
        
        # Run claude with script to capture everything
        cmd = ["script", "-q", "-a", str(log_file), "-c", f"claude {' '.join(args.claude_args)}"]
        
        start_time = datetime.now()
        try:
            result = subprocess.run(cmd)
            return_code = result.returncode
        except KeyboardInterrupt:
            print("\nSession interrupted")
            return_code = 130
        finally:
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            # Update session info
            session_info["duration"] = duration
            session_info["end_time"] = end_time.isoformat()
            
            # Log session end
            with open(log_file, 'a') as f:
                f.write("\n\n" + "=" * 50 + "\n")
                f.write(f"=== Claude CLI Session Ended ===\n")
                f.write(f"End Time: {end_time}\n")
                f.write(f"Duration: {duration:.2f} seconds\n")
                f.write("=" * 50 + "\n")
            
            # Optional: Prompt for creative energy
            if args.track_energy:
                energy = self.get_creative_energy()
                session_info["creative_energy"] = energy
            
            # Save metadata
            self.metadata["sessions"].append(session_info)
            self.save_metadata()
            
            # Commit to git
            commit_hash = self.git_commit_session(session_info, log_file)
            
            print(f"\n📝 Session logged to: {log_file}")
            print(f"📊 Methodology: {session_info['methodology']}")
            print(f"⏱️  Duration: {duration:.2f} seconds ({duration/60:.1f} minutes)")
            
            if commit_hash:
                print(f"🔒 Git commit: {commit_hash}")
            
            if args.track_energy and energy:
                print(f"🔋 Creative Energy: {'🔋' * energy}")
        
        sys.exit(return_code)
    
    def get_creative_energy(self):
        """Prompt for creative energy level"""
        print("\n" + "=" * 50)
        print("How would you rate your creative energy after this session?")
        print("1 🔋     - Depleted")
        print("2 🔋🔋   - Neutral") 
        print("3 🔋🔋🔋 - Energized")
        
        while True:
            try:
                energy = input("\nEnergy level (1-3): ").strip()
                if energy in ['1', '2', '3']:
                    return int(energy)
                print("Please enter 1, 2, or 3")
            except KeyboardInterrupt:
                print("\nSkipping energy tracking")
                return None

def main():
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
        import subprocess
        subprocess.run([sys.executable, str(Path(__file__).parent / "analyze-sessions.py")])
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