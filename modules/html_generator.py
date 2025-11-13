"""
HTML Generator Module - Generate GitHub Pages for stock picks
"""
import os
from datetime import datetime
from .stock_codes import get_stock_name
from .logger import get_logger

logger = get_logger(__name__)


def generate_daily_html(picked_df, date_str, group1_codes, group2_codes,
                       chart1_url=None, chart2_url=None, output_dir="docs"):
    """
    Generate daily stock picks HTML page

    Args:
        picked_df: DataFrame with picked stocks
        date_str: Date string (YYYY-MM-DD)
        group1_codes: List of strong momentum stock codes
        group2_codes: List of potential stock codes
        chart1_url: URL for strong momentum chart (optional)
        chart2_url: URL for potential stocks chart (optional)
        output_dir: Output directory (default: docs)

    Returns:
        str: Path to generated HTML file
    """
    os.makedirs(output_dir, exist_ok=True)

    # Generate filename
    filename = f"{date_str}.html"
    filepath = os.path.join(output_dir, filename)

    # Generate HTML content
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>US Stock Picks - {date_str}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            padding: 40px;
        }}

        .header {{
            text-align: center;
            margin-bottom: 40px;
            padding-bottom: 30px;
            border-bottom: 3px solid #667eea;
        }}

        .header h1 {{
            font-size: 2.5em;
            color: #2d3748;
            margin-bottom: 10px;
        }}

        .header .date {{
            font-size: 1.2em;
            color: #718096;
            font-weight: 500;
        }}

        .section {{
            margin-bottom: 50px;
        }}

        .section-title {{
            font-size: 1.8em;
            color: #2d3748;
            margin-bottom: 20px;
            padding-left: 15px;
            border-left: 5px solid #667eea;
        }}

        .section.strong-momentum .section-title {{
            border-left-color: #48bb78;
        }}

        .section.potential .section-title {{
            border-left-color: #ed8936;
        }}

        .stock-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}

        .stock-card {{
            background: #f7fafc;
            border-radius: 12px;
            padding: 20px;
            border: 2px solid #e2e8f0;
            transition: all 0.3s ease;
        }}

        .stock-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 10px 25px rgba(0,0,0,0.1);
            border-color: #667eea;
        }}

        .stock-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }}

        .stock-code {{
            font-size: 1.4em;
            font-weight: bold;
            color: #2d3748;
        }}

        .stock-name {{
            font-size: 0.95em;
            color: #718096;
            margin-bottom: 15px;
        }}

        .stock-metrics {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
        }}

        .metric {{
            background: white;
            padding: 10px;
            border-radius: 8px;
            border: 1px solid #e2e8f0;
        }}

        .metric-label {{
            font-size: 0.75em;
            color: #a0aec0;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}

        .metric-value {{
            font-size: 1.1em;
            font-weight: 600;
            color: #2d3748;
            margin-top: 3px;
        }}

        .chart-container {{
            margin-top: 30px;
            text-align: center;
        }}

        .chart-container img {{
            max-width: 100%;
            border-radius: 12px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }}

        .no-stocks {{
            text-align: center;
            padding: 40px;
            color: #a0aec0;
            font-size: 1.1em;
        }}

        .back-link {{
            display: inline-block;
            margin-top: 30px;
            padding: 12px 24px;
            background: #667eea;
            color: white;
            text-decoration: none;
            border-radius: 8px;
            transition: all 0.3s ease;
        }}

        .back-link:hover {{
            background: #5568d3;
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }}

        @media (max-width: 768px) {{
            .container {{
                padding: 20px;
            }}

            .header h1 {{
                font-size: 1.8em;
            }}

            .stock-grid {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🇺🇸 US Stock Picks</h1>
            <div class="date">📅 {date_str}</div>
        </div>
"""

    # Strong Momentum Group
    if group1_codes:
        group1_df = picked_df[picked_df['code'].isin(group1_codes)]
        html_content += f"""
        <div class="section strong-momentum">
            <div class="section-title">🔥 Strong Momentum ({len(group1_codes)} stocks)</div>
            <div class="stock-grid">
"""
        for _, row in group1_df.iterrows():
            stock_name = get_stock_name(row['code'])
            html_content += f"""
                <div class="stock-card">
                    <div class="stock-header">
                        <div class="stock-code">{row['code']}</div>
                    </div>
                    <div class="stock-name">{stock_name}</div>
                    <div class="stock-metrics">
                        <div class="metric">
                            <div class="metric-label">Close</div>
                            <div class="metric-value">${row['close']:.2f}</div>
                        </div>
                        <div class="metric">
                            <div class="metric-label">MA20</div>
                            <div class="metric-value">${row['ma20']:.2f}</div>
                        </div>
                        <div class="metric">
                            <div class="metric-label">Slope</div>
                            <div class="metric-value">{row['ma20_slope']:.3f}</div>
                        </div>
                        <div class="metric">
                            <div class="metric-label">Volatility</div>
                            <div class="metric-value">{row['volatility']:.2f}%</div>
                        </div>
                    </div>
                </div>
"""
        html_content += """
            </div>
"""
        if chart1_url:
            html_content += f"""
            <div class="chart-container">
                <img src="{chart1_url}" alt="Strong Momentum Stocks Chart">
            </div>
"""
        html_content += """
        </div>
"""

    # Potential Stocks Group
    if group2_codes:
        group2_df = picked_df[picked_df['code'].isin(group2_codes)]
        html_content += f"""
        <div class="section potential">
            <div class="section-title">👀 Potential Stocks ({len(group2_codes)} stocks)</div>
            <div class="stock-grid">
"""
        for _, row in group2_df.iterrows():
            stock_name = get_stock_name(row['code'])
            html_content += f"""
                <div class="stock-card">
                    <div class="stock-header">
                        <div class="stock-code">{row['code']}</div>
                    </div>
                    <div class="stock-name">{stock_name}</div>
                    <div class="stock-metrics">
                        <div class="metric">
                            <div class="metric-label">Close</div>
                            <div class="metric-value">${row['close']:.2f}</div>
                        </div>
                        <div class="metric">
                            <div class="metric-label">MA20</div>
                            <div class="metric-value">${row['ma20']:.2f}</div>
                        </div>
                        <div class="metric">
                            <div class="metric-label">Slope</div>
                            <div class="metric-value">{row['ma20_slope']:.3f}</div>
                        </div>
                        <div class="metric">
                            <div class="metric-label">Volatility</div>
                            <div class="metric-value">{row['volatility']:.2f}%</div>
                        </div>
                    </div>
                </div>
"""
        html_content += """
            </div>
"""
        if chart2_url:
            html_content += f"""
            <div class="chart-container">
                <img src="{chart2_url}" alt="Potential Stocks Chart">
            </div>
"""
        html_content += """
        </div>
"""

    if not group1_codes and not group2_codes:
        html_content += """
        <div class="no-stocks">
            📊 No stocks meet the selection criteria today.
        </div>
"""

    html_content += """
        <div style="text-align: center;">
            <a href="index.html" class="back-link">← Back to All Picks</a>
        </div>
    </div>
</body>
</html>
"""

    # Write to file
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html_content)

    logger.info(f"Generated daily HTML: {filepath}")
    return filepath


def generate_index_html(history_data, output_dir="docs"):
    """
    Generate index page with all historical picks

    Args:
        history_data: List of dicts with date and counts
        output_dir: Output directory

    Returns:
        str: Path to generated index.html
    """
    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, "index.html")

    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>US Stocks Autobot - Historical Picks</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }

        .container {
            max-width: 1000px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            padding: 40px;
        }

        .header {
            text-align: center;
            margin-bottom: 40px;
        }

        .header h1 {
            font-size: 2.5em;
            color: #2d3748;
            margin-bottom: 10px;
        }

        .header p {
            font-size: 1.1em;
            color: #718096;
        }

        .picks-list {
            display: grid;
            gap: 15px;
        }

        .pick-card {
            background: #f7fafc;
            border-radius: 12px;
            padding: 20px;
            border: 2px solid #e2e8f0;
            transition: all 0.3s ease;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .pick-card:hover {
            transform: translateX(5px);
            border-color: #667eea;
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.2);
        }

        .pick-date {
            font-size: 1.3em;
            font-weight: bold;
            color: #2d3748;
        }

        .pick-stats {
            display: flex;
            gap: 20px;
            color: #718096;
        }

        .pick-stat {
            display: flex;
            align-items: center;
            gap: 5px;
        }

        .view-link {
            padding: 10px 20px;
            background: #667eea;
            color: white;
            text-decoration: none;
            border-radius: 8px;
            transition: all 0.3s ease;
        }

        .view-link:hover {
            background: #5568d3;
            transform: translateY(-2px);
        }

        .footer {
            margin-top: 40px;
            text-align: center;
            color: #a0aec0;
            padding-top: 20px;
            border-top: 2px solid #e2e8f0;
        }

        @media (max-width: 768px) {
            .pick-card {
                flex-direction: column;
                gap: 15px;
                text-align: center;
            }

            .pick-stats {
                flex-direction: column;
                gap: 10px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🇺🇸 US Stocks Autobot</h1>
            <p>Historical Stock Picks - Momentum-Based Selection</p>
        </div>

        <div class="picks-list">
"""

    # Add picks
    for item in sorted(history_data, key=lambda x: x['date'], reverse=True):
        html_content += f"""
            <div class="pick-card">
                <div class="pick-date">📅 {item['date']}</div>
                <div class="pick-stats">
                    <div class="pick-stat">
                        <span>🔥</span>
                        <span>{item.get('strong', 0)} Strong</span>
                    </div>
                    <div class="pick-stat">
                        <span>👀</span>
                        <span>{item.get('potential', 0)} Potential</span>
                    </div>
                    <div class="pick-stat">
                        <span>📊</span>
                        <span>{item.get('total', 0)} Total</span>
                    </div>
                </div>
                <a href="{item['date']}.html" class="view-link">View Details →</a>
            </div>
"""

    html_content += """
        </div>

        <div class="footer">
            <p>Generated by US Stocks Autobot | Updated automatically</p>
            <p style="margin-top: 10px;">⚠️ For educational purposes only. Not investment advice.</p>
        </div>
    </div>
</body>
</html>
"""

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html_content)

    logger.info(f"Generated index HTML: {filepath}")
    return filepath
