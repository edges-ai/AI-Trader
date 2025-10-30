#!/usr/bin/env python3
"""
Analyze trading agent performance metrics

Usage:
    python tools/analyze_agent.py momentum-nasdaq-conservative
    python tools/analyze_agent.py gpt-5
    python tools/analyze_agent.py --list
"""

import argparse
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

from tools.result_tools import (
    calculate_and_save_metrics,
    get_available_date_range,
    print_performance_report
)


def list_available_agents():
    """List all available agent signatures with data"""
    data_dir = project_root / "data" / "agent_data"

    if not data_dir.exists():
        print("No agent data directory found")
        return []

    agents = []
    for agent_dir in data_dir.iterdir():
        if agent_dir.is_dir():
            position_file = agent_dir / "position" / "position.jsonl"
            if position_file.exists():
                start_date, end_date = get_available_date_range(agent_dir.name)
                agents.append({
                    "signature": agent_dir.name,
                    "start_date": start_date,
                    "end_date": end_date
                })

    return agents


def analyze_agent(signature: str, start_date: str = None, end_date: str = None):
    """Analyze performance for a specific agent"""

    # Check if agent data exists
    position_file = project_root / "data" / "agent_data" / signature / "position" / "position.jsonl"

    if not position_file.exists():
        print(f"❌ No data found for agent: {signature}")
        print(f"   Expected file: {position_file}")
        print("\nAvailable agents:")
        for agent in list_available_agents():
            print(f"  - {agent['signature']} ({agent['start_date']} to {agent['end_date']})")
        return False

    print(f"📊 Analyzing Agent: {signature}")
    print("=" * 80)

    # Get date range if not provided
    if not start_date or not end_date:
        auto_start, auto_end = get_available_date_range(signature)
        start_date = start_date or auto_start
        end_date = end_date or auto_end
        print(f"Date Range: {start_date} to {end_date}\n")

    # Calculate and display metrics
    metrics = calculate_and_save_metrics(
        modelname=signature,
        start_date=start_date,
        end_date=end_date,
        print_report=True
    )

    print("\n" + "=" * 80)
    print(f"✅ Analysis complete for {signature}")
    print(f"📁 Metrics saved to: data/agent_data/{signature}/metrics/")

    return True


def main():
    parser = argparse.ArgumentParser(
        description="Analyze trading agent performance",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze momentum agent
  python tools/analyze_agent.py momentum-nasdaq-conservative

  # Analyze specific date range
  python tools/analyze_agent.py gpt-5 --start 2025-10-01 --end 2025-10-15

  # List all available agents
  python tools/analyze_agent.py --list
        """
    )

    parser.add_argument(
        "signature",
        nargs="?",
        help="Agent signature to analyze (e.g., momentum-nasdaq-conservative)"
    )
    parser.add_argument(
        "--start",
        help="Start date (YYYY-MM-DD)"
    )
    parser.add_argument(
        "--end",
        help="End date (YYYY-MM-DD)"
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List all available agents"
    )

    args = parser.parse_args()

    # List available agents
    if args.list:
        print("📋 Available Agents:")
        print("=" * 80)
        agents = list_available_agents()
        if not agents:
            print("No agents with data found")
        else:
            for agent in agents:
                print(f"\n🤖 {agent['signature']}")
                print(f"   Date Range: {agent['start_date']} to {agent['end_date']}")
        return

    # Require signature if not listing
    if not args.signature:
        parser.print_help()
        print("\n❌ Error: signature required (use --list to see available agents)")
        sys.exit(1)

    # Analyze agent
    success = analyze_agent(args.signature, args.start, args.end)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
