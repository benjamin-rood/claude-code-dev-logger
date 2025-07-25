use chrono::{DateTime, Duration, Utc};
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::path::PathBuf;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SessionMetadata {
    pub id: String,
    pub timestamp: DateTime<Utc>,
    pub project: String,
    pub methodology: Methodology,
    pub working_directory: PathBuf,
    pub command: String,
    pub log_file: PathBuf,
    pub duration: Option<Duration>,
    pub end_time: Option<DateTime<Utc>>,
    pub features_worked_on: Vec<String>,
    pub creative_energy: Option<u8>,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq, Hash)]
pub enum Methodology {
    ContextDriven,
    CommandBased,
    Unknown,
}

impl std::fmt::Display for Methodology {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            Methodology::ContextDriven => write!(f, "Context-Driven"),
            Methodology::CommandBased => write!(f, "Command-Based"),
            Methodology::Unknown => write!(f, "Unknown"),
        }
    }
}

#[derive(Debug, Clone)]
pub struct AnalysisMetrics {
    pub exchanges: usize,
    pub code_blocks: usize,
    pub questions_asked: usize,
    pub enthusiasm_markers: usize,
    pub confusion_markers: usize,
    pub compaction_indicators: usize,
}

impl Default for AnalysisMetrics {
    fn default() -> Self {
        Self {
            exchanges: 0,
            code_blocks: 0,
            questions_asked: 0,
            enthusiasm_markers: 0,
            confusion_markers: 0,
            compaction_indicators: 0,
        }
    }
}

#[derive(Debug, Clone)]
pub struct MethodologyStats {
    pub sessions: usize,
    pub total_duration: Duration,
    pub avg_duration: Duration,
    pub creative_energy: Vec<u8>,
    pub avg_energy: Option<f64>,
    pub metrics: AnalysisMetrics,
}

impl MethodologyStats {
    pub fn new() -> Self {
        Self {
            sessions: 0,
            total_duration: Duration::zero(),
            avg_duration: Duration::zero(),
            creative_energy: Vec::new(),
            avg_energy: None,
            metrics: AnalysisMetrics::default(),
        }
    }

    pub fn add_session(&mut self, session: &SessionMetadata, metrics: AnalysisMetrics) {
        self.sessions += 1;
        
        if let Some(duration) = session.duration {
            self.total_duration = self.total_duration + duration;
            self.avg_duration = self.total_duration / self.sessions as i32;
        }

        if let Some(energy) = session.creative_energy {
            self.creative_energy.push(energy);
            let avg = self.creative_energy.iter().map(|&x| x as f64).sum::<f64>() 
                / self.creative_energy.len() as f64;
            self.avg_energy = Some(avg);
        }

        // Aggregate metrics
        self.metrics.exchanges += metrics.exchanges;
        self.metrics.code_blocks += metrics.code_blocks;
        self.metrics.questions_asked += metrics.questions_asked;
        self.metrics.enthusiasm_markers += metrics.enthusiasm_markers;
        self.metrics.confusion_markers += metrics.confusion_markers;
        self.metrics.compaction_indicators += metrics.compaction_indicators;
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SessionsMetadata {
    pub sessions: HashMap<String, SessionMetadata>,
}

impl SessionsMetadata {
    pub fn new() -> Self {
        Self {
            sessions: HashMap::new(),
        }
    }

    pub fn add_session(&mut self, session: SessionMetadata) {
        self.sessions.insert(session.id.clone(), session);
    }

    pub fn get_session(&self, id: &str) -> Option<&SessionMetadata> {
        self.sessions.get(id)
    }

    pub fn get_session_mut(&mut self, id: &str) -> Option<&mut SessionMetadata> {
        self.sessions.get_mut(id)
    }

    pub fn sessions_by_methodology(&self) -> HashMap<Methodology, Vec<&SessionMetadata>> {
        let mut result = HashMap::new();
        
        for session in self.sessions.values() {
            result.entry(session.methodology.clone())
                .or_insert_with(Vec::new)
                .push(session);
        }
        
        result
    }
}

impl Default for SessionsMetadata {
    fn default() -> Self {
        Self::new()
    }
}