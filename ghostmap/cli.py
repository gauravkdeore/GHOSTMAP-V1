"""
GHOSTMAP CLI — Main command-line interface.
"""

import json
import logging
import os
import sys
from datetime import datetime
from typing import Optional

import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.table import Table
from rich.panel import Panel
from rich import print as rprint

from ghostmap import __version__
from ghostmap.utils.config import GhostMapConfig

console = Console()


def setup_logging(verbose: bool):
    """Configure logging based on verbosity."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
        datefmt="%H:%M:%S",
    )


@click.group()
@click.version_option(version=__version__, prog_name="ghostmap")
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose debug output")
@click.option("--config", "-c", default=None, help="Path to YAML/JSON config file")
@click.pass_context
def main(ctx, verbose, config):
    """👻 GHOSTMAP — Discover undocumented API endpoints before attackers do."""
    ctx.ensure_object(dict)
    ctx.obj["verbose"] = verbose
    setup_logging(verbose)

    # Load config file if provided
    if config:
        try:
            cfg = GhostMapConfig.load_from_file(config)
            cfg.verbose = verbose  # CLI verbose flag overrides config
            ctx.obj["config"] = cfg
            click.echo(f"Loaded configuration from {config}")
        except Exception as e:
            click.echo(f"Error loading config: {e}", err=True)
            sys.exit(1)
    else:
        ctx.obj["config"] = GhostMapConfig(verbose=verbose)


# ==========================================================================
# COLLECT COMMAND
# ==========================================================================

@main.command()
@click.option("--domain", "-d", required=True, help="Target domain to scan (e.g., example.com)")
@click.option("--output", "-o", default=None, help="Output JSON file (default: auto-organized)")
@click.option("--limit", "-l", default=50, help="Max pages to scrape per source")
@click.option("--skip-js", is_flag=True, help="Skip JavaScript analysis")
@click.option("--skip-commoncrawl", is_flag=True, help="Skip CommonCrawl scraping")
@click.option("--rate-limit", "-rl", type=float, default=None, help="Rate limit (requests per second)")
@click.option("--header", "-H", multiple=True, help="Custom header 'Key: Value'")
@click.pass_context
def collect(ctx, domain, output, limit, skip_js, skip_commoncrawl, rate_limit, header):
    """🔍 Collect public footprint from internet archives."""
    from ghostmap.collector.wayback import WaybackScraper
    from ghostmap.collector.commoncrawl import CommonCrawlScraper
    from ghostmap.collector.js_analyzer import JSAnalyzer
    from ghostmap.collector.dedup import DeduplicationEngine
    import os
    from datetime import datetime

    # Get config from context and apply overrides
    config = ctx.obj["config"]
    if rate_limit is not None:
        config.rate_limit = rate_limit
    
    # Auto-folder logic
    if output is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        sanitized_domain = domain.replace("https://", "").replace("http://", "").replace("/", "_")
        scan_dir = os.path.join("scans", sanitized_domain, timestamp)
        os.makedirs(scan_dir, exist_ok=True)
        output = os.path.join(scan_dir, "footprint.json")
        console.print(f"[bold green]📂 Created scan directory: {scan_dir}[/bold green]")
        
        # Save scan metadata/config there?
        ctx.obj["scan_dir"] = scan_dir
    else:
        # If user provided output, ensure dir exists
        os.makedirs(os.path.dirname(os.path.abspath(output)) or ".", exist_ok=True)

    # Parse headers
    for h in header:
        try:
            key, value = h.split(":", 1)
            config.headers[key.strip()] = value.strip()
        except ValueError:
            console.print(f"[bold red]⚠️ Invalid header format: {h}[/bold red]")
    dedup = DeduplicationEngine()

    console.print(Panel(
        f"[bold cyan]👻 GHOSTMAP Collector[/bold cyan]\n"
        f"Target: [bold]{domain}[/bold]\n"
        f"Output: [bold]{output}[/bold]",
        border_style="cyan",
    ))

    # --- Wayback Machine ---
    console.print("\n[bold yellow]📡 Phase 1/3: Wayback Machine[/bold yellow]")
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console,
    ) as progress:
        task = progress.add_task("Scraping Wayback Machine...", total=None)

        with WaybackScraper(config) as wb:
            def wb_callback(batch, total):
                progress.update(task, description=f"Wayback: {total} URLs found", total=total, completed=total)

            wayback_urls = wb.fetch_urls(domain, limit=limit, callback=wb_callback)
            js_urls = wb.extract_js_urls(wayback_urls)

            progress.update(task, description=f"[green]✅ Wayback: {len(wayback_urls)} URLs[/green]")

    dedup.add_many(wayback_urls)
    console.print(f"  Found [bold]{len(wayback_urls)}[/bold] URLs, [bold]{len(js_urls)}[/bold] JS files")

    # --- CommonCrawl ---
    cc_urls = []
    if not skip_commoncrawl:
        console.print("\n[bold yellow]📡 Phase 2/3: CommonCrawl[/bold yellow]")
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Scraping CommonCrawl...", total=None)

            with CommonCrawlScraper(config) as cc:
                def cc_callback(idx_name, batch, total):
                    progress.update(task, description=f"CommonCrawl ({idx_name}): {total} URLs")

                cc_urls = cc.fetch_urls(domain, limit=limit, callback=cc_callback)
                progress.update(task, description=f"[green]✅ CommonCrawl: {len(cc_urls)} URLs[/green]")

        dedup.add_many(cc_urls)
        console.print(f"  Found [bold]{len(cc_urls)}[/bold] URLs")
    else:
        console.print("\n[dim]⏭ Skipping CommonCrawl[/dim]")

    # --- JavaScript Analysis ---
    js_endpoints = []
    if not skip_js and js_urls:
        console.print(f"\n[bold yellow]📡 Phase 3/3: JavaScript Analysis ({len(js_urls)} files)[/bold yellow]")
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=console,
        ) as progress:
            task = progress.add_task("Analyzing JS files...", total=len(js_urls))

            with JSAnalyzer(config) as js:
                def js_callback(url, idx, total, found):
                    progress.update(task, completed=idx, description=f"JS: {idx}/{total} files")

                result = js.analyze_js_urls(js_urls, base_domain=domain, callback=js_callback)
                js_endpoints = result["endpoints"]
                progress.update(task, description=f"[green]✅ JS: {len(js_endpoints)} endpoints[/green]")

        # Add JS endpoints to dedup
        for ep in js_endpoints:
            dedup.add({
                "url": ep["endpoint"],
                "source": "js_analysis",
                "source_file": ep.get("source_file", ""),
                "pattern_name": ep.get("pattern_name", ""),
            })
        console.print(f"  Found [bold]{len(js_endpoints)}[/bold] endpoints from JS")
    else:
        console.print("\n[dim]⏭ Skipping JS analysis[/dim]")

    # --- Final Results ---
    results = dedup.get_results()
    stats = dedup.get_stats()

    output_data = {
        "meta": {
            "tool": "ghostmap",
            "version": __version__,
            "domain": domain,
            "timestamp": datetime.now().isoformat(),
            "stats": stats,
        },
        "endpoints": results,
    }

    # Ensure output directory exists
    output_dir = os.path.dirname(output)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    with open(output, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2, default=str)

    # Summary table
    console.print()
    summary = Table(title="📊 Collection Summary", border_style="cyan")
    summary.add_column("Metric", style="bold")
    summary.add_column("Value", style="green")
    summary.add_row("Domain", domain)
    summary.add_row("Wayback URLs", str(len(wayback_urls)))
    summary.add_row("CommonCrawl URLs", str(len(cc_urls)))
    summary.add_row("JS Endpoints", str(len(js_endpoints)))
    summary.add_row("Unique Endpoints", str(stats["unique_endpoints"]))
    summary.add_row("Dedup Ratio", f"{stats['dedup_ratio']:.0%}")
    summary.add_row("Output File", output)
    console.print(summary)

    console.print(f"\n[bold green]✅ Footprint saved to {output}[/bold green]")


# ==========================================================================
# SANITIZE COMMAND
# ==========================================================================

@main.command()
@click.option("--input", "-i", "input_file", required=True, help="Input JSON footprint file")
@click.option("--output", "-o", default="sanitized_footprint.json", help="Output sanitized JSON file")
@click.option("--strict", is_flag=True, help="Enable strict sanitization mode")
@click.pass_context
def sanitize(ctx, input_file, output, strict):
    """🧹 Sanitize footprint data for safe internal transfer."""
    from ghostmap.sanitizer.sanitizer import FootprintSanitizer

    console.print(Panel(
        f"[bold cyan]🧹 GHOSTMAP Sanitizer[/bold cyan]\n"
        f"Input: [bold]{input_file}[/bold]\n"
        f"Output: [bold]{output}[/bold]\n"
        f"Mode: [bold]{'Strict' if strict else 'Standard'}[/bold]",
        border_style="cyan",
    ))

    # Load input
    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    sanitizer = FootprintSanitizer(strict=strict)
    sanitized = sanitizer.sanitize(data)
    report = sanitizer.get_report()

    # Save output
    output_dir = os.path.dirname(output)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    with open(output, "w", encoding="utf-8") as f:
        json.dump(sanitized, f, indent=2, default=str)

    # Summary
    summary = Table(title="🧹 Sanitization Summary", border_style="cyan")
    summary.add_column("Metric", style="bold")
    summary.add_column("Value", style="green")
    summary.add_row("Emails Removed", str(report.get("emails_removed", 0)))
    summary.add_row("Tokens Removed", str(report.get("tokens_removed", 0)))
    summary.add_row("Session IDs Removed", str(report.get("sessions_removed", 0)))
    summary.add_row("Query Values Stripped", str(report.get("query_values_stripped", 0)))
    summary.add_row("Suspicious Patterns", str(report.get("suspicious_patterns", 0)))
    summary.add_row("Output File", output)
    console.print(summary)

    console.print(f"\n[bold green]✅ Sanitized data saved to {output}[/bold green]")


# ==========================================================================
# AUDIT COMMAND
# ==========================================================================

# Helper function extracted from audit command


def run_audit_scan(
    ctx,
    unique_name,
    base_url,
    endpoints,
    documented_endpoints,
    swagger,
    git_repo,
    probe,
    fuzz,
    fuzz_mode,
    config,
    input_file,
    output
):
    """Execution logic for a single audit target."""
    console.print(Panel(
        f"[bold cyan]🔎 GHOSTMAP Auditor[/bold cyan]\n"
        f"Target: [bold]{base_url}[/bold]\n"
        f"Output: [bold]{output}[/bold]\n"
        f"Swagger: [bold]{swagger or 'None'}[/bold]\n"
        f"Git Repo: [bold]{git_repo or 'None'}[/bold]\n"
        f"Probing: [bold]{'Enabled' if probe else 'Disabled'}[/bold]",
        border_style="cyan",
    ))

    # --- WAF Detection ---
    if base_url:
        from ghostmap.auditor.waf_detector import WafDetector
        detector = WafDetector(config)
        with console.status("Checking for WAF protection..."):
            is_waf, waf_name, safe_limit = detector.detect(base_url)
        
        if is_waf:
            console.print(f"[bold red]🛡️ WAF Detected: {waf_name}[/bold red]")
            if safe_limit > 0 and (config.rate_limit is None or config.rate_limit > safe_limit):
                console.print(f"[yellow]⚠️ Auto-adjusting rate limit to {safe_limit} req/s for evasion[/yellow]")
                config.rate_limit = safe_limit


    from ghostmap.auditor.swagger_compare import SwaggerComparator
    from ghostmap.auditor.git_miner import GitEndpointMiner
    from ghostmap.auditor.prober import EndpointProber
    from ghostmap.auditor.risk_scorer import RiskScorer
    from ghostmap.auditor.noise_filter import NoiseFilter
    from ghostmap.auditor.fuzzer import GhostFuzzer

    audit_endpoints = list(endpoints)  # Copy list for this scan
    current_doc_endpoints = set(documented_endpoints)
    
    # --- Swagger Comparison ---
    if swagger:
        console.print("\n[bold yellow]📋 Comparing with Swagger/OpenAPI spec...[/bold yellow]")
        comparator = SwaggerComparator()
        swagger_endpoints = comparator.load_spec(swagger)
        current_doc_endpoints.update(swagger_endpoints)
        comparison = comparator.compare(audit_endpoints, swagger_endpoints)
        console.print(f"  Documented: {len(swagger_endpoints)} | Ghost: {len(comparison['ghost'])} | Missing from spec: {len(comparison['undocumented'])}")

    # --- Git Mining ---
    if git_repo:
        console.print("\n[bold yellow]⛏️ Mining Git repository for endpoints...[/bold yellow]")
        miner = GitEndpointMiner()
        git_endpoints = miner.mine(git_repo)
        current_doc_endpoints.update(git_endpoints)
        console.print(f"  Found {len(git_endpoints)} endpoints in code")

    # --- Live Probing ---
    probe_results = {}
    if probe and base_url:
        console.print(f"\n[bold yellow]🔌 Probing endpoints at {base_url}...[/bold yellow]")
        prober = EndpointProber(config)

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=console,
        ) as progress:
            task = progress.add_task("Probing...", total=len(audit_endpoints))

            def probe_callback(idx, total, url, status):
                progress.update(task, completed=idx)

            probe_results = prober.probe_all(audit_endpoints, base_url, callback=probe_callback)

        console.print(f"  Active: {probe_results.get('active', 0)} | Dead: {probe_results.get('dead', 0)}")

    # --- Smart Fuzzing ---
    fuzzed_endpoints = []
    if fuzz and base_url:
        console.print(f"\n[bold yellow]⚡ Running Smart Fuzzer (Mode: {fuzz_mode})...[/bold yellow]")
        fuzzer = GhostFuzzer(config)
        with console.status("Fuzzing target..."):
            fuzzed_endpoints = fuzzer.fuzz(base_url, mode=fuzz_mode)
        
        console.print(f"  Found {len(fuzzed_endpoints)} hidden endpoints")
        
        # Add fuzzed endpoints
        for ep in fuzzed_endpoints:
            audit_endpoints.append({
                "endpoint": ep["endpoint"],
                "source": "ghost_fuzzer",
                "method": ep["method"],
                "status": ep["status"]
            })

    # --- Noise Filtering ---
    console.print("\n[bold cyan]🧹 Filtering noise (blogs, docs, tracking params)...[/bold cyan]")
    noise_filter = NoiseFilter(config)
    clean_endpoints = noise_filter.filter_endpoints(audit_endpoints)
    stats = noise_filter.stats
    if stats["filtered"] > 0:
        console.print(f"[dim]   Removed {stats['filtered']} noise URLs, {stats['kept']} endpoints remain[/dim]")

    # --- Risk Scoring ---
    console.print("[bold yellow]⚠️ Calculating risk scores...[/bold yellow]")
    scorer = RiskScorer(config)
    scored_endpoints = scorer.score_all(
        clean_endpoints,
        documented_endpoints=current_doc_endpoints,
        probe_results=probe_results.get("details", {}),
    )

    # Build output
    output_data = {
        "meta": {
            "tool": "ghostmap",
            "version": __version__,
            "timestamp": datetime.now().isoformat(),
            "input_file": input_file,
            "swagger_spec": swagger,
            "git_repo": git_repo,
            "probing_enabled": probe,
            "base_url": base_url,
        },
        "summary": {
            "total_endpoints": len(scored_endpoints),
            "high_risk": sum(1 for e in scored_endpoints if e.get("risk_score", 0) >= 70),
            "medium_risk": sum(1 for e in scored_endpoints if 40 <= e.get("risk_score", 0) < 70),
            "low_risk": sum(1 for e in scored_endpoints if e.get("risk_score", 0) < 40),
            "documented": len(current_doc_endpoints),
        },
        "endpoints": scored_endpoints,
    }

    output_dir = os.path.dirname(output)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    with open(output, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2, default=str)

    # Summary table
    summary = Table(title=f"🔎 Audit Summary: {unique_name}", border_style="cyan")
    summary.add_column("Risk Level", style="bold")
    summary.add_column("Count", style="green")
    summary.add_row("[red]🔴 HIGH (≥70)[/red]", str(output_data["summary"]["high_risk"]))
    summary.add_row("[yellow]🟡 MEDIUM (40-69)[/yellow]", str(output_data["summary"]["medium_risk"]))
    summary.add_row("[green]🟢 LOW (<40)[/green]", str(output_data["summary"]["low_risk"]))
    summary.add_row("Total", str(output_data["summary"]["total_endpoints"]))
    console.print(summary)

    console.print(f"\n[bold green]✅ Audit results saved to {output}[/bold green]")


@main.command()
@click.option("--input", "-i", "input_file", required=True, help="Input sanitized footprint JSON")
@click.option("--swagger", "-s", default=None, help="Swagger/OpenAPI spec file (JSON or YAML)")
@click.option("--git-repo", "-g", default=None, help="Path to Git repository for endpoint mining")
@click.option("--probe", "-p", is_flag=True, help="Enable live endpoint probing")
@click.option("--base-url", "-b", default=None, help="Base URL for probing (e.g., http://localhost:8080)")
@click.option("--output", "-o", default=None, help="Output audit results JSON (default: auto)")
@click.option("--rate-limit", "-rl", type=float, default=None, help="Rate limit (requests per second)")
@click.option("--header", "-H", multiple=True, help="Custom header 'Key: Value'")
@click.option("--fuzz", is_flag=True, help="Enable Smart Fuzzing for hidden endpoints")
@click.option("--fuzz-mode", type=click.Choice(["auto", "all"]), default="auto", help="Fuzzing mode: auto (tech-detect) or all (brute-force)")
@click.option("--scan-all", is_flag=True, help="Automatically scan all discovered subdomains")
@click.pass_context
def audit(ctx, input_file, swagger, git_repo, probe, base_url, output, rate_limit, header, fuzz, fuzz_mode, scan_all):
    """🔎 Audit endpoints against internal documentation."""
    import os
    from urllib.parse import urlparse

    # Get config from context and apply overrides
    config = ctx.obj["config"]
    if rate_limit is not None:
        config.rate_limit = rate_limit

    # Parse headers
    for h in header:
        try:
            key, value = h.split(":", 1)
            config.headers[key.strip()] = value.strip()
        except ValueError:
            console.print(f"[bold red]⚠️ Invalid header format: {h}[/bold red]")

    # Load input
    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    endpoints = data.get("endpoints", [])
    documented_endpoints = set()
    
    # Determine Targets
    targets = [] # List of tuples: (name, base_url, output_path)

    # 1. Explicit Base URL (Single Target)
    if base_url:
        target_output = output
        if target_output is None:
            input_dir = os.path.dirname(input_file)
            target_output = os.path.join(input_dir or ".", "audit_results.json")
        
        parsed = urlparse(base_url)
        name = parsed.netloc or "target"
        targets.append((name, base_url, target_output))

    # 2. Extract from Footprint (Multi Target)
    else:
        console.print("[yellow]No base URL provided. analyzing footprint for subdomains...[/yellow]")
        domains = set()
        for ep in endpoints:
            url = ep.get("url") or ep.get("normalized_url")
            if url:
                try:
                    parsed = urlparse(url)
                    if parsed.netloc:
                        domains.add(parsed.netloc)
                except: pass
        
        sorted_domains = sorted(list(domains))
        
        if not sorted_domains:
            console.print("[bold red]❌ No domains found in footprint and no base URL provided![/bold red]")
            return

        selected_domains = []
        if scan_all:
             selected_domains = sorted_domains
             console.print(f"[green]Auto-selecting all {len(selected_domains)} domains.[/green]")
        elif len(sorted_domains) == 1:
             selected_domains = sorted_domains
             console.print(f"[green]Only one domain found: {selected_domains[0]}. Auto-selecting.[/green]")
        else:
             # Interactive Prompt
             from rich.prompt import Prompt
             console.print(f"[cyan]Found {len(sorted_domains)} subdomains:[/cyan]")
             for i, d in enumerate(sorted_domains):
                 console.print(f"  {i+1}. {d}")
             
             choice = Prompt.ask(
                 "\n[bold yellow]Enter number to scan specific domain, or 'all' to scan everything[/bold yellow]", 
                 default="all"
             )
             
             if choice.lower() == "all":
                 selected_domains = sorted_domains
             else:
                 try:
                     idx = int(choice) - 1
                     if 0 <= idx < len(sorted_domains):
                         selected_domains = [sorted_domains[idx]]
                     else:
                         console.print("[red]Invalid selection![/red]")
                         return
                 except ValueError:
                     console.print("[red]Invalid input![/red]")
                     return

        input_dir = os.path.dirname(input_file) or "."
        for domain in selected_domains:
            # Construct Base URL (guess HTTPS)
            t_base = f"https://{domain}"
            # Construct Output Path
            if output:
                # If explicit output given, use it (append domain suffix if multi-target?)
                # If multi-target, we MUST unique-ify output
                base, ext = os.path.splitext(output)
                t_out = f"{base}_{domain}{ext}"
            else:
                t_out = os.path.join(input_dir, f"audit_results_{domain}.json")
            
            targets.append((domain, t_base, t_out))

    # EXECUTE SCANS
    for i, (name, t_base, t_out) in enumerate(targets):
        if len(targets) > 1:
            console.print(f"\n[bold magenta]🚀 Starting Scan {i+1}/{len(targets)}: {name}[/bold magenta]")
        
        run_audit_scan(
            ctx, name, t_base, endpoints, documented_endpoints, 
            swagger, git_repo, probe, fuzz, fuzz_mode, config, input_file, t_out
        )


# ==========================================================================
# DASHBOARD COMMAND
# ==========================================================================

@main.command()
@click.option("--input", "-i", "input_file", required=True, help="Audit results JSON file")
@click.option("--port", "-p", default=8501, help="Streamlit server port")
@click.pass_context
def dashboard(ctx, input_file, port):
    """📊 Launch the Ghost Map interactive dashboard."""
    import subprocess

    console.print(Panel(
        f"[bold cyan]📊 GHOSTMAP Dashboard[/bold cyan]\n"
        f"Loading: [bold]{input_file}[/bold]\n"
        f"Port: [bold]{port}[/bold]",
        border_style="cyan",
    ))

    dashboard_script = os.path.join(os.path.dirname(__file__), "dashboard", "app.py")

    cmd = [
        sys.executable, "-m", "streamlit", "run",
        dashboard_script,
        "--server.port", str(port),
        "--", "--input", input_file,
    ]

    console.print(f"[bold green]🚀 Launching dashboard at http://localhost:{port}[/bold green]")
    subprocess.run(cmd)


# ==========================================================================
# REPORT COMMAND
# ==========================================================================

@main.command()
@click.option("--input", "-i", "input_file", required=True, help="Audit results JSON file")
@click.option("--output", "-o", default=None, help="Output report file (PDF/HTML)")
@click.pass_context
def report(ctx, input_file, output):
    """📊 Generate PDF or HTML report from audit results."""
    from ghostmap.reporter.pdf_report import GhostMapReporter as PDFReportGenerator
    from ghostmap.reporter.html_generator import HTMLReportGenerator
    import json
    import os

    # Determine output format and default output path
    if output is None:
        input_dir = os.path.dirname(input_file)
        # Default to HTML for better interactivity
        output = os.path.join(input_dir, "report.html") if input_dir else "report.html"

    format_type = "pdf" if output.lower().endswith(".pdf") else "html"

    console.print(Panel(
        f"[bold cyan]📄 GHOSTMAP Reporter[/bold cyan]\n"
        f"Input: [bold]{input_file}[/bold]\n"
        f"Output: [bold]{output}[/bold]\n"
        f"Format: [bold]{format_type.upper()}[/bold]",
        border_style="cyan",
    ))

    try:
        with open(input_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        if format_type == "html":
            console.print("[bold cyan]Generating interactive HTML report...[/bold cyan]")
            generator = HTMLReportGenerator()
            generator.generate(data, output)
        else:
            console.print("[bold cyan]Generating PDF report...[/bold cyan]")
            generator = PDFReportGenerator()
            generator.generate(data, output)
            
        console.print(f"\n[bold green]✅ Report saved to {output}[/bold green]")

    except Exception as e:
        console.print(f"[bold red]❌ Failed to generate report: {e}[/bold red]")
        if ctx.obj.get("config").verbose:
            import traceback
            console.print(traceback.format_exc())


if __name__ == "__main__":
    main()
