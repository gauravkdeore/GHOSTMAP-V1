import json
from pathlib import Path
from rich.console import Console

console = Console()

class HTMLReportGenerator:
    """Generates a standalone interactive HTML report."""

    def generate(self, audit_data: dict, output_path: str):
        """
        Creates an HTML file with embedded JSON data and a JS table.
        """
        json_str = json.dumps(audit_data)
        
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GHOSTMAP Scan Report</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #f4f4f9; color: #333; margin: 0; padding: 20px; }}
        .header {{ background: #1a1a2e; color: #fff; padding: 20px; border-radius: 8px; margin-bottom: 20px; }}
        .header h1 {{ margin: 0; }}
        .summary {{ display: flex; gap: 20px; margin-bottom: 20px; }}
        .card {{ background: #fff; padding: 15px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); flex: 1; text-align: center; }}
        .card h3 {{ margin: 0 0 10px 0; color: #666; font-size: 0.9em; text-transform: uppercase; }}
        .card .value {{ font-size: 2em; font-weight: bold; }}
        .high {{ color: #e74c3c; }}
        .medium {{ color: #f39c12; }}
        .low {{ color: #27ae60; }}
        
        table {{ width: 100%; border-collapse: collapse; background: #fff; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
        th, td {{ padding: 12px 15px; text-align: left; border-bottom: 1px solid #eee; }}
        th {{ background: #f8f9fa; font-weight: 600; color: #555; }}
        tr:hover {{ background: #f1f1f1; }}
        .badge {{ padding: 4px 8px; border-radius: 4px; font-size: 0.8em; font-weight: bold; text-transform: uppercase; }}
        .badge-HIGH {{ background: #fadbd8; color: #c0392b; }}
        .badge-MEDIUM {{ background: #fdebd0; color: #d35400; }}
        .badge-LOW {{ background: #d4efdf; color: #27ae60; }}
        
        .search-box {{ margin-bottom: 20px; width: 100%; padding: 10px; font-size: 1em; border: 1px solid #ddd; border-radius: 8px; box-sizing: border-box; }}
    </style>
</head>
<body>

<div class="header">
    <h1>👻 GHOSTMAP Report</h1>
    <p>Target: {audit_data['meta'].get('input_file', 'Unknown')}</p>
    <p>Generated: {audit_data['meta'].get('timestamp', '')}</p>
</div>

<div class="summary">
    <div class="card"><h3 class="high">High Risk</h3><div class="value high" id="count-high">0</div></div>
    <div class="card"><h3 class="medium">Medium Risk</h3><div class="value medium" id="count-medium">0</div></div>
    <div class="card"><h3 class="low">Low Risk</h3><div class="value low" id="count-low">0</div></div>
    <div class="card"><h3>Total Endpoints</h3><div class="value" id="count-total">0</div></div>
</div>

<div class="filters">
    <input type="text" id="searchInput" class="search-box" placeholder="🔍 Search URL, Source, or Details...">
    
    <select id="riskFilter" class="filter-select">
        <option value="">All Risks</option>
        <option value="HIGH">High Only</option>
        <option value="MEDIUM">Medium Only</option>
        <option value="LOW">Low Only</option>
    </select>

    <select id="statusFilter" class="filter-select">
        <option value="">All Statuses</option>
        <option value="200">200 OK</option>
        <option value="301">301/302/307 Redirect</option>
        <option value="403">401/403 Auth Required</option>
        <option value="404">404 (Why is this here?)</option>
        <option value="500">500 Errors</option>
    </select>
</div>

<style>
    .filters {{ display: flex; gap: 10px; margin-bottom: 20px; }}
    .search-box {{ flex: 2; padding: 10px; font-size: 1em; border: 1px solid #ddd; border-radius: 8px; }}
    .filter-select {{ flex: 1; padding: 10px; font-size: 1em; border: 1px solid #ddd; border-radius: 8px; background: #fff; }}
</style>

<table id="resultsTable">
    <thead>
        <tr>
            <th>Endpoint</th>
            <th>Method</th>
            <th>Status</th>
            <th>Risk</th>
            <th>Source</th>
            <th>Detected Tech/Details</th>
        </tr>
    </thead>
    <tbody>
        <!-- JS will populate this -->
    </tbody>
</table>

<script>
    const data = {json_str};
    const endpoints = data.endpoints || [];
    const summary = data.summary || {{}};

    // Update Summary
    document.getElementById('count-high').innerText = summary.high_risk || 0;
    document.getElementById('count-medium').innerText = summary.medium_risk || 0;
    document.getElementById('count-low').innerText = summary.low_risk || 0;
    document.getElementById('count-total').innerText = endpoints.length;

    const tbody = document.querySelector('#resultsTable tbody');
    const searchInput = document.getElementById('searchInput');
    const riskFilter = document.getElementById('riskFilter');
    const statusFilter = document.getElementById('statusFilter');
    
    // Safely get base URL
    const baseUrl = data.meta && data.meta.base_url ? data.meta.base_url.replace(/\\/$/, "") : "";

    function renderTable() {{
        tbody.innerHTML = "";
        const filterText = searchInput.value.toLowerCase();
        const riskVal = riskFilter.value;
        const statusVal = statusFilter.value;
        
        endpoints.forEach(ep => {{
            let url = ep.endpoint || ep.url || "";
            // Fix relative URLs
            let displayUrl = url;
            let href = url;
            
            if (url && !url.startsWith("http") && baseUrl) {{
                // Remove leading slash from url if present
                const cleanPath = url.startsWith("/") ? url.substring(1) : url;
                href = `${{baseUrl}}/${{cleanPath}}`;
            }}

            const method = ep.method || "GET";
            const status = ep.status || ep.status_codes?.[0] || 0;
            const risk = ep.risk_level || "UNKNOWN";
            const source = ep.source || ep.sources?.[0] || "unknown";
            
            // Text Filter
            if (filterText && !url.toLowerCase().includes(filterText) && !source.toLowerCase().includes(filterText)) {{
                return;
            }}

            // Risk Filter
            if (riskVal && risk !== riskVal) {{
                return;
            }}

            // Status Filter Logic
            if (statusVal) {{
                const s = parseInt(status);
                if (statusVal === "200" && s !== 200) return;
                if (statusVal === "301" && ![301, 302, 307, 308].includes(s)) return;
                if (statusVal === "403" && ![401, 403].includes(s)) return;
                if (statusVal === "500" && s < 500) return;
            }}

            const row = document.createElement('tr');
            
            let details = "";
            if (ep.risk_factors) {{
                details = ep.risk_factors.map(f => f.detail).join(", ");
            }}
            if (ep.source === "ghost_fuzzer" && ep.payload) {{
                details += ` [Payload: ${{ep.payload}}]`;
            }}
            if (ep.is_soft_404) {{
                 details += " (Soft 404)";
                 row.style.opacity = "0.6";
            }}

            row.innerHTML = `
                <td><a href="${{href}}" target="_blank">${{displayUrl}}</a></td>
                <td>${{method}}</td>
                <td>${{status}}</td>
                <td><span class="badge badge-${{risk}}">${{risk}}</span></td>
                <td>${{source}}</td>
                <td>${{details}}</td>
            `;
            tbody.appendChild(row);
        }});
    }}

    renderTable();

    searchInput.addEventListener('input', renderTable);
    riskFilter.addEventListener('change', renderTable);
    statusFilter.addEventListener('change', renderTable);
</script>

</body>
</html>
"""
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        
        console.print(f"[bold green]✅ HTML Report saved to {output_path}[/bold green]")
