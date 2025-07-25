use crate::session::SessionMetadata;
use anyhow::{Context, Result};
use std::path::{Path, PathBuf};
use std::process::Command;

pub struct GitRepo {
    repo_path: PathBuf,
}

impl GitRepo {
    pub fn init_or_open(path: &Path) -> Result<Self> {
        let git_dir = path.join(".git");
        
        if !git_dir.exists() {
            // Initialize new git repository
            let output = Command::new("git")
                .args(["init"])
                .current_dir(path)
                .output()
                .context("Failed to run git init")?;

            if !output.status.success() {
                let stderr = String::from_utf8_lossy(&output.stderr);
                return Err(anyhow::anyhow!("Git init failed: {}", stderr));
            }

            // Set up initial commit with .gitkeep
            let gitkeep_path = path.join(".gitkeep");
            std::fs::write(&gitkeep_path, "")
                .context("Failed to create .gitkeep file")?;

            Command::new("git")
                .args(["add", ".gitkeep"])
                .current_dir(path)
                .output()
                .context("Failed to add .gitkeep")?;

            Command::new("git")
                .args(["commit", "-m", "Initial commit: Initialize claude-logs repository"])
                .current_dir(path)
                .output()
                .context("Failed to create initial commit")?;
        }

        Ok(Self {
            repo_path: path.to_path_buf(),
        })
    }

    pub fn commit_session(&self, session: &SessionMetadata, log_file: &Path) -> Result<String> {
        // Add the log file to git
        let log_filename = log_file
            .file_name()
            .and_then(|name| name.to_str())
            .context("Invalid log file name")?;

        let add_output = Command::new("git")
            .args(["add", log_filename])
            .current_dir(&self.repo_path)
            .output()
            .context("Failed to run git add")?;

        if !add_output.status.success() {
            let stderr = String::from_utf8_lossy(&add_output.stderr);
            return Err(anyhow::anyhow!("Git add failed: {}", stderr));
        }

        // Create commit message
        let commit_message = self.generate_commit_message(session);

        let commit_output = Command::new("git")
            .args(["commit", "-m", &commit_message])
            .current_dir(&self.repo_path)
            .output()
            .context("Failed to run git commit")?;

        if !commit_output.status.success() {
            let stderr = String::from_utf8_lossy(&commit_output.stderr);
            return Err(anyhow::anyhow!("Git commit failed: {}", stderr));
        }

        // Get the commit hash
        let hash_output = Command::new("git")
            .args(["rev-parse", "HEAD"])
            .current_dir(&self.repo_path)
            .output()
            .context("Failed to get commit hash")?;

        let commit_hash = String::from_utf8_lossy(&hash_output.stdout).trim().to_string();
        Ok(commit_hash)
    }

    fn generate_commit_message(&self, session: &SessionMetadata) -> String {
        let mut message = format!(
            "Session: {} | {} | {}",
            session.id,
            session.methodology,
            session.project
        );

        if let Some(duration) = session.duration {
            let minutes = duration.num_minutes();
            message.push_str(&format!(" | {}m", minutes));
        }

        if let Some(energy) = session.creative_energy {
            message.push_str(&format!(" | Energy: {}/3", energy));
        }

        if !session.features_worked_on.is_empty() {
            message.push_str(&format!(" | Features: {}", session.features_worked_on.join(", ")));
        }

        message
    }

    pub fn show_log(&self, count: usize) -> Result<()> {
        let output = Command::new("git")
            .args([
                "log",
                "--oneline",
                "--graph",
                "--decorate",
                &format!("-{}", count),
            ])
            .current_dir(&self.repo_path)
            .output()
            .context("Failed to run git log")?;

        if !output.status.success() {
            let stderr = String::from_utf8_lossy(&output.stderr);
            return Err(anyhow::anyhow!("Git log failed: {}", stderr));
        }

        let log_output = String::from_utf8_lossy(&output.stdout);
        println!("{}", log_output);

        Ok(())
    }

    pub fn get_commit_count(&self) -> Result<usize> {
        let output = Command::new("git")
            .args(["rev-list", "--count", "HEAD"])
            .current_dir(&self.repo_path)
            .output()
            .context("Failed to get commit count")?;

        if !output.status.success() {
            return Ok(0);
        }

        let binding = String::from_utf8_lossy(&output.stdout);
        let count_str = binding.trim();
        count_str.parse::<usize>()
            .with_context(|| format!("Failed to parse commit count: {}", count_str))
    }

    pub fn get_recent_commits(&self, count: usize) -> Result<Vec<String>> {
        let output = Command::new("git")
            .args([
                "log",
                "--pretty=format:%H|%s|%ad",
                "--date=short",
                &format!("-{}", count),
            ])
            .current_dir(&self.repo_path)
            .output()
            .context("Failed to get recent commits")?;

        if !output.status.success() {
            return Ok(Vec::new());
        }

        let commits_output = String::from_utf8_lossy(&output.stdout);
        Ok(commits_output.lines().map(|line| line.to_string()).collect())
    }

    pub fn repo_path(&self) -> &Path {
        &self.repo_path
    }
}