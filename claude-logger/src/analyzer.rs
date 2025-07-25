use crate::patterns::{analyze_session_quality, get_patterns, SessionQuality};
use crate::session::{AnalysisMetrics, Methodology, MethodologyStats, SessionMetadata, SessionsMetadata};
use anyhow::{Context, Result};
use std::collections::HashMap;
use std::fs;
use std::path::{Path, PathBuf};

pub struct SessionAnalyzer {
    logs_dir: PathBuf,
    metadata: SessionsMetadata,
}

impl SessionAnalyzer {
    pub fn new() -> Result<Self> {
        let logs_dir = Self::get_logs_directory()?;
        Self::new_with_dir(&logs_dir)
    }

    pub fn new_with_dir(logs_dir: &Path) -> Result<Self> {
        let metadata_file = logs_dir.join("sessions_metadata.json");
        let metadata = Self::load_metadata(&metadata_file)?;

        Ok(Self {
            logs_dir: logs_dir.to_path_buf(),
            metadata,
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

    pub fn analyze_log_file(&self, log_path: &Path) -> Result<AnalysisMetrics> {
        let content = fs::read_to_string(log_path)
            .with_context(|| format!("Failed to read log file: {}", log_path.display()))?;

        let patterns = get_patterns();
        Ok(patterns.analyze_content(&content))
    }

    pub fn analyze_session(&self, session_id: &str) -> Result<(AnalysisMetrics, SessionQuality)> {
        let session = self.metadata.get_session(session_id)
            .context("Session not found")?;

        let metrics = self.analyze_log_file(&session.log_file)?;
        let quality = analyze_session_quality(&fs::read_to_string(&session.log_file)?);

        Ok((metrics, quality))
    }

    pub fn compare_methodologies(&self) -> Result<HashMap<Methodology, MethodologyStats>> {
        let mut methodology_stats = HashMap::new();

        for (methodology, sessions) in self.metadata.sessions_by_methodology() {
            let mut stats = MethodologyStats::new();

            for session in sessions {
                if session.log_file.exists() {
                    match self.analyze_log_file(&session.log_file) {
                        Ok(metrics) => stats.add_session(session, metrics),
                        Err(e) => {
                            eprintln!("Warning: Failed to analyze session {}: {}", session.id, e);
                        }
                    }
                } else {
                    eprintln!("Warning: Log file not found for session {}", session.id);
                }
            }

            methodology_stats.insert(methodology, stats);
        }

        Ok(methodology_stats)
    }

    pub fn generate_report(&self) -> Result<()> {
        println!("=== Claude Code Session Analysis Report ===\n");

        let methodology_stats = self.compare_methodologies()?;

        if methodology_stats.is_empty() {
            println!("No sessions found for analysis.");
            return Ok(());
        }

        // Overall statistics
        let total_sessions: usize = methodology_stats.values().map(|stats| stats.sessions).sum();
        println!("Total Sessions Analyzed: {}\n", total_sessions);

        // Methodology comparison
        println!("=== Methodology Comparison ===");
        for (methodology, stats) in &methodology_stats {
            if stats.sessions == 0 {
                continue;
            }

            println!("\n{} Sessions:", methodology);
            println!("  Sessions: {}", stats.sessions);
            
            if stats.avg_duration.num_minutes() > 0 {
                println!("  Average Duration: {} minutes", stats.avg_duration.num_minutes());
                println!("  Total Duration: {} minutes", stats.total_duration.num_minutes());
            }

            if let Some(avg_energy) = stats.avg_energy {
                println!("  Average Creative Energy: {:.1}/3", avg_energy);
            }

            println!("  Conversation Metrics:");
            println!("    Total Exchanges: {}", stats.metrics.exchanges);
            println!("    Code Blocks: {}", stats.metrics.code_blocks);
            println!("    Questions Asked: {}", stats.metrics.questions_asked);
            println!("    Enthusiasm Markers: {}", stats.metrics.enthusiasm_markers);
            println!("    Confusion Markers: {}", stats.metrics.confusion_markers);
            println!("    Compaction Indicators: {}", stats.metrics.compaction_indicators);

            // Calculate derived metrics
            if stats.sessions > 0 {
                let avg_exchanges = stats.metrics.exchanges as f64 / stats.sessions as f64;
                let avg_code_blocks = stats.metrics.code_blocks as f64 / stats.sessions as f64;
                println!("  Average per Session:");
                println!("    Exchanges: {:.1}", avg_exchanges);
                println!("    Code Blocks: {:.1}", avg_code_blocks);
            }
        }

        // Quality analysis
        println!("\n=== Session Quality Analysis ===");
        self.generate_quality_report(&methodology_stats)?;

        // Recommendations
        println!("\n=== Recommendations ===");
        self.generate_recommendations(&methodology_stats);

        Ok(())
    }

    fn generate_quality_report(&self, methodology_stats: &HashMap<Methodology, MethodologyStats>) -> Result<()> {
        for (methodology, stats) in methodology_stats {
            if stats.sessions == 0 {
                continue;
            }

            println!("\n{} Quality Metrics:", methodology);
            
            // Sample a few sessions for detailed quality analysis
            let sessions_by_methodology = self.metadata.sessions_by_methodology();
            if let Some(sessions) = sessions_by_methodology.get(methodology) {
                let mut quality_scores = Vec::new();

                for session in sessions.iter().take(5) { // Sample first 5 sessions
                    if let Ok(content) = fs::read_to_string(&session.log_file) {
                        let quality = analyze_session_quality(&content);
                        quality_scores.push(quality);
                    }
                }

                if !quality_scores.is_empty() {
                    let avg_engagement = quality_scores.iter().map(|q| q.engagement_score).sum::<f64>() / quality_scores.len() as f64;
                    let avg_clarity = quality_scores.iter().map(|q| q.clarity_score).sum::<f64>() / quality_scores.len() as f64;
                    let avg_productivity = quality_scores.iter().map(|q| q.productivity_score).sum::<f64>() / quality_scores.len() as f64;
                    let avg_overall = quality_scores.iter().map(|q| q.overall_score).sum::<f64>() / quality_scores.len() as f64;

                    println!("  Average Engagement Score: {:.1}/100", avg_engagement);
                    println!("  Average Clarity Score: {:.1}/100", avg_clarity);
                    println!("  Average Productivity Score: {:.1}/100", avg_productivity);
                    println!("  Average Overall Score: {:.1}/100", avg_overall);
                }
            }
        }

        Ok(())
    }

    fn generate_recommendations(&self, methodology_stats: &HashMap<Methodology, MethodologyStats>) {
        let mut recommendations = Vec::new();

        // Find the methodology with highest engagement
        let best_methodology = methodology_stats
            .iter()
            .filter(|(_, stats)| stats.sessions > 0)
            .max_by(|(_, a), (_, b)| {
                let a_score = if let Some(energy) = a.avg_energy { energy } else { 0.0 };
                let b_score = if let Some(energy) = b.avg_energy { energy } else { 0.0 };
                a_score.partial_cmp(&b_score).unwrap_or(std::cmp::Ordering::Equal)
            });

        if let Some((methodology, stats)) = best_methodology {
            if let Some(avg_energy) = stats.avg_energy {
                if avg_energy > 2.0 {
                    recommendations.push(format!(
                        "Continue using {} methodology - it shows high creative energy ({:.1}/3)",
                        methodology, avg_energy
                    ));
                }
            }
        }

        // Check for confusion patterns
        for (methodology, stats) in methodology_stats {
            if stats.sessions > 0 {
                let confusion_rate = stats.metrics.confusion_markers as f64 / stats.sessions as f64;
                if confusion_rate > 2.0 {
                    recommendations.push(format!(
                        "Consider clearer requirements when using {} - high confusion rate ({:.1} per session)",
                        methodology, confusion_rate
                    ));
                }
            }
        }

        // Check for productivity patterns
        for (methodology, stats) in methodology_stats {
            if stats.sessions > 0 {
                let code_rate = stats.metrics.code_blocks as f64 / stats.sessions as f64;
                if code_rate > 5.0 {
                    recommendations.push(format!(
                        "{} shows high code productivity ({:.1} blocks per session)",
                        methodology, code_rate
                    ));
                }
            }
        }

        if recommendations.is_empty() {
            println!("No specific recommendations - continue logging sessions for better insights.");
        } else {
            for (i, recommendation) in recommendations.iter().enumerate() {
                println!("{}. {}", i + 1, recommendation);
            }
        }
    }

    pub fn get_session_summary(&self, session_id: &str) -> Result<SessionSummary> {
        let session = self.metadata.get_session(session_id)
            .context("Session not found")?;

        let (metrics, quality) = self.analyze_session(session_id)?;

        Ok(SessionSummary {
            session: session.clone(),
            metrics,
            quality,
        })
    }

    pub fn metadata(&self) -> &SessionsMetadata {
        &self.metadata
    }
}

#[derive(Debug)]
pub struct SessionSummary {
    pub session: SessionMetadata,
    pub metrics: AnalysisMetrics,
    pub quality: SessionQuality,
}

impl SessionSummary {
    pub fn print_summary(&self) {
        println!("=== Session Summary: {} ===", self.session.id);
        println!("Project: {}", self.session.project);
        println!("Methodology: {}", self.session.methodology);
        println!("Timestamp: {}", self.session.timestamp.format("%Y-%m-%d %H:%M:%S UTC"));
        
        if let Some(duration) = self.session.duration {
            println!("Duration: {} minutes", duration.num_minutes());
        }

        if let Some(energy) = self.session.creative_energy {
            println!("Creative Energy: {}/3", energy);
        }

        println!("\nConversation Metrics:");
        println!("  Exchanges: {}", self.metrics.exchanges);
        println!("  Code Blocks: {}", self.metrics.code_blocks);
        println!("  Questions Asked: {}", self.metrics.questions_asked);
        println!("  Enthusiasm Markers: {}", self.metrics.enthusiasm_markers);
        println!("  Confusion Markers: {}", self.metrics.confusion_markers);
        println!("  Compaction Indicators: {}", self.metrics.compaction_indicators);

        println!("\nQuality Scores:");
        println!("  Engagement: {:.1}/100", self.quality.engagement_score);
        println!("  Clarity: {:.1}/100", self.quality.clarity_score);
        println!("  Productivity: {:.1}/100", self.quality.productivity_score);
        println!("  Overall: {:.1}/100", self.quality.overall_score);
    }
}