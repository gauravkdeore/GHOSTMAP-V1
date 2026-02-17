# GHOSTMAP 👻🗺️

**Discover undocumented API endpoints before attackers do.**

GHOSTMAP is an Application Security tool that discovers "ghost" API endpoints — routes that exist in production but are missing from documentation, forgotten after refactors, or left behind as debug/admin backdoors.

## How It Works

1. **Collect** — Scrape public internet archives (Wayback Machine, CommonCrawl) and JavaScript files to build a historical endpoint footprint
2. **Sanitize** — Strip sensitive data (tokens, emails, session IDs) for safe internal transfer
3. **Audit** — Compare collected endpoints against internal documentation (Git, Swagger/OpenAPI), probe for active ghost endpoints
4. **Report** — Generate risk-scored reports and interactive dashboards

## Quick Start

```bash
pip install -r requirements.txt

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

## License

MIT
