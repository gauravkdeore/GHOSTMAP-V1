# 👻 GHOSTMAP User Manual

**GhostMap** helps you find hidden, forgotten, or undocumented API endpoints that attackers might exploit.

## 🚀 Quick Start
Run from the root directory:
```bash
python -m ghostmap.cli --help
```

---

## 💡 Why GHOSTMAP? (vs. Standard Tools)

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
