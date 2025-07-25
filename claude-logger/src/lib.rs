pub mod analyzer;
pub mod cli;
pub mod git;
pub mod logger;
pub mod patterns;
pub mod session;

pub use analyzer::{SessionAnalyzer, SessionSummary};
pub use cli::{Cli, Commands};
pub use git::GitRepo;
pub use logger::ClaudeLogger;
pub use patterns::{ConversationPatterns, SessionQuality};
pub use session::{AnalysisMetrics, Methodology, MethodologyStats, SessionMetadata, SessionsMetadata};