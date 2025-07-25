use crate::session::AnalysisMetrics;
use regex::Regex;
use std::sync::OnceLock;

pub struct ConversationPatterns {
    enthusiasm: Regex,
    confusion: Regex,
    compaction: Regex,
    code_blocks: Regex,
    exchanges: Regex,
    questions: Regex,
}

impl ConversationPatterns {
    pub fn new() -> Self {
        Self {
            enthusiasm: Regex::new(r"(?i)(excellent|great|perfect|amazing|awesome|fantastic|wonderful|brilliant|outstanding|superb|terrific|love it|exactly|precisely)").unwrap(),
            confusion: Regex::new(r"(?i)(confused|unclear|not sure|don't understand|what do you mean|can you clarify|help me understand|i'm lost|not following)").unwrap(),
            compaction: Regex::new(r"(?i)(concise|brief|short|summarize|compact|terse|reduce|minimize|streamline)").unwrap(),
            code_blocks: Regex::new(r"```[\s\S]*?```").unwrap(),
            exchanges: Regex::new(r"^(Human:|Assistant:)").unwrap(),
            questions: Regex::new(r"\?").unwrap(),
        }
    }

    pub fn analyze_content(&self, content: &str) -> AnalysisMetrics {
        AnalysisMetrics {
            exchanges: self.count_exchanges(content),
            code_blocks: self.count_code_blocks(content),
            questions_asked: self.count_questions(content),
            enthusiasm_markers: self.count_matches(&self.enthusiasm, content),
            confusion_markers: self.count_matches(&self.confusion, content),
            compaction_indicators: self.count_matches(&self.compaction, content),
        }
    }

    fn count_matches(&self, regex: &Regex, content: &str) -> usize {
        regex.find_iter(content).count()
    }

    fn count_exchanges(&self, content: &str) -> usize {
        content.lines()
            .filter(|line| self.exchanges.is_match(line))
            .count()
    }

    fn count_code_blocks(&self, content: &str) -> usize {
        self.code_blocks.find_iter(content).count()
    }

    fn count_questions(&self, content: &str) -> usize {
        // Count question marks but exclude those in code blocks
        let mut question_count = 0;
        let mut in_code_block = false;
        
        for line in content.lines() {
            if line.trim_start().starts_with("```") {
                in_code_block = !in_code_block;
                continue;
            }
            
            if !in_code_block {
                question_count += line.matches('?').count();
            }
        }
        
        question_count
    }
}

impl Default for ConversationPatterns {
    fn default() -> Self {
        Self::new()
    }
}

// Global instance using OnceLock for thread-safe lazy initialization
static PATTERNS: OnceLock<ConversationPatterns> = OnceLock::new();

pub fn get_patterns() -> &'static ConversationPatterns {
    PATTERNS.get_or_init(ConversationPatterns::new)
}

// Specialized pattern analysis functions
pub fn analyze_session_quality(content: &str) -> SessionQuality {
    let patterns = get_patterns();
    let metrics = patterns.analyze_content(content);
    
    SessionQuality::from_metrics(&metrics)
}

#[derive(Debug, Clone)]
pub struct SessionQuality {
    pub engagement_score: f64,
    pub clarity_score: f64,
    pub productivity_score: f64,
    pub overall_score: f64,
}

impl SessionQuality {
    pub fn from_metrics(metrics: &AnalysisMetrics) -> Self {
        let engagement_score = Self::calculate_engagement_score(metrics);
        let clarity_score = Self::calculate_clarity_score(metrics);
        let productivity_score = Self::calculate_productivity_score(metrics);
        let overall_score = (engagement_score + clarity_score + productivity_score) / 3.0;

        Self {
            engagement_score,
            clarity_score,
            productivity_score,
            overall_score,
        }
    }

    fn calculate_engagement_score(metrics: &AnalysisMetrics) -> f64 {
        let base_score = 50.0;
        let enthusiasm_bonus = (metrics.enthusiasm_markers as f64 * 10.0).min(30.0);
        let confusion_penalty = (metrics.confusion_markers as f64 * 5.0).min(20.0);
        let exchange_bonus = ((metrics.exchanges as f64 / 10.0) * 20.0).min(20.0);

        (base_score + enthusiasm_bonus + exchange_bonus - confusion_penalty).clamp(0.0, 100.0)
    }

    fn calculate_clarity_score(metrics: &AnalysisMetrics) -> f64 {
        let base_score = 70.0;
        let confusion_penalty = (metrics.confusion_markers as f64 * 10.0).min(40.0);
        let question_penalty = if metrics.questions_asked > metrics.exchanges {
            ((metrics.questions_asked - metrics.exchanges) as f64 * 2.0).min(20.0)
        } else {
            0.0
        };

        (base_score - confusion_penalty - question_penalty).clamp(0.0, 100.0)
    }

    fn calculate_productivity_score(metrics: &AnalysisMetrics) -> f64 {
        let base_score = 40.0;
        let code_bonus = (metrics.code_blocks as f64 * 15.0).min(40.0);
        let compaction_bonus = (metrics.compaction_indicators as f64 * 5.0).min(20.0);

        (base_score + code_bonus + compaction_bonus).clamp(0.0, 100.0)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_pattern_matching() {
        let patterns = ConversationPatterns::new();
        let content = r#"
Human: This is great! Can you help me with ```rust
fn main() {
    println!("Hello, world!");
}
```
Assistant: Sure\! This code creates a simple Hello World program.
"#;

        let metrics = patterns.analyze_content(content);
        
        assert_eq!(metrics.exchanges, 2);
        assert_eq!(metrics.code_blocks, 1);
        assert!(metrics.enthusiasm_markers > 0);
    }
}
