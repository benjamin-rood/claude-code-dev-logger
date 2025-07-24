# Claude Code Dev Logger

A comprehensive logging and analysis tool for Claude Code CLI conversations, designed to track and compare different development methodologies with automatic git versioning.

```
 ██████╗ ██╗      █████╗ ██╗   ██╗██████╗ ███████╗       ██████╗  ██╗     ██╗
██╔════╝ ██║     ██╔══██╗██║   ██║██╔══██╗██╔════╝       ██╔════╝ ██║     ██║
██║      ██║     ███████║██║   ██║██║  ██║█████╗         ██║      ██║     ██║
██║      ██║     ██╔══██║██║   ██║██║  ██║██╔══╝         ██║      ██║     ██║
╚██████╗ ███████╗██║  ██║╚██████╔╝██████╔╝███████╗       ╚██████╗ ███████╗██║
 ╚═════╝ ╚══════╝╚═╝  ╚═╝ ╚═════╝ ╚═════╝ ╚══════╝        ╚═════╝ ╚══════╝╚═╝

██████╗ ███████╗██╗   ██╗       ██╗      ██████╗  ██████╗  ██████╗ ███████╗██████╗ 
██╔══██╗██╔════╝██║   ██║       ██║     ██╔═══██╗██╔════╝ ██╔════╝ ██╔════╝██╔══██╗
██║  ██║█████╗  ██║   ██║       ██║     ██║   ██║██║  ███╗██║  ███╗█████╗  ██████╔╝
██║  ██║██╔══╝  ╚██╗ ██╔╝       ██║     ██║   ██║██║   ██║██║   ██║██╔══╝  ██╔══██╗
██████╔╝███████╗ ╚████╔╝        ███████╗╚██████╔╝╚██████╔╝╚██████╔╝███████╗██║  ██║
╚═════╝ ╚══════╝  ╚═══╝         ╚══════╝ ╚═════╝  ╚═════╝  ╚═════╝ ╚══════╝╚═╝  ╚═╝
```

## 🎯 Purpose

