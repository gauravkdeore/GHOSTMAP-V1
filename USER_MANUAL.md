# 👻 GHOSTMAP User Manual

**GhostMap** helps you find hidden, forgotten, or undocumented API endpoints that attackers might exploit.


## 📋 Installation & Prerequisites

**Requirements:**
- Python 3.8 or higher
- Internet access (for `collect` mode only)

**Install Dependences:**
```bash
git clone https://github.com/your-repo/ghostmap.git
cd ghostmap
pip install -r requirements.txt
```

## 🚀 Quick Start
Run from the root directory:
```bash
python -m ghostmap.cli --help
```


---

## ⚙️ Configuration

GHOSTMAP is designed to be turnkey. A default `config.yaml` file is included in the project root.

**1. Auto-Loading (Recommended)**
GHOSTMAP **automatically loads** `config.yaml` (or `config.json`) if it exists in your current folder. You don't need to pass any flags.
- Just edit the `config.yaml` file to change settings like `rate_limit` or `verbose`.
- Run your commands normally:
  ```bash
  python -m ghostmap.cli collect -d example.com
  ```

**2. Manual Override**
If you have multiple config files (e.g., `fast_scan.yaml`, `stealth_scan.yaml`), you can specify one explicitly:
```bash
python -m ghostmap.cli collect -d example.com --config fast_scan.yaml
```

**Configuration Reference (`config.yaml`):**
```yaml
# --- HTTP Client ---
rate_limit: 2.0             # Max requests per second (default: 2.0)
request_timeout: 30         # Timeout in seconds (default: 30)
max_retries: 3              # Max retries for failed requests
retry_backoff: 1.5          # Exponential backoff factor
headers:                    # Custom global headers
  Authorization: "Bearer xyz"

# --- Collector (Scraping) ---
wayback_timeout: 60
max_js_file_size: 5242880   # 5MB max JS file size

# --- Auditor (Scanning) ---
probe_concurrency: 10       # Simultaneous threads for probing
probe_timeout: 10
probe_methods:              # HTTP methods to use for probing
  - "HEAD"
  - "GET"

# --- Risk Scoring ---
weight_undocumented: 30     # Score weight for endpoints missing from Swagger
weight_active: 25           # Score weight for 200 OK endpoints
weight_sensitive: 20        # Score weight for keywords like 'admin', 'secret'
```

---

## 🖥️ Commands Reference

Arguments common to all commands:
- `--verbose (-v)`: Enable debug logging.
- `--config (-c)`: Path to custom config file.

### 1. `collect`
Gather historical endpoints from public archives.
- `--domain (-d)`: Target domain (e.g., `example.com`).
- `--limit (-l)`: Max pages to scrape per source (default: 50).
- `--skip-js`: Skip JavaScript file analysis.
- `--skip-commoncrawl`: Skip CommonCrawl (faster but less data).
- `--rate-limit`: Override rate limit just for this run.

### 2. `audit`
Probe endpoints and compare against documentation.
- `--input (-i)`: Path to footprint file (from `collect`).
- `--base-url (-b)`: Live server URL (e.g., `https://example.com` or `http://localhost:8080`).
- `--swagger (-s)`: Path to OpenAPI/Swagger spec (JSON/YAML) for "Ghost" detection.
- `--fuzz`: Enable brute-force fuzzing for common hidden paths.
- `--scan-all`: Automatically scan all subdomains found in footprint.
- `--header (-H)`: Add custom headers (e.g., `-H "Cookie: id=1"`).

### 3. `sanitize`
Clean data for report sharing.
- `--input (-i)`: Source JSON file.
- `--output (-o)`: Destination JSON file.
- `--strict`: Aggressive filtering of potential secrets.

### 4. `report`
Generate visual reports.
- `--input (-i)`: Audit results JSON.
- `--output (-o)`: Output file path (.html or .pdf).

### 5. `dashboard`
Launch interactive GUI.
- `--input (-i)`: Audit results JSON.
- `--port (-p)`: Dashboard port (default: 8501).





GHOSTMAP is an **AppSec Agent**, not just a URL fuzzer. It combines the best of multiple tools into one intelligent workflow.

| Feature | 👻 GHOSTMAP | 🔨 Gobuster / Ffuf | 🕰️ Waybackurls |
| :--- | :--- | :--- | :--- |
| **Discovery Method** | **Hybrid** (Archive + Fuzzing) | Brute-force only | Archive only |
| **Context Awareness** | **Smart** (Detects Tech Stack) | Blind (User must guess wordlists) | N/A |
| **Ghost Detection** | **✅ Yes** (Compares w/ Swagger) | ❌ No | ❌ No |
| **WAF Evasion** | **✅ Auto-Throttling & Retries** | ❌ Manual tuning required | ❌ No |
| **False Positives** | **✅ Low** (Soft 404 Detection) | ❌ High (Needs manual filtering) | ❌ High |
| **Report Generation** | **✅ Interactive HTML/PDF** | ❌ Text output only | ❌ Text output only |

### Key Differentiators:
1.  **👻 The "Ghost" Concept**: Standard tools just find URLs. GHOSTMAP compares findings against your **Swagger/OpenAPI** specs to identify *undocumented* (Ghost) endpoints—the highest risk for attacks.
2.  **🧠 Smart Fuzzing**: Instead of blindly trying 10,000 words, it uses a **Tech Detector**. If it sees a Spring Boot server, it scans for Java actuators; if WordPress, it scans for plugins.
3.  **🛡️ Zero-Config WAF Evasion**: Unlike other tools where you must manually tweak rate limits, GHOSTMAP automatically detects 429/403 errors and backs off, ensuring your scan finishes without getting banned.

---

## 🎯 Usage Scenarios

### Scenario A: Public Domain Discovery (The "Full Ghost" Scan)
**Goal:** Map the entire attack surface of a public website (e.g., `example.com`), including historical files from Archive.org.

**Steps:**
1.  **Collect Footprint** (Gather public data):
    ```bash
    python -m ghostmap.cli collect -d example.com --limit 1000
    ```
    *This creates a `footprint.json` file in `scans/example.com/TIMESTAMP/`.*

2.  **Audit & Fuzz** (Check what's alive + Fuzz for hidden secrets):
    ```bash
    python -m ghostmap.cli audit -i scans/example.com/LATEST/footprint.json -b https://example.com --fuzz
    ```
    *   `-b`: The live URL to test against.
    *   `--fuzz`: Brute-force common hidden paths (e.g., `/admin`, `.env`, `/metrics`).

3.  **Generate Report** (View results):
    ```bash
    python -m ghostmap.cli report -i scans/example.com/LATEST/audit_results.json
    ```
    *Opens an interactive HTML report to filter and search findings.*

---

### Scenario B: Private/Dev Environment (The "Blind" Scan)
**Goal:** Test a local development server or internal IP that has **no external history**.

**Steps:**
1.  **Create Empty Footprint**:
    ```bash
    python -m ghostmap.cli collect -d localhost
    ```
    *Since it's private, this finds nothing but creates the necessary file structure.*

2.  **Active Fuzzing** (Brute-force discovery):
    ```bash
    python -m ghostmap.cli audit -i scans/localhost/LATEST/footprint.json -b http://localhost:8080 --fuzz
    ```
    *   GHOSTMAP will detect the tech stack and fuzz for common endpoints specific to that tech (e.g., Spring Boot actuators, Django admin).*

> [!TIP]
> **Subdomain Scanning**
> If your footprint contains multiple subdomains (e.g., `api.localhost`, `admin.localhost`), run `audit` **without** the `-b` flag.
> GHOSTMAP will detect them and ask:
> *   "Found 3 subdomains. Enter number to scan one, or 'all' to scan everything."
> Use `--scan-all` to automate this!


---

### Scenario C: Authenticated Scan (Finding User-Data Leaks)
**Goal:** Test endpoints that require login to see if they leak data or have broken access controls.

**Steps:**
1.  **Get Your Session Cookie**: Log in to the application in your browser and copy the `Cookie` header (e.g., `session_id=xyz`).

2.  **Run Audit with Auth**:
    ```bash
    python -m ghostmap.cli audit -i scans/example.com/LATEST/footprint.json \
      -b https://app.example.com \
      --header "Cookie: session_id=xyz"
    ```
    *GHOSTMAP will use this cookie for all probes, allowing it to find endpoints hidden behind login screens.*

---

---

### Scenario D: Reporting & Analysis
**Goal:** Share findings with your team or filter through noise.

**Generate Interactive Report:**
```bash
python -m ghostmap.cli report -i <path_to_audit_results.json>
```
**Features in Report:**
-   **Risk Filter**: Show only `HIGH` risk items (e.g., likely sensitive data).
-   **Status Filter**: Show `200 OK` (live endpoints) and ignore `301 Redirects`.
-   **Search**: Type `/admin` or `api` to instantly filter the list.

---

## 📊 Interactive Dashboard

For a more visual experience, launch the Streamlit dashboard:
```bash
python -m ghostmap.cli dashboard -i scans/example.com/LATEST/audit_results.json
```
This opens a local web interface where you can:
-   Visualize risk distribution charts.
-   Filter endpoints by status code, risk score, and discovery source.
-   Export filtered results.

---

## 🧹 Data Sanitization

Before sharing footprint data externally (e.g., with a security consultant), you might want to remove sensitive information like emails, session IDs, or API tokens.

**Run Sanitizer:**
```bash
python -m ghostmap.cli sanitize -i scans/example.com/LATEST/footprint.json -o sanitized.json
```
**Options:**
-   `--strict`: Aggressively remove anything looking like a token or secret.


---

## 🛠️ Troubleshooting

### "Too Many False Positives!" (Soft 404s)
If a site redirects **everything** to a "Whoops" page (returning 200 OK), GHOSTMAP might think every fuzzed path exists.
-   **Solution**: GHOSTMAP now **automatically detects** this. It probes a random path first (e.g., `/uuid-random`). If that returns 200/Redirect, GHOSTMAP filters out all similar responses from the report.
-   **Manual Check**: In the report, use the search bar to see if many results have the exact same size/length.

### "Rate Limited / 429 Errors"
If the server blocks you for scanning too fast:
-   **Auto-Adjustment**: GHOSTMAP now automatically detects 429/403 errors and backs off exponentially. It will also lower the concurrency if a WAF is detected.
-   **Manual Override**: You can still enforce a stricter limit in `ghostmap_config.yaml`:
    ```yaml
    rate_limit: 2.0        # Max 2 requests per second
    probe_concurrency: 5   # Lower active threads
    ```
