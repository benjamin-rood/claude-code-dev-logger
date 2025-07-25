use claude_logger::{Cli, ClaudeLogger, Commands, SessionAnalyzer};
use clap::Parser;
use std::process;

fn main() {
    let cli = Cli::parse();

    if let Err(e) = run_cli(cli) {
        eprintln!("Error: {}", e);
        process::exit(1);
    }
}

fn run_cli(cli: Cli) -> anyhow::Result<()> {
    match cli.command {
        Some(Commands::Analyze { methodology, comparative }) => {
            let analyzer = SessionAnalyzer::new()?;
            
            if comparative {
                analyzer.generate_report()?;
            } else if let Some(method_filter) = methodology {
                println!("Analyzing sessions with methodology: {}", method_filter);
                let stats = analyzer.compare_methodologies()?;
                
                // Find matching methodology and display its stats
                for (method, stat) in stats {
                    if method.to_string().to_lowercase().contains(&method_filter.to_lowercase()) {
                        println!("=== {} Analysis ===", method);
                        println!("Sessions: {}", stat.sessions);
                        if let Some(avg_energy) = stat.avg_energy {
                            println!("Average Creative Energy: {:.1}/3", avg_energy);
                        }
                        println!("Total Exchanges: {}", stat.metrics.exchanges);
                        println!("Code Blocks: {}", stat.metrics.code_blocks);
                        break;
                    }
                }
            } else {
                analyzer.generate_report()?;
            }
        }
        
        Some(Commands::List { methodology, limit }) => {
            let logger = ClaudeLogger::new()?;
            let sessions = logger.list_sessions(methodology.as_deref(), limit);
            
            if sessions.is_empty() {
                println!("No sessions found.");
                return Ok(());
            }

            println!("=== Recent Sessions ===");
            for session in sessions {
                print!("{} | {} | {} | {}", 
                    session.id, 
                    session.methodology, 
                    session.project,
                    session.timestamp.format("%Y-%m-%d %H:%M")
                );
                
                if let Some(duration) = session.duration {
                    print!(" | {}m", duration.num_minutes());
                }
                
                if let Some(energy) = session.creative_energy {
                    print!(" | Energy: {}/3", energy);
                }
                
                println!();
            }
        }
        
        Some(Commands::GitLog { count }) => {
            let logger = ClaudeLogger::new()?;
            logger.git_repo().show_log(count)?;
        }
        
        Some(Commands::Show { session_id, full }) => {
            let analyzer = SessionAnalyzer::new()?;
            let summary = analyzer.get_session_summary(&session_id)?;
            
            summary.print_summary();
            
            if full {
                println!("\n=== Full Log Content ===");
                let content = std::fs::read_to_string(&summary.session.log_file)?;
                println!("{}", content);
            }
        }
        
        None => {
            // Run Claude with logging
            let mut logger = ClaudeLogger::new()?;
            logger.run_logged_session(&cli.claude_args, cli.track_energy)?;
        }
    }

    Ok(())
}