Initially intended to be used with the [Contextual Spec-Driven Agentic Development framework for Claude Code CLI](https://github.com/benjamin-rood/context-driven-sdad) to use to evaluate its performance as a methodology, but it can be adapted to any purpose where you might want complete storage of Claude Code CLI conversations.

Claude Logger helps you:
- **Track every conversation** with Claude CLI automatically
- **Measure creative energy** after each session
- **Compare methodologies** (command-based vs context-driven)
- **Maintain git history** of all sessions
- **Analyze patterns** to find what works best for you

## 🚀 Quick Start

### Installation

1. **Download the scripts:**
```bash
# Clone or download claude-logger and analyze-sessions.py
wget https://raw.githubusercontent.com/benjamin-rood/claude-code-dev-logger/main/claude-logger.py
wget https://raw.githubusercontent.com/benjamin-rood/claude-code-dev-logger/main/analyze-sessions.py

# Make executable
chmod +x claude-logger analyze-sessions.py

# Move to PATH
sudo mv claude-logger analyze-sessions.py /usr/local/bin/
```

2. **Create an alias (recommended):**
```bash
# Add to ~/.bashrc or ~/.zshrc
alias claude='claude-logger --track-energy'
```

### Basic Usage

```bash
# Start a logged session with energy tracking
claude-logger --track-energy

# Regular session (no energy prompt)
claude-logger

# Your normal Claude commands work as expected
claude-logger --help
claude-logger --version
```

## 📊 Features

### Automatic Logging
- Captures complete conversation transcript
- Records metadata (project, methodology, duration)
- Detects methodology from `.claude/CLAUDE.md`
- Timestamps every session

### Git Integration
- Automatically creates git repository in `~/.claude-logs/`
- Commits each session with meaningful messages
- Preserves immutable history
- Enables powerful searching and analysis

### Creative Energy Tracking
After each session with `--track-energy`:
```
How would you rate your creative energy after this session?
1 🔋     - Depleted
2 🔋🔋   - Neutral
3 🔋🔋🔋 - Energized

Energy level (1-3): 3
```

### Session Analysis
Compare methodologies across multiple sessions:
```bash
# Generate analysis report
claude-logger --analyze

# Output:
📊 Methodology: CONTEXT-DRIVEN
   Sessions: 12
   Avg Duration: 2834.2 seconds
   Avg Creative Energy: 🔋🔋🔋 (2.8/3)
   Avg Exchanges: 45.3
   Enthusiasm Markers: 8.2
   
📊 Methodology: COMMAND-BASED
   Sessions: 8  
   Avg Duration: 1923.5 seconds
   Avg Creative Energy: 🔋🔋 (2.1/3)
   Avg Exchanges: 23.7
   Enthusiasm Markers: 3.4
```

## 🛠️ Commands

### Running Sessions
```bash
# Basic logging
claude-logger [claude arguments]

# With energy tracking (recommended)
claude-logger --track-energy [claude arguments]
claude-logger -e
```

### Viewing History
```bash
# List all sessions with summary
claude-logger --list-sessions
claude-logger -l

# Show git log with pretty formatting
claude-logger --git-log
claude-logger -g

# View specific session
claude-logger --show-session 20240115_143022
claude-logger -s 20240115_143022
```

### Analysis
```bash
# Run comparative analysis
claude-logger --analyze
claude-logger -a
```

## 📁 File Structure

All logs are stored in `~/.claude-logs/`:
```
~/.claude-logs/
├── .git/                    # Git repository
├── sessions_metadata.json   # Session index and metadata
├── claude_[project]_[methodology]_[timestamp].log
└── analyze-sessions.py      # Analysis script
```

### Log Naming Convention
`claude_[project]_[methodology]_[timestamp].log`
- **project**: Current directory name
- **methodology**: Detected from `.claude/CLAUDE.md`
- **timestamp**: YYYYMMDD_HHMMSS

## 🔍 Methodology Detection

Claude Logger automatically detects your methodology by reading `.claude/CLAUDE.md`:
- Contains "Context-Driven" → `context-driven`
- Contains "Spec-Driven" → `command-based`
- Otherwise → `unknown`

## 📈 Metrics Tracked

### Session Metadata
- Timestamp and duration
- Project and working directory
- Command executed
- Methodology used
- Creative energy rating

### Conversation Analysis
- Number of exchanges
- Code blocks generated
- Questions asked
- Enthusiasm markers (excitement, joy)
- Confusion markers (clarifications)
- Compaction indicators (context loss)

## 🔧 Advanced Usage

### Git Commands
```bash
# Navigate to logs directory
cd ~/.claude-logs

# Search across all sessions
git grep "authentication"

# Compare two sessions
git diff session1.log session2.log

# View commit history with stats
git log --stat

# Find when you were most energized
git log --grep="Energy: 🔋🔋🔋"
```

### Remote Backup
```bash
cd ~/.claude-logs
git remote add origin git@github.com:yourusername/claude-logs-private.git
git push -u origin main
```

### Custom Analysis
```python
# The metadata file is JSON - easy to analyze
import json
with open("~/.claude-logs/sessions_metadata.json") as f:
    data = json.load(f)
    
# Find your most productive time of day
# Track methodology preferences over time
# Identify patterns in creative energy
```

## 🎨 Example Workflow

1. **Start your day:**
```bash
cd my-project
claude  # Using alias with --track-energy
```

2. **Work naturally with Claude**
   - Conversation is logged automatically
   - No need to think about logging

3. **End session:**
   - Rate your energy (1-3)
   - Session commits to git automatically

4. **Weekly review:**
```bash
# See what you've accomplished
claude-logger --git-log

# Analyze patterns
claude-logger --analyze

# Review high-energy sessions
git log --grep="Energy: 🔋🔋🔋" --oneline
```

## 🤝 Integration Tips

### With Spec-Driven Development Projects
Place in projects using either methodology:
- Command-based: `marcelsud/spec-driven-agentic-development`
- Context-driven: Your custom context-driven approach

The logger detects and tracks which methodology you're using automatically.

### Shell Aliases
```bash
# Always track energy
alias claude='claude-logger --track-energy'

# Quick session review
alias claude-history='claude-logger --git-log'

# Daily standup helper
alias claude-yesterday='cd ~/.claude-logs && git log --since="24 hours ago" --pretty=format:"%h - %s"'
```

## 📊 Understanding the Analysis

The analyzer looks for patterns indicating:

**Joy/Engagement:**
- Enthusiasm markers: "excellent!", "great!", "love it", "🎉"
- Question frequency (curiosity)
- Code generation rate

**Friction/Confusion:**
- Clarification requests: "I meant", "actually", "not quite"
- Context loss: "as we discussed", "remember when"
- Conversation restarts

**Productivity:**
- Session duration
- Code blocks generated
- Features completed

## 🔮 Future Enhancements

Potential additions:
- Feature extraction from conversations
- Time-of-day productivity analysis
- Learning curve tracking
- Export to CSV/JSON
- Web dashboard
- Team aggregation

## 🐛 Troubleshooting

### Git not initialized
```bash
cd ~/.claude-logs
git init
```

### Permission issues
```bash
chmod +x claude-logger
chmod +x analyze-sessions.py
```

### Can't find claude command
Ensure Claude Code CLI tool is in your PATH before installing the logger.

## 📝 License

MIT License - Use freely and modify as needed.

## 🙏 Credits

Built to support the comparison of:
- Command-based methodology by @marcelsud
- Context-driven methodology for natural conversation flow
**Remember**: The best methodology is the one that brings you joy and creative energy! 🔋🔋🔋

---
