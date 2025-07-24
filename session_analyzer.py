#!/usr/bin/env python3
"""
Analyze Claude conversation logs to compare methodologies
"""
import json
import re
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import statistics

class SessionAnalyzer:
    def __init__(self):
        self.logs_dir = Path.home() / ".claude-logs"
        self.metadata_file = self.logs_dir / "sessions_metadata.json"
        self.load_metadata()
    
    def load_metadata(self):
        """Load session metadata"""
        if self.metadata_file.exists():
            with open(self.metadata_file, 'r') as f:
                self.metadata = json.load(f)
        else:
            self.metadata = {"sessions": []}
    
    def analyze_log_file(self, log_path):
        """Extract metrics from a single log file"""
        with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        metrics = {
            "exchanges": 0,
            "human_messages": [],
            "claude_messages": [],
            "code_blocks": 0,
            "questions_asked": 0,
            "clarifications": 0,
            "enthusiasm_markers": 0,
            "confusion_markers": 0,
            "compaction_indicators": 0
        }
        
        # Pattern matching for conversation analysis
        # This is simplified - real implementation would be more sophisticated
        
        # Count exchanges (Human: / Assistant: patterns)
        human_pattern = r'Human:|You:|User:'
        assistant_pattern = r'Assistant:|Claude:|AI:'
        
        metrics["exchanges"] = len(re.findall(human_pattern, content, re.IGNORECASE))
        
        # Count code blocks
        metrics["code_blocks"] = len(re.findall(r'```', content))
        
        # Count questions (? at end of line)
        metrics["questions_asked"] = len(re.findall(r'\?[\s\n]', content))
        
        # Enthusiasm markers
        enthusiasm_patterns = [
            r'excellent!', r'great!', r'perfect!', r'fantastic!',
            r'love it', r'this is great', r'😊', r'🎉'
        ]
        for pattern in enthusiasm_patterns:
            metrics["enthusiasm_markers"] += len(re.findall(pattern, content, re.IGNORECASE))
        
        # Confusion markers
        confusion_patterns = [
            r"that's not", r"hmm", r"wait", r"actually no",
            r"let me clarify", r"I meant", r"not quite"
        ]
        for pattern in confusion_patterns:
            metrics["confusion_markers"] += len(re.findall(pattern, content, re.IGNORECASE))
        
        # Compaction indicators
        compaction_patterns = [
            r"as we discussed", r"as mentioned", r"remember when",
            r"earlier you said", r"previously we"
        ]
        for pattern in compaction_patterns:
            metrics["compaction_indicators"] += len(re.findall(pattern, content, re.IGNORECASE))
        
        return metrics
    
    def compare_methodologies(self):
        """Compare command-based vs context-driven approaches"""
        methodology_stats = defaultdict(lambda: {
            "sessions": 0,
            "total_duration": 0,
            "avg_duration": 0,
            "creative_energy": [],
            "exchanges": [],
            "code_blocks": [],
            "enthusiasm": [],
            "confusion": [],
            "compaction": []
        })
        
        for session in self.metadata["sessions"]:
            methodology = session.get("methodology", "unknown")
            stats = methodology_stats[methodology]
            
            stats["sessions"] += 1
            
            if session.get("duration"):
                stats["total_duration"] += session["duration"]
            
            if session.get("creative_energy"):
                stats["creative_energy"].append(session["creative_energy"])
            
            # Analyze log file if it exists
            log_file = Path(session["log_file"])
            if log_file.exists():
                metrics = self.analyze_log_file(log_file)
                stats["exchanges"].append(metrics["exchanges"])
                stats["code_blocks"].append(metrics["code_blocks"])
                stats["enthusiasm"].append(metrics["enthusiasm_markers"])
                stats["confusion"].append(metrics["confusion_markers"])
                stats["compaction"].append(metrics["compaction_indicators"])
        
        # Calculate averages
        for methodology, stats in methodology_stats.items():
            if stats["sessions"] > 0:
                stats["avg_duration"] = stats["total_duration"] / stats["sessions"]
                
                if stats["creative_energy"]:
                    stats["avg_energy"] = statistics.mean(stats["creative_energy"])
                
                for metric in ["exchanges", "code_blocks", "enthusiasm", "confusion", "compaction"]:
                    if stats[metric]:
                        stats[f"avg_{metric}"] = statistics.mean(stats[metric])
        
        return methodology_stats
    
    def generate_report(self):
        """Generate comparison report"""
        stats = self.compare_methodologies()
        
        print("\n" + "=" * 60)
        print("CLAUDE CONVERSATION ANALYSIS REPORT")
        print("=" * 60 + "\n")
        
        for methodology, data in stats.items():
            if data["sessions"] == 0:
                continue
                
            print(f"📊 Methodology: {methodology.upper()}")
            print(f"   Sessions: {data['sessions']}")
            print(f"   Avg Duration: {data['avg_duration']:.1f} seconds")
            
            if 'avg_energy' in data:
                energy_display = "🔋" * int(data['avg_energy'])
                print(f"   Avg Creative Energy: {energy_display} ({data['avg_energy']:.1f}/3)")
            
            if 'avg_exchanges' in data:
                print(f"   Avg Exchanges: {data['avg_exchanges']:.1f}")
            
            if 'avg_code_blocks' in data:
                print(f"   Avg Code Blocks: {data['avg_code_blocks']:.1f}")
            
            if 'avg_enthusiasm' in data:
                print(f"   Enthusiasm Markers: {data['avg_enthusiasm']:.1f}")
            
            if 'avg_confusion' in data:
                print(f"   Confusion Markers: {data['avg_confusion']:.1f}")
            
            if 'avg_compaction' in data:
                print(f"   Compaction Events: {data['avg_compaction']:.1f}")
            
            print()
        
        # Direct comparison if both methodologies present
        if "context-driven" in stats and "command-based" in stats:
            print("\n" + "=" * 60)
            print("DIRECT COMPARISON")
            print("=" * 60 + "\n")
            
            ctx = stats["context-driven"]
            cmd = stats["command-based"]
            
            if 'avg_energy' in ctx and 'avg_energy' in cmd:
                energy_diff = ctx['avg_energy'] - cmd['avg_energy']
                if energy_diff > 0:
                    print(f"✨ Context-driven shows {energy_diff:.1f} higher creative energy")
                elif energy_diff < 0:
                    print(f"✨ Command-based shows {-energy_diff:.1f} higher creative energy")
                else:
                    print("✨ Both approaches show equal creative energy")
            
            print()
            
            # Show which approach had more of each metric
            metrics_comparison = [
                ("exchanges", "Conversation Depth"),
                ("code_blocks", "Code Generation"),
                ("enthusiasm", "Joy/Enthusiasm"),
                ("confusion", "Confusion/Clarification"),
                ("compaction", "Context Loss")
            ]
            
            for metric, label in metrics_comparison:
                ctx_val = ctx.get(f'avg_{metric}', 0)
                cmd_val = cmd.get(f'avg_{metric}', 0)
                
                if ctx_val > cmd_val:
                    pct = ((ctx_val - cmd_val) / cmd_val * 100) if cmd_val > 0 else 100
                    print(f"📈 {label}: Context-driven {pct:.0f}% higher")
                elif cmd_val > ctx_val:
                    pct = ((cmd_val - ctx_val) / ctx_val * 100) if ctx_val > 0 else 100
                    print(f"📈 {label}: Command-based {pct:.0f}% higher")
                else:
                    print(f"📈 {label}: Equal in both approaches")

def main():
    analyzer = SessionAnalyzer()
    analyzer.generate_report()

if __name__ == "__main__":
    main()