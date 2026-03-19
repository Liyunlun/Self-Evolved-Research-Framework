#!/usr/bin/env python3
"""
Skill usage statistics analyzer - incremental processing
Extract Skill usage data from LLM invocation records and generate a statistics
report for /skill-evolve.

Features:
1. Incrementally scan new invocation records (avoid reprocessing)
2. Extract Skill calls, token usage, and user satisfaction
3. Generate a structured JSON report
4. Compute variant win rates and recommendations

Usage:
  python scripts/skill_analyzer.py

Output:
  logs/analysis/skills_stats.json  - latest statistics
  logs/analysis/last_processed.txt - last processed position (incremental)
"""

import os
import re
import json
import yaml
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from typing import Dict, List, Any, Optional

# ============ Configuration ============

PROJECT_ROOT = Path(__file__).parent.parent
LOGS_DIR = PROJECT_ROOT / "logs"
RESEARCH_SKILLS_DIR = LOGS_DIR / "research_skills"
ANALYSIS_DIR = LOGS_DIR / "analysis"
VARIANTS_DIR = PROJECT_ROOT / "skills" / "variants"

# Skill ID mapping (unique identifiers)
SKILL_IDS = {
    # Meta-layer Skills
    "research-init": "meta_001",
    "background-builder": "meta_002",
    "method-designer": "meta_003",
    "progress": "meta_004",
    "review": "meta_005",
    "skill-evolve": "meta_006",
    "proposal-generator": "meta_007",

    # Object-layer Skills (theory research)
    "problem-decompose": "research_001",
    "cross-domain-search": "research_002",
    "counterexample": "research_003",
    "proof-refine": "research_004",
    "formal-proof": "research_005",
    "symbolic-verify": "research_006",
    "complexity-analysis": "research_007",
    "theorem-generalize": "research_008",
    "paper-writing": "research_009",
    "peer-review": "research_010",
    "research-workflow": "research_workflow",
}

# Reverse mapping
ID_TO_SKILL = {v: k for k, v in SKILL_IDS.items()}

# ============ Data Structures ============

class SkillStats:
    """Statistics for a single Skill."""
    def __init__(self, skill_id: str, skill_name: str):
        self.skill_id = skill_id
        self.skill_name = skill_name
        self.total_calls = 0
        self.token_consumption = []
        self.satisfaction_scores = []
        self.last_called = None
        self.variants_used = defaultdict(int)  # variant_name -> count
        self.variants_wins = defaultdict(int)  # variant_name -> wins

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        avg_token = sum(self.token_consumption) / len(self.token_consumption) if self.token_consumption else 0
        avg_satisfaction = sum(self.satisfaction_scores) / len(self.satisfaction_scores) if self.satisfaction_scores else 0

        return {
            "skill_id": self.skill_id,
            "skill_name": self.skill_name,
            "total_calls": self.total_calls,
            "last_called": self.last_called,
            "token_stats": {
                "total": sum(self.token_consumption),
                "average": round(avg_token, 0),
                "min": min(self.token_consumption) if self.token_consumption else 0,
                "max": max(self.token_consumption) if self.token_consumption else 0,
                "samples": len(self.token_consumption)
            },
            "satisfaction": {
                "average": round(avg_satisfaction, 2),
                "scores": self.satisfaction_scores,
                "count": len(self.satisfaction_scores)
            },
            "variants": {
                "usage": dict(self.variants_used),
                "wins": dict(self.variants_wins)
            }
        }

# ============ Core Functions ============

def ensure_dirs():
    """Ensure required directories exist."""
    ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)
    for skill_name in SKILL_IDS.keys():
        skill_dir = RESEARCH_SKILLS_DIR / skill_name
        skill_dir.mkdir(parents=True, exist_ok=True)

def get_last_processed_position() -> Optional[str]:
    """Get the last processed position (incremental)."""
    marker_file = ANALYSIS_DIR / "last_processed.txt"
    if marker_file.exists():
        return marker_file.read_text().strip()
    return None

def save_processed_position(position: str):
    """Save the current processed position."""
    marker_file = ANALYSIS_DIR / "last_processed.txt"
    marker_file.write_text(position)

def scan_skill_logs() -> Dict[str, SkillStats]:
    """Scan all Skill log files."""
    stats = {}

    for skill_name, skill_id in SKILL_IDS.items():
        stats[skill_id] = SkillStats(skill_id, skill_name)
        skill_dir = RESEARCH_SKILLS_DIR / skill_name

        if not skill_dir.exists():
            continue

        # Scan all log files for this Skill
        for log_file in skill_dir.glob("*.yaml"):
            try:
                data = yaml.safe_load(log_file.read_text())

                # Extract statistics
                stats[skill_id].total_calls += 1

                if "token_consumption" in data:
                    token = data["token_consumption"]
                    if isinstance(token, dict) and "actual" in token:
                        stats[skill_id].token_consumption.append(token["actual"])
                    elif isinstance(token, int):
                        stats[skill_id].token_consumption.append(token)

                if "user_satisfaction" in data:
                    stats[skill_id].satisfaction_scores.append(data["user_satisfaction"])

                if "timestamp" in data:
                    timestamp = data["timestamp"]
                    if not stats[skill_id].last_called or timestamp > stats[skill_id].last_called:
                        stats[skill_id].last_called = timestamp

                # Extract variant usage
                if "variant_used" in data:
                    variant = data["variant_used"]
                    stats[skill_id].variants_used[variant] += 1

                # Extract variant wins/losses (if present)
                if "variant_winner" in data:
                    winner = data["variant_winner"]
                    stats[skill_id].variants_wins[winner] += 1

            except Exception as e:
                print(f"Warning: Failed to parse {log_file}: {e}")
                continue

    return stats

def load_variant_configs() -> Dict[str, Any]:
    """Load existing variant configurations."""
    variants = {}

    if not VARIANTS_DIR.exists():
        return variants

    for variant_file in VARIANTS_DIR.glob("*.yaml"):
        try:
            skill_name = variant_file.stem
            data = yaml.safe_load(variant_file.read_text())
            variants[skill_name] = data
        except Exception as e:
            print(f"Warning: Failed to load variant config {variant_file}: {e}")

    return variants

def calculate_recommendations(stats: Dict[str, SkillStats]) -> List[Dict[str, Any]]:
    """Generate recommendations from statistics."""
    recommendations = []

    # Define thresholds
    HIGH_FREQUENCY_THRESHOLD = 10  # calls >= 10 counts as high frequency
    LOW_SATISFACTION_THRESHOLD = 3.5  # average satisfaction < 3.5 needs improvement

    for skill_id, stat in stats.items():
        # Skip unused Skills
        if stat.total_calls == 0:
            continue

        # High-frequency usage with no variants -> recommend creating variants
        if stat.total_calls >= HIGH_FREQUENCY_THRESHOLD and not stat.variants_used:
            recommendations.append({
                "skill_id": skill_id,
                "skill_name": stat.skill_name,
                "type": "create_variant",
                "priority": "high",
                "reason": f"High-frequency usage ({stat.total_calls} calls); recommend creating variants to provide more options"
            })

        # Low satisfaction -> recommend optimization
        avg_satisfaction = sum(stat.satisfaction_scores) / len(stat.satisfaction_scores) if stat.satisfaction_scores else 0
        if avg_satisfaction > 0 and avg_satisfaction < LOW_SATISFACTION_THRESHOLD:
            recommendations.append({
                "skill_id": skill_id,
                "skill_name": stat.skill_name,
                "type": "optimize",
                "priority": "high",
                "reason": f"User satisfaction is low ({avg_satisfaction:.1f}/5); improvement is needed"
            })

        # Variant win-rate analysis
        if stat.variants_used:
            total_variant_uses = sum(stat.variants_used.values())
            for variant, count in stat.variants_used.items():
                usage_rate = count / total_variant_uses
                win_rate = stat.variants_wins.get(variant, 0) / count if count > 0 else 0

                # Low-win-rate variants -> recommend retiring or improving them
                if count >= 5 and win_rate < 0.3:
                    recommendations.append({
                        "skill_id": skill_id,
                        "skill_name": stat.skill_name,
                        "type": "variant_retire",
                        "priority": "medium",
                        "variant": variant,
                        "reason": f"Variant '{variant}' has a low win rate ({win_rate:.1%}); consider retiring or improving it"
                    })

    return recommendations

def generate_report(stats: Dict[str, SkillStats], recommendations: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Generate the full statistics report."""
    # Group by category
    meta_skills = {}
    research_skills = {}

    for skill_id, stat in stats.items():
        stat_dict = stat.to_dict()
        if skill_id.startswith("meta_"):
            meta_skills[skill_id] = stat_dict
        elif skill_id.startswith("research_"):
            research_skills[skill_id] = stat_dict

    # Compute overall statistics
    total_calls = sum(s.total_calls for s in stats.values())
    total_tokens = sum(sum(s.token_consumption) for s in stats.values())

    report = {
        "generated_at": datetime.now().isoformat(),
        "summary": {
            "total_skills": len(stats),
            "total_calls": total_calls,
            "total_tokens": total_tokens,
            "meta_skills_count": len(meta_skills),
            "research_skills_count": len(research_skills)
        },
        "meta_skills": meta_skills,
        "research_skills": research_skills,
        "recommendations": recommendations,
        "top_used_skills": sorted(
            [{"skill_id": sid, "skill_name": s.skill_name, "calls": s.total_calls}
             for sid, s in stats.items()],
            key=lambda x: x["calls"],
            reverse=True
        )[:10]
    }

    return report

def save_report(report: Dict[str, Any]):
    """Save the report to a file."""
    output_file = ANALYSIS_DIR / "skills_stats.json"
    output_file.write_text(json.dumps(report, indent=2, ensure_ascii=False))
    print(f"✓ Statistics report saved: {output_file}")

# ============ Main Program ============

def main():
    """Main entry point."""
    print("=" * 60)
    print("Skill Usage Statistics Analyzer v1.0")
    print("=" * 60)

    # 1. Ensure directories exist
    print("\n[1/5] Checking directory structure...")
    ensure_dirs()
    print("  ✓ Directory structure is ready")

    # 2. Scan Skill logs
    print("\n[2/5] Scanning Skill invocation logs...")
    stats = scan_skill_logs()
    active_skills = [s for s in stats.values() if s.total_calls > 0]
    print(f"  ✓ Found {len(active_skills)} active Skills ({len(stats)} total)")

    # 3. Load variant configurations
    print("\n[3/5] Loading variant configurations...")
    variants = load_variant_configs()
    print(f"  ✓ Loaded {len(variants)} variant configurations")

    # 4. Generate recommendations
    print("\n[4/5] Analyzing data and generating recommendations...")
    recommendations = calculate_recommendations(stats)
    print(f"  ✓ Generated {len(recommendations)} improvement recommendations")

    # 5. Generate and save report
    print("\n[5/5] Generating statistics report...")
    report = generate_report(stats, recommendations)
    save_report(report)

    # Show summary
    print("\n" + "=" * 60)
    print("Statistics Summary")
    print("=" * 60)
    print(f"Total calls: {report['summary']['total_calls']}")
    print(f"Total token usage: {report['summary']['total_tokens']:,}")
    print(f"\nMost-used Skills:")
    for i, skill in enumerate(report['top_used_skills'][:5], 1):
        if skill['calls'] > 0:
            print(f"  {i}. {skill['skill_name']}: {skill['calls']} calls")

    if recommendations:
        print(f"\nImprovement Recommendations:")
        for rec in recommendations[:5]:
            print(f"  • [{rec['priority'].upper()}] {rec['skill_name']}: {rec['reason']}")

    print("\n✓ Analysis complete!")
    print(f"Detailed report: logs/analysis/skills_stats.json")

if __name__ == "__main__":
    main()
