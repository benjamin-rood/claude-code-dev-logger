use crate::git::GitRepo;
use crate::session::{Methodology, SessionMetadata, SessionsMetadata};
use anyhow::{Context, Result};
use chrono::Utc;
use std::fs;
use std::io::{self, Write};
use std::path::{Path, PathBuf};
use std::process::{Command, Stdio};

pub struct ClaudeLogger {
    logs_dir: PathBuf,
    metadata_file: PathBuf,
    metadata: SessionsMetadata,
    git_repo: GitRepo,
}

impl ClaudeLogger {
    pub fn new() -> Result<Self> {
        let logs_dir = Self::get_logs_directory()?;
        Self::new_with_dir(&logs_dir)
    }

    pub fn new_with_dir(logs_dir: &Path) -> Result<Self> {
        // Ensure logs directory exists
        fs::create_dir_all(logs_dir)
            .with_context(|| format!("Failed to create logs directory: {}", logs_dir.display()))?;

        let metadata_file = logs_dir.join("sessions_metadata.json");
        
        // Load existing metadata or create new
        let metadata = Self::load_metadata(&metadata_file)?;
        
        // Initialize git repository
        let git_repo = GitRepo::init_or_open(logs_dir)?;

        Ok(Self {
            logs_dir: logs_dir.to_path_buf(),
            metadata_file,
            metadata,
            git_repo,
        })
    }

    fn get_logs_directory() -> Result<PathBuf> {
        let home_dir = dirs::home_dir()
            .context("Failed to get home directory")?;
        Ok(home_dir.join(".claude-logs"))
    }

    fn load_metadata(metadata_file: &Path) -> Result<SessionsMetadata> {
        if metadata_file.exists() {
            let content = fs::read_to_string(metadata_file)
                .with_context(|| format!("Failed to read metadata file: {}", metadata_file.display()))?;
            
            serde_json::from_str(&content)
                .with_context(|| format!("Failed to parse metadata file: {}", metadata_file.display()))
        } else {
            Ok(SessionsMetadata::new())
        }
    }

    pub fn create_session_log(&self, args: &[String]) -> Result<(PathBuf, SessionMetadata)> {
        let timestamp = Utc::now();
        let session_id = timestamp.format("%Y-%m-%d_%H-%M-%S").to_string();
        
        let project_dir = std::env::current_dir()
            .context("Failed to get current working directory")?;
        
        let methodology = self.detect_methodology(&project_dir)
            .context("Failed to detect development methodology")?;
        
        let project_name = project_dir
            .file_name()
            .and_then(|name| name.to_str())
            .unwrap_or("unknown")
            .to_string();

        let log_file = self.logs_dir.join(format!("{}.log", session_id));
        
        let command = if args.is_empty() {
            "claude".to_string()
        } else {
            format!("claude {}", args.join(" "))
        };

        let session = SessionMetadata {
            id: session_id,
            timestamp,
            project: project_name,
            methodology,
            working_directory: project_dir,
            command,
            log_file: log_file.clone(),
            duration: None,
            end_time: None,
            features_worked_on: Vec::new(),
            creative_energy: None,
        };

        Ok((log_file, session))
    }

    fn detect_methodology(&self, project_dir: &Path) -> Result<Methodology> {
        let claude_md_path = project_dir.join(".claude").join("CLAUDE.md");
        
        if claude_md_path.exists() {
            let content = fs::read_to_string(&claude_md_path)
                .with_context(|| format!("Failed to read CLAUDE.md: {}", claude_md_path.display()))?;
            
            if content.contains("Context-Driven") || content.contains("context-driven") {
                return Ok(Methodology::ContextDriven);
            } else if content.contains("Command-Based") || content.contains("command-based") {
                return Ok(Methodology::CommandBased);
            }
        }

        Ok(Methodology::Unknown)
    }

