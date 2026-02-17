# GHOSTMAP 👻🗺️

**Discover undocumented API endpoints before attackers do.**

GHOSTMAP is an Application Security tool that discovers "ghost" API endpoints — routes that exist in production but are missing from documentation, forgotten after refactors, or left behind as debug/admin backdoors.

## Why GHOSTMAP?

| Feature | 👻 GHOSTMAP | 🔨 Gobuster / Ffuf | 🕰️ Waybackurls |
| :--- | :--- | :--- | :--- |
| **Discovery Method** | **Hybrid** (Archive + Fuzzing) | Brute-force only | Archive only |
| **Context Awareness** | **Smart** (Detects Tech Stack) | Blind (User must guess wordlists) | N/A |
| **Ghost Detection** | **✅ Yes** (Compares w/ Swagger) | ❌ No | ❌ No |
| **WAF Evasion** | **✅ Auto-Throttling & Retries** | ❌ Manual tuning required | ❌ No |
| **False Positives** | **✅ Low** (Soft 404 Detection) | ❌ High (Needs manual filtering) | ❌ High |
| **Report Generation** | **✅ Interactive HTML/PDF** | ❌ Text output only | ❌ Text output only |

## Key Features
- **👻 The "Ghost" Concept**: Finds *undocumented* endpoints by comparing against Swagger/OpenAPI specs.
- **🧠 Smart Fuzzing**: Detects tech stack (Spring Boot, WordPress, etc.) and fuzzes relevant paths only.
- **🛡️ WAF Evasion**: Automatically detects WAFs (Cloudflare, Akamai) and adjusts rate limits.
- **🛡️ Soft 404 Detection**: Filters out "fake" 200 OK responses to reduce noise.

## How It Works

1. **Collect** — Scrape public internet archives (Wayback Machine, CommonCrawl) and JavaScript files to build a historical endpoint footprint
2. **Sanitize** — Strip sensitive data (tokens, emails, session IDs) for safe internal transfer
3. **Audit** — Compare collected endpoints against internal documentation (Git, Swagger/OpenAPI), probe for active ghost endpoints
4. **Report** — Generate risk-scored reports and interactive dashboards

## Quick Start

```bash
pip install -r requirements.txt

# (Optional) Edit config.yaml for custom settings
# ghostmap collect -d example.com  <-- Auto-loads config.yaml

# Collect public footprint
ghostmap collect --domain targetcompany.com --output public_footprint.json

# Sanitize for internal transfer
ghostmap sanitize --input public_footprint.json --output sanitized_footprint.json

# Audit against internal docs
ghostmap audit --input sanitized_footprint.json --swagger api-docs.yaml --output audit_results.json

# Launch dashboard
ghostmap dashboard --input audit_results.json

# Generate PDF report
ghostmap report --input audit_results.json --output ghost_report.pdf
```

## Risk Levels

| Color  | Meaning               |
|--------|----------------------|
| 🟢 Green  | Documented & expected |
| 🟡 Yellow | Suspicious / unclear  |
| 🔴 Red    | Ghost endpoint — HIGH RISK |

## 🔒 Security & Privacy

GHOSTMAP is designed for sensitive internal assessments:
- **No Telemetry**: The tool does **not** send any data to the developers or third parties.
- **Local Data**: All scan results and footprints are stored locally in the `scans/` folder.
- **Air-Gap Friendly**: The `audit` mode works offline (provided you have the target IP reachable). The `collect` mode requires internet access only to fetch public archives (Wayback/CommonCrawl).

## License

MIT
