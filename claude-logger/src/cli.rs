use clap::{Parser, Subcommand};

#[derive(Parser)]
#[command(name = "claude-logger")]
#[command(about = "Claude Code conversation logging and analysis")]
#[command(version = "0.1.0")]
pub struct Cli {
    #[command(subcommand)]
    pub command: Option<Commands>,
    
    /// Arguments to pass to claude
    #[arg(trailing_var_arg = true, allow_hyphen_values = true)]
    pub claude_args: Vec<String>,
    
    /// Track creative energy after session
    #[arg(short = 'e', long)]
    pub track_energy: bool,
}

#[derive(Subcommand)]
pub enum Commands {
    /// Analyze logged sessions
    #[command(name = "analyze")]
    Analyze {
        /// Analyze sessions using specific methodology
        #[arg(long)]
        methodology: Option<String>,
        
        /// Generate comparative analysis between methodologies
        #[arg(long)]
        comparative: bool,
    },
    
    /// List all logged sessions
    #[command(name = "list")]
    List {
        /// Filter by methodology
        #[arg(short, long)]
        methodology: Option<String>,
        
        /// Limit number of sessions shown
        #[arg(short, long, default_value = "10")]
        limit: usize,
    },
    
    /// Show git log of sessions
    #[command(name = "git-log")]
    GitLog {
        /// Number of commits to show
        #[arg(short, long, default_value = "10")]
        count: usize,
    },
    
    /// Show specific session
    #[command(name = "show")]
    Show { 
        /// Session ID to display
        session_id: String,
        
        /// Show full log content
        #[arg(short, long)]
        full: bool,
    },
}

impl Cli {
    pub fn is_command_mode(&self) -> bool {
        self.command.is_some()
    }
    
    pub fn should_run_claude(&self) -> bool {
        !self.is_command_mode()
    }
}