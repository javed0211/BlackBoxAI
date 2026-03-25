import json
import os
from typing import List, Dict, Any, Optional
from datetime import datetime

class ReportGenerator:
    """
    Generates premium, glass-morphic QA execution reports.
    Supports summary, AI analytics, steps, screenshots, videos, and error logs.
    """

    @staticmethod
    def generate_html(
        mission_input: str,
        success: bool,
        actions: List[Dict[str, Any]],
        analytics: Dict[str, Any],
        start_url: str,
        failure_analysis: Optional[str] = None,
        screenshots: List[str] = [],
        video_path: Optional[str] = None,
        trace_path: Optional[str] = None,
        console_logs: List[Dict[str, Any]] = [],
        network_logs: List[Dict[str, Any]] = []
    ) -> str:

        status_color = "#10b981" if success else "#ef4444"
        status_text = "PASSED" if success else "FAILED"
        status_icon = "✓" if success else "✗"
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Basic Glass-morphism CSS
        css = """
        :root {
            --primary: #10b981;
            --danger: #ef4444;
            --bg: #0f172a;
            --card-bg: rgba(30, 41, 59, 0.7);
            --border: rgba(255, 255, 255, 0.1);
            --text-main: #f8fafc;
            --text-dim: #94a3b8;
        }
        body {
            font-family: 'Inter', system-ui, -apple-system, sans-serif;
            background-color: var(--bg);
            color: var(--text-main);
            margin: 0;
            padding: 40px 20px;
            line-height: 1.5;
        }
        .container {
            max-width: 1000px;
            margin: 0 auto;
        }
        .glass-card {
            background: var(--card-bg);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid var(--border);
            border-radius: 24px;
            padding: 32px;
            margin-bottom: 24px;
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
        }
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 40px;
        }
        .status-badge {
            padding: 8px 20px;
            border-radius: 99px;
            font-weight: 700;
            font-size: 14px;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .status-passed { background: rgba(16, 185, 129, 0.2); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.3); }
        .status-failed { background: rgba(239, 68, 68, 0.2); color: #f87171; border: 1px solid rgba(239, 68, 68, 0.3); }
        
        h1 { font-size: 28px; font-weight: 800; margin: 0; color: #fff; }
        h2 { font-size: 20px; font-weight: 700; margin-top: 0; margin-bottom: 24px; color: #34d399; display: flex; align-items: center; gap: 10px; }
        .section-title { color: var(--text-dim); text-transform: uppercase; font-size: 12px; font-weight: 700; letter-spacing: 0.1em; margin-bottom: 16px; display: block; }
        
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; }
        .metric { background: rgba(255, 255, 255, 0.03); border-radius: 16px; padding: 16px; border: 1px solid var(--border); }
        .metric-label { font-size: 12px; color: var(--text-dim); display: block; margin-bottom: 4px; }
        .metric-value { font-size: 18px; font-weight: 700; color: #fff; }

        .analytics-tag { display: inline-flex; align-items: center; padding: 4px 12px; border-radius: 12px; background: rgba(59, 130, 246, 0.1); color: #60a5fa; border: 1px solid rgba(59, 130, 246, 0.2); font-size: 12px; font-weight: 600; margin-right: 8px; }

        table { width: 100%; border-collapse: separate; border-spacing: 0 8px; }
        th { text-align: left; padding: 12px 16px; color: var(--text-dim); font-size: 12px; font-weight: 600; text-transform: uppercase; }
        td { padding: 16px; background: rgba(255, 255, 255, 0.02); border-top: 1px solid var(--border); border-bottom: 1px solid var(--border); }
        td:first-child { border-left: 1px solid var(--border); border-top-left-radius: 12px; border-bottom-left-radius: 12px; }
        td:last-child { border-right: 1px solid var(--border); border-top-right-radius: 12px; border-bottom-right-radius: 12px; }
        
        .step-num { font-weight: 800; color: var(--text-dim); }
        .action-code { font-family: 'JetBrains Mono', monospace; font-size: 13px; color: #60a5fa; background: rgba(96, 165, 250, 0.1); padding: 4px 8px; border-radius: 6px; }
        .locator { font-size: 13px; color: #f472b6; }
        
        .error-box { background: rgba(239, 68, 68, 0.05); border: 1px solid rgba(239, 68, 68, 0.2); border-radius: 16px; padding: 20px; color: #f87171; font-family: 'JetBrains Mono', monospace; font-size: 13px; white-space: pre-wrap; margin-top: 16px; }
        
        .media-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px; margin-top: 24px; }
        .media-item { border-radius: 16px; overflow: hidden; border: 1px solid var(--border); position: relative; }
        .media-item img, .media-item video { width: 100%; display: block; }
        .media-label { position: absolute; bottom: 0; left: 0; right: 0; background: rgba(0,0,0,0.6); padding: 8px 12px; font-size: 12px; backdrop-filter: blur(4px); }

        .btn { display: inline-flex; align-items: center; gap: 8px; padding: 10px 20px; border-radius: 12px; font-weight: 600; font-size: 14px; text-decoration: none; transition: all 0.2s; }
        .btn-primary { background: #10b981; color: #000; }
        .btn-primary:hover { background: #34d399; transform: translateY(-2px); }
        .btn-outline { border: 1px solid var(--border); color: var(--text-main); }
        .btn-outline:hover { background: rgba(255,255,255,0.05); }
        """

        steps_html = ""
        for act in actions:
            steps_html += f"""
            <tr>
                <td class="step-num">{act.get('step_number')}</td>
                <td><span class="action-code">{act.get('action_type')}</span></td>
                <td class="locator">{act.get('target_locator')}</td>
                <td>{act.get('input_value')}</td>
                <td style="font-size: 13px; color: var(--text-dim);">{act.get('description')}</td>
            </tr>
            """

        media_html = ""
        if screenshots:
            for i, s in enumerate(screenshots):
                rel_path = os.path.basename(s)
                media_html += f"""
                <div class="media-item">
                    <img src="{rel_path}" alt="Screenshot {i+1}">
                    <div class="media-label">Step Screenshot {i+1}</div>
                </div>
                """
        
        if video_path:
            rel_video = os.path.basename(video_path)
            media_html += f"""
            <div class="media-item">
                <video controls><source src="{rel_video}" type="video/mp4"></video>
                <div class="media-label">Execution Recording</div>
            </div>
            """

        failure_html = ""
        if failure_analysis:
            failure_html = f"""
            <div class="glass-card" style="border-color: rgba(239, 68, 68, 0.3);">
                <span class="section-title">🚨 AI Failure Analysis</span>
                <div class="error-box">{failure_analysis}</div>
            </div>
            """

        diagnostics_html = ""
        if console_logs or network_logs:
            console_items = ""
            for log in console_logs:
                color = "#f87171" if log['type'] == 'error' else "#fbbf24"
                console_items += f'<div style="color: {color}; margin-bottom: 4px;">[{log["type"].upper()}] {log["text"]}</div>'
            
            network_items = ""
            for req in network_logs:
                network_items += f'<tr><td>{req["method"]}</td><td style="color: #f87171;">{req["status"]}</td><td style="font-size: 12px;">{req["url"][:80]}...</td></tr>'

            diagnostics_html = f"""
            <div class="glass-card">
                <span class="section-title">🧠 Advanced Diagnostics</span>
                <div class="grid" style="grid-template-columns: 1fr 1fr;">
                    <div>
                        <h4 style="font-size: 14px; margin-bottom: 12px; color: #fbbf24;">JS Console Feed</h4>
                        <div class="error-box" style="margin-top: 0; background: rgba(0,0,0,0.2); max-height: 200px; overflow-y: auto;">
                            {console_items if console_items else 'No errors detected.'}
                        </div>
                    </div>
                    <div>
                        <h4 style="font-size: 14px; margin-bottom: 12px; color: #f87171;">Failed Network Calls</h4>
                        <div style="font-size: 12px; background: rgba(0,0,0,0.2); border-radius: 12px; padding: 12px; border: 1px solid var(--border);">
                            <table style="margin: 0;">
                                <thead><tr><th>MET</th><th>ST</th><th>URL</th></tr></thead>
                                <tbody>{network_items if network_items else '<tr><td colspan="3">Clean network traffic.</td></tr>'}</tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
            """

        links_html = ""

        if trace_path:
            rel_trace = os.path.basename(trace_path)
            links_html += f'<a href="{rel_trace}" class="btn btn-outline">📥 Download Trace</a>'

        html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Nexus AI | QA Report</title>
            <style>{css}</style>
            <link rel="preconnect" href="https://fonts.googleapis.com">
            <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
            <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&family=JetBrains+Mono&display=swap" rel="stylesheet">
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <div>
                        <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 8px;">
                            <span style="font-weight: 900; letter-spacing: -0.02em; font-size: 20px; color: #34d399;">NEXUS AI</span>
                            <span style="color: var(--text-dim); font-size: 20px;">/</span>
                            <span style="font-weight: 500; color: var(--text-dim); font-size: 14px;">QA AGENT PLATFORM</span>
                        </div>
                        <h1>Mission: {mission_input[:60]}{'...' if len(mission_input) > 60 else ''}</h1>
                        <p style="color: var(--text-dim); font-size: 14px; margin-top: 8px;">Executed on {timestamp} • <a href="{start_url}" style="color: #60a5fa; text-decoration: none;">{start_url}</a></p>
                    </div>
                    <div class="status-badge status-{'passed' if success else 'failed'}">
                        <span style="font-size: 18px;">{status_icon}</span> {status_text}
                    </div>
                </div>

                <div class="glass-card">
                    <span class="section-title">📊 Execution Stats</span>
                    <div class="grid">
                        <div class="metric">
                            <span class="metric-label">Execution Time</span>
                            <span class="metric-value">{analytics.get('duration', 'N/A')}s</span>
                        </div>
                        <div class="metric">
                            <span class="metric-label">Steps Completed</span>
                            <span class="metric-value">{len(actions)}</span>
                        </div>
                        <div class="metric">
                            <span class="metric-label">Token Usage</span>
                            <span class="metric-value">{analytics.get('total_tokens', 0):,}</span>
                        </div>
                        <div class="metric">
                            <span class="metric-label">API Cost</span>
                            <span class="metric-value">${analytics.get('total_cost', 0):.4f}</span>
                        </div>
                    </div>
                    <div style="margin-top: 24px;">
                        <span class="analytics-tag">Azure GPT-4o-mini</span>
                        <span class="analytics-tag">Playwright v1.42+</span>
                        <span class="analytics-tag">Self-Healing Enabled</span>
                    </div>
                </div>

                {failure_html}
                {diagnostics_html}

                <div class="glass-card">

                    <span class="section-title">📑 Execution Log</span>
                    <div style="overflow-x: auto;">
                        <table>
                            <thead>
                                <tr>
                                    <th>#</th>
                                    <th>Action</th>
                                    <th>Locator</th>
                                    <th>Value</th>
                                    <th>Details</th>
                                </tr>
                            </thead>
                            <tbody>
                                {steps_html}
                            </tbody>
                        </table>
                    </div>
                </div>

                <div class="glass-card">
                    <span class="section-title">🎬 Media Artifacts</span>
                    <div class="media-grid">
                        {media_html}
                    </div>
                    <div style="margin-top: 32px; display: flex; gap: 12px;">
                        {links_html}
                        <a href="#" class="btn btn-primary" onclick="window.print()">🖨️ Print PDF Report</a>
                    </div>
                </div>

                <div style="text-align: center; color: var(--text-dim); font-size: 12px; margin-top: 40px;">
                    Generated by Nexus AI Autonomous Browser Agent • Security Policy: SEC-402 Compliant
                </div>
            </div>
        </body>
        </html>
        """
        return html
