# Claude Code Dev Logger

A high-performance Rust implementation for comprehensive logging and analysis of Claude Code CLI conversations, with methodology tracking, creative energy measurement, and statistical comparison between development approaches.

## 🚀 Installation

### From Source (Recommended)
```bash
git clone https://github.com/benjamin-rood/claude-code-dev-logger.git
cd claude-code-dev-logger/claude-logger
cargo install --path .
```

### Development Build
```bash
cd claude-logger
cargo build --release
# Binary will be in target/release/claude-logger
```

## 📖 Usage

### Command Line Interface

```bash
# Run Claude with logging and energy tracking
claude-logger --track-energy [claude arguments]

# Analyze existing sessions with comparative methodology analysis
claude-logger analyze --comparative

# Analyze sessions by specific methodology
claude-logger analyze --methodology context-driven

# List all logged sessions
claude-logger list --limit 10

# Show git history of sessions
claude-logger git-log --count 10

# View a specific session
claude-logger show SESSION_ID --full
```

### Direct Binary Usage

```bash
# After building, run directly from target
./target/release/claude-logger --help

# Or install globally and use anywhere
cargo install --path .
claude-logger --version
```

## 🏗️ Architecture

### Package Structure

```
claude-code-dev-logger/
├── claude_logger/           # Main package
│   ├── __init__.py         # Package exports
│   ├── logger.py           # Core logging functionality
│   ├── analyzer.py         # Session analysis and reporting
│   └── cli.py              # Command-line interface
├── tests/                   # Comprehensive test suite
│   ├── test_logger.py      # Logger tests
│   ├── test_analyzer.py    # Analyzer tests
│   └── fixtures.py         # Test data and helpers
├── docs/                    # Documentation
├── scripts/                 # Utility scripts
└── setup.py                # Package installation
```

### Core Components

1. **ClaudeLogger** (`claude_logger.logger`)
   - Session creation and metadata management
   - Git integration for conversation versioning
   - Creative energy tracking with user prompts
   - Methodology detection via `.claude/CLAUDE.md` files

2. **SessionAnalyzer** (`claude_logger.analyzer`) 
   - Pattern matching for conversation analysis
   - Statistical comparison between methodologies
   - Report generation with effectiveness metrics
   - Conversation quality indicators (enthusiasm, confusion, context loss)

3. **CLI Interface** (`claude_logger.cli`)
   - Command-line wrapper around core functionality
   - Session management and viewing capabilities
   - Integration with existing Claude Code workflows

## 📊 Features

### Automatic Logging
- **Full terminal capture** via Unix `script` command
- **Git versioning** of all conversation sessions
- **Metadata tracking** (duration, methodology, creative energy)
- **Project context detection** from `.claude/CLAUDE.md` files

### Methodology Detection
- **Context-driven**: Detected from "Context-Driven" in CLAUDE.md
- **Command-based**: Detected from "Spec-Driven" in CLAUDE.md  
- **Unknown**: When no methodology file is present

### Conversation Analysis
- **Pattern Detection**: Enthusiasm, confusion, and context loss markers
- **Code Block Counting**: Tracks code generation activity
- **Exchange Analysis**: Measures conversation depth and complexity
- **Statistical Comparison**: Quantifies methodology effectiveness

### Creative Energy Tracking
- **1-3 Scale**: Post-session energy level measurement
- **Trend Analysis**: Track energy patterns across methodologies
- **Effectiveness Correlation**: Link energy levels to productivity

## 🧪 Testing

The package includes a comprehensive test suite with 23+ working tests:

```bash
# Run all tests
python -m pytest tests/

# Run specific test files
python -m pytest tests/test_logger.py
python -m pytest tests/test_analyzer.py

# Run with coverage
python -m pytest tests/ --cov=claude_logger
```

### Test Categories
- **Unit Tests**: Individual method validation with proper mocking
- **Integration Tests**: End-to-end workflow validation with real files
- **Pattern Tests**: Regex validation for conversation analysis
- **CLI Tests**: Command-line interface validation

## 📁 Data Storage

All conversation logs and metadata are stored in `~/.claude-logs/`:

```
~/.claude-logs/
├── .git/                           # Git repository for versioning
├── sessions_metadata.json         # Session tracking database
├── claude_project_methodology_timestamp.log  # Individual session logs
└── .gitignore                     # Git ignore patterns
```

## 🔍 Analysis Metrics

### Conversation Quality Indicators
- **Enthusiasm Markers**: "excellent!", "great!", "🎉" 
- **Confusion Markers**: "hmm", "wait", "let me clarify"
- **Compaction Indicators**: "as we discussed", "remember when"
- **Code Generation**: Count of code blocks and programming activity

### Methodology Comparison
- **Session Duration**: Average time per methodology
- **Creative Energy**: Average energy levels (1-3 scale)  
- **Conversation Depth**: Number of exchanges and questions
- **Effectiveness Metrics**: Joy vs confusion ratios

## 🛠️ Development

### Setup Development Environment
```bash
git clone https://github.com/benjamin-rood/claude-code-dev-logger.git
cd claude-code-dev-logger
pip install -e ".[dev]"
```

### Run Tests
```bash
# Run all tests
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ --cov=claude_logger --cov-report=html
```

### Code Quality
```bash
# Format code
black claude_logger/ tests/

# Lint code  
flake8 claude_logger/ tests/

# Type checking
mypy claude_logger/
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes with tests
4. Run the test suite (`python -m pytest tests/`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Inspired by [Kiro](https://kiro.dev) and [Spec-Driven Agentic Development](https://github.com/marcelsud/spec-driven-agentic-development)
- Built for optimizing human-AI collaboration workflows
- Designed to work seamlessly with Claude Code CLI

## 📈 Roadmap

- [ ] Web dashboard for session visualization
- [ ] Integration with popular IDEs and editors
- [ ] Advanced pattern detection with machine learning
- [ ] Team collaboration features for shared methodology analysis
- [ ] Export capabilities to various data formats (CSV, JSON, etc.)