"""
Utility functions for building CLAUDE.md files from shared sections.
"""

from pathlib import Path


def build_claude_md(
    strategy_name: str,
    strategy_framework: str,
    risk_rules: dict,
    base_sections: list = None
) -> str:
    """
    Build CLAUDE.md content by combining shared base sections with strategy-specific content.

    Args:
        strategy_name: Name of the strategy (e.g., "Momentum")
        strategy_framework: Strategy methodology markdown
        risk_rules: Dictionary of risk parameters
        base_sections: List of section names to include (default: all)

    Returns:
        Complete CLAUDE.md content as string
    """
    if base_sections is None:
        base_sections = ['base', 'data_formats', 'tools', 'decision_format']

    instructions_dir = Path(__file__).parent

    # Start with strategy title
    content = f"# {strategy_name} Agent for NASDAQ 100\n\n"

    # Add shared sections
    for section in base_sections:
        section_file = instructions_dir / f"{section}.md"
        if section_file.exists():
            content += section_file.read_text(encoding='utf-8')
            content += "\n\n"

    # Add strategy-specific methodology
    content += f"## {strategy_name} Strategy Methodology\n\n"
    content += strategy_framework
    content += "\n\n"

    # Add risk management section
    content += "## Risk Management Rules\n\n"
    content += f"- **Max position size**: {risk_rules['max_position']*100:.0f}% of portfolio\n"
    content += f"- **Minimum cash buffer**: {risk_rules['min_cash']*100:.0f}% of portfolio\n"
    content += f"- **Stop loss threshold**: {risk_rules['stop_loss']*100:.0f}% drawdown\n"
    content += f"- **Maximum positions**: {risk_rules['max_positions']} stocks\n"
    content += f"- **Minimum confidence**: {risk_rules['confidence_threshold']*100:.0f}% to trade\n"
    content += "\n"

    return content


__all__ = ['build_claude_md']
