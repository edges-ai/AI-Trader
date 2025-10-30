#!/usr/bin/env python3
"""
Compare performance metrics across multiple trading agents

Usage:
    python tools/compare_strategies.py
    python tools/compare_strategies.py momentum-nasdaq-conservative gpt-5 claude-3.7-sonnet
    python tools/compare_strategies.py --all
"""

import argparse
import sys
import os
from pathlib import Path
from typing import List, Dict
import json

# Add project root to path
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

from tools.result_tools import (
    calculate_all_metrics,
    get_available_date_range
)


def get_all_agents() -> List[str]:
    """Get all available agent signatures"""
    data_dir = project_root / "data" / "agent_data"

    if not data_dir.exists():
        return []

    agents = []
    for agent_dir in data_dir.iterdir():
        if agent_dir.is_dir():
            position_file = agent_dir / "position" / "position.jsonl"
            if position_file.exists():
                agents.append(agent_dir.name)

    return sorted(agents)


def format_percentage(value: float, decimals: int = 2) -> str:
    """Format as percentage"""
    if value is None:
        return "N/A"
    return f"{value * 100:.{decimals}f}%"


def format_number(value: float, decimals: int = 2) -> str:
    """Format number with decimals"""
    if value is None:
        return "N/A"
    return f"{value:.{decimals}f}"


def format_currency(value: float) -> str:
    """Format as currency"""
    if value is None:
        return "N/A"
    return f"${value:,.2f}"


def compare_agents(signatures: List[str], start_date: str = None, end_date: str = None):
    """Compare performance across multiple agents"""

    if not signatures:
        print("❌ No agents to compare")
        return

    print("📊 Multi-Agent Performance Comparison")
    print("=" * 120)

    # Collect metrics for all agents
    all_metrics = []
    for signature in signatures:
        position_file = project_root / "data" / "agent_data" / signature / "position" / "position.jsonl"

        if not position_file.exists():
            print(f"⚠️  Skipping {signature} (no data found)")
            continue

        # Get date range
        auto_start, auto_end = get_available_date_range(signature)
        use_start = start_date or auto_start
        use_end = end_date or auto_end

        print(f"📈 Calculating metrics for {signature} ({use_start} to {use_end})...")

        try:
            metrics = calculate_all_metrics(
                modelname=signature,
                start_date=use_start,
                end_date=use_end
            )
            metrics['signature'] = signature
            all_metrics.append(metrics)
        except Exception as e:
            print(f"⚠️  Error calculating metrics for {signature}: {e}")
            continue

    if not all_metrics:
        print("❌ No valid metrics calculated")
        return

    print("\n" + "=" * 120)
    print("\n📋 PERFORMANCE SUMMARY")
    print("=" * 120)

    # Print header
    header = f"{'Agent':<35} {'Return':<12} {'Sharpe':<10} {'Max DD':<12} {'Volatility':<12} {'Win Rate':<10} {'Trades':<8}"
    print(header)
    print("-" * 120)

    # Sort by Sharpe ratio (descending)
    sorted_metrics = sorted(all_metrics, key=lambda x: x.get('sharpe_ratio', -999), reverse=True)

    # Print each agent's metrics
    for metrics in sorted_metrics:
        sig = metrics['signature'][:34]  # Truncate if too long
        cum_return = format_percentage(metrics.get('cumulative_return'))
        sharpe = format_number(metrics.get('sharpe_ratio'), 3)
        max_dd = format_percentage(metrics.get('max_drawdown'))
        volatility = format_percentage(metrics.get('volatility'))
        win_rate = format_percentage(metrics.get('win_rate'))
        num_trades = metrics.get('num_trades', 'N/A')

        row = f"{sig:<35} {cum_return:<12} {sharpe:<10} {max_dd:<12} {volatility:<12} {win_rate:<10} {num_trades:<8}"
        print(row)

    print("=" * 120)

    # Print detailed comparison
    print("\n📊 DETAILED METRICS COMPARISON")
    print("=" * 120)

    metric_names = [
        ('cumulative_return', 'Cumulative Return', format_percentage),
        ('annualized_return', 'Annualized Return', format_percentage),
        ('sharpe_ratio', 'Sharpe Ratio', lambda x: format_number(x, 3)),
        ('max_drawdown', 'Max Drawdown', format_percentage),
        ('volatility', 'Volatility', format_percentage),
        ('win_rate', 'Win Rate', format_percentage),
        ('profit_loss_ratio', 'Profit/Loss Ratio', lambda x: format_number(x, 2)),
        ('num_trades', 'Number of Trades', str),
        ('final_portfolio_value', 'Final Portfolio Value', format_currency),
    ]

    for metric_key, metric_label, formatter in metric_names:
        print(f"\n{metric_label}:")
        values = [(m['signature'], m.get(metric_key)) for m in sorted_metrics]

        for sig, value in values:
            formatted_value = formatter(value)
            print(f"  {sig:<40} {formatted_value}")

    print("\n" + "=" * 120)

    # Determine winner
    if sorted_metrics:
        winner = sorted_metrics[0]
        print(f"\n🏆 BEST RISK-ADJUSTED PERFORMANCE (by Sharpe Ratio):")
        print(f"   {winner['signature']}")
        print(f"   Sharpe Ratio: {format_number(winner.get('sharpe_ratio'), 3)}")
        print(f"   Return: {format_percentage(winner.get('cumulative_return'))}")
        print(f"   Max Drawdown: {format_percentage(winner.get('max_drawdown'))}")

    print("\n" + "=" * 120)


def main():
    parser = argparse.ArgumentParser(
        description="Compare performance across multiple trading agents",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Compare all available agents
  python tools/compare_strategies.py --all

  # Compare specific agents
  python tools/compare_strategies.py momentum-nasdaq-conservative value-nasdaq alpha-nasdaq

  # Compare with custom date range
  python tools/compare_strategies.py --all --start 2025-10-01 --end 2025-10-15
        """
    )

    parser.add_argument(
        "signatures",
        nargs="*",
        help="Agent signatures to compare"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Compare all available agents"
    )
    parser.add_argument(
        "--start",
        help="Start date (YYYY-MM-DD)"
    )
    parser.add_argument(
        "--end",
        help="End date (YYYY-MM-DD)"
    )

    args = parser.parse_args()

    # Determine which agents to compare
    if args.all:
        signatures = get_all_agents()
        if not signatures:
            print("❌ No agents found")
            sys.exit(1)
        print(f"🔍 Found {len(signatures)} agents to compare\n")
    elif args.signatures:
        signatures = args.signatures
    else:
        # Default: compare all available
        signatures = get_all_agents()
        if not signatures:
            print("❌ No agents found")
            parser.print_help()
            sys.exit(1)
        print(f"🔍 No agents specified, comparing all {len(signatures)} available agents\n")

    # Run comparison
    compare_agents(signatures, args.start, args.end)


if __name__ == "__main__":
    main()