    pub fn run_logged_session(&mut self, claude_args: &[String], track_energy: bool) -> Result<()> {
        let (log_file, mut session) = self.create_session_log(claude_args)?;
        
        println!("Starting Claude session - logging to: {}", log_file.display());
        
        let start_time = Utc::now();
        
        // Run Claude CLI through script command for full terminal capture
        let exit_status = self.run_claude_with_logging(&log_file, claude_args)?;
        
        let end_time = Utc::now();
        session.duration = Some(end_time.signed_duration_since(start_time));
        session.end_time = Some(end_time);

        // Get creative energy if requested
        if track_energy {
            session.creative_energy = Self::get_creative_energy()?;
        }

        // Save session metadata
        self.metadata.add_session(session.clone());
        self.save_metadata()?;

        // Commit to git
        self.git_repo.commit_session(&session, &log_file)?;

        println!("Session completed. Exit status: {}", exit_status);
        if let Some(energy) = session.creative_energy {
            println!("Creative energy level: {}/3", energy);
        }

        Ok(())
    }

    fn run_claude_with_logging(&self, log_file: &Path, claude_args: &[String]) -> Result<i32> {
        let mut cmd = Command::new("script");
        cmd.arg("-q")  // Quiet mode
            .arg(&log_file)
            .arg("claude");
        
        // Add claude arguments
        for arg in claude_args {
            cmd.arg(arg);
        }

        let mut child = cmd
            .stdout(Stdio::inherit())
            .stderr(Stdio::inherit())
            .stdin(Stdio::inherit())
            .spawn()
            .context("Failed to start script command")?;

        let exit_status = child.wait()
            .context("Failed to wait for script command")?;

        Ok(exit_status.code().unwrap_or(-1))
    }

    pub fn get_creative_energy() -> Result<Option<u8>> {
        print!("Rate your creative energy for this session (1-3, or press Enter to skip): ");
        io::stdout().flush()?;

        let mut input = String::new();
        io::stdin().read_line(&mut input)
            .context("Failed to read creative energy input")?;

        let input = input.trim();
        if input.is_empty() {
            return Ok(None);
        }

        match input.parse::<u8>() {
            Ok(energy) if (1..=3).contains(&energy) => Ok(Some(energy)),
            _ => {
                println!("Invalid input. Please enter 1, 2, or 3.");
                Self::get_creative_energy()
            }
        }
    }

    pub fn save_metadata(&self) -> Result<()> {
        let json = serde_json::to_string_pretty(&self.metadata)
            .context("Failed to serialize metadata to JSON")?;
        
        fs::write(&self.metadata_file, json)
            .with_context(|| format!("Failed to write metadata file: {}", self.metadata_file.display()))?;
        
        Ok(())
    }

    pub fn get_session(&self, session_id: &str) -> Option<&SessionMetadata> {
        self.metadata.get_session(session_id)
    }

    pub fn list_sessions(&self, methodology_filter: Option<&str>, limit: usize) -> Vec<&SessionMetadata> {
        let mut sessions: Vec<_> = self.metadata.sessions.values().collect();
        
        // Filter by methodology if specified
        if let Some(methodology_str) = methodology_filter {
            let methodology = match methodology_str.to_lowercase().as_str() {
                "context-driven" | "contextdriven" => Some(Methodology::ContextDriven),
                "command-based" | "commandbased" => Some(Methodology::CommandBased),
                "unknown" => Some(Methodology::Unknown),
                _ => None,
            };
            
            if let Some(method) = methodology {
                sessions.retain(|session| session.methodology == method);
            }
        }

        // Sort by timestamp (newest first)
        sessions.sort_by(|a, b| b.timestamp.cmp(&a.timestamp));
        
        // Apply limit
        sessions.into_iter().take(limit).collect()
    }

    pub fn metadata(&self) -> &SessionsMetadata {
        &self.metadata
    }

    pub fn add_session(&mut self, session: SessionMetadata) {
        self.metadata.add_session(session);
    }

    pub fn git_repo(&self) -> &GitRepo {
        &self.git_repo
    }
}