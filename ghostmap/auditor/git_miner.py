"""
GHOSTMAP Git Endpoint Miner — Extract route definitions from source code.
"""

import os
import re
import logging
from typing import List, Set, Dict, Any, Optional

logger = logging.getLogger("ghostmap.auditor.git_miner")


# ===========================================================================
# Framework-specific route patterns
# ===========================================================================

ROUTE_PATTERNS = {
    # Flask / Python
    "flask": re.compile(
        r"""@(?:app|blueprint|bp)\.(?:route|get|post|put|delete|patch)\s*\(\s*['"]([^'"]+)['"]""",
        re.IGNORECASE,
    ),
    # Django
    "django_path": re.compile(
        r"""(?:path|re_path|url)\s*\(\s*['"]([^'"]+)['"]""",
    ),
    # FastAPI
    "fastapi": re.compile(
        r"""@(?:app|router)\.(?:get|post|put|delete|patch|options|head)\s*\(\s*['"]([^'"]+)['"]""",
        re.IGNORECASE,
    ),
    # Express.js / Node.js
    "express": re.compile(
        r"""(?:app|router)\.(?:get|post|put|delete|patch|all|use)\s*\(\s*['"]([^'"]+)['"]""",
        re.IGNORECASE,
    ),
    # Spring Boot / Java
    "spring": re.compile(
        r"""@(?:Request|Get|Post|Put|Delete|Patch)Mapping\s*\(\s*(?:value\s*=\s*)?['"]([^'"]+)['"]""",
        re.IGNORECASE,
    ),
    # Go (gorilla/mux, gin, echo)
    "go_router": re.compile(
        r"""\.(?:HandleFunc|Handle|GET|POST|PUT|DELETE|PATCH|Group)\s*\(\s*['"]([^'"]+)['"]""",
    ),
    # Ruby on Rails
    "rails": re.compile(
        r"""(?:get|post|put|patch|delete|match|root)\s+['"]([^'"]+)['"]""",
    ),
    # ASP.NET
    "aspnet": re.compile(
        r"""\[(?:Http(?:Get|Post|Put|Delete|Patch)|Route)\s*\(\s*['"]([^'"]+)['"]""",
        re.IGNORECASE,
    ),
    # Generic API path strings
    "generic_api": re.compile(
        r"""['"](/api/[a-zA-Z0-9/_\-{}:]+)['"]""",
    ),
}

# File extensions to scan
SCANNABLE_EXTENSIONS = {
    ".py", ".js", ".ts", ".jsx", ".tsx",
    ".java", ".kt", ".go", ".rb",
    ".cs", ".php", ".rs",
}

# Directories to skip
SKIP_DIRS = {
    "node_modules", ".git", "__pycache__", "venv", "env",
    ".venv", "vendor", "dist", "build", ".next",
    "target", "bin", "obj",
}


class GitEndpointMiner:
    """
    Mines a Git repository (or any source code directory) for
    route/endpoint definitions across multiple frameworks.
    """

    def __init__(self, additional_patterns: Optional[Dict[str, re.Pattern]] = None):
        self.patterns = dict(ROUTE_PATTERNS)
        if additional_patterns:
            self.patterns.update(additional_patterns)

    def mine(self, repo_path: str, callback=None) -> Set[str]:
        """
        Scan a directory tree for endpoint definitions.

        Args:
            repo_path: Path to the git repository root
            callback: Progress callback(file_path, endpoints_found)

        Returns:
            Set of discovered endpoint paths
        """
        if not os.path.isdir(repo_path):
            logger.error(f"Repository path not found: {repo_path}")
            return set()

        all_endpoints = set()
        files_scanned = 0

        for root, dirs, files in os.walk(repo_path):
            # Skip unwanted directories
            dirs[:] = [d for d in dirs if d not in SKIP_DIRS]

            for filename in files:
                ext = os.path.splitext(filename)[1].lower()
                if ext not in SCANNABLE_EXTENSIONS:
                    continue

                filepath = os.path.join(root, filename)
                try:
                    endpoints = self._scan_file(filepath)
                    all_endpoints.update(endpoints)
                    files_scanned += 1

                    if callback and endpoints:
                        callback(filepath, endpoints)

                except Exception as e:
                    logger.debug(f"Error scanning {filepath}: {e}")

        logger.info(f"Git mining: scanned {files_scanned} files, found {len(all_endpoints)} endpoints")
        return all_endpoints

    def _scan_file(self, filepath: str) -> Set[str]:
        """Scan a single file for endpoint definitions."""
        try:
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
        except Exception as e:
            logger.debug(f"Cannot read {filepath}: {e}")
            return set()

        endpoints = set()
        for pattern_name, pattern in self.patterns.items():
            matches = pattern.findall(content)
            for match in matches:
                cleaned = self._clean_endpoint(match)
                if cleaned:
                    endpoints.add(cleaned)

        return endpoints

    @staticmethod
    def _clean_endpoint(endpoint: str) -> str:
        """Clean up a matched endpoint string."""
        endpoint = endpoint.strip().rstrip("/")

        # Skip if too short or doesn't look like a path
        if len(endpoint) < 2:
            return ""

        # Ensure it starts with /
        if not endpoint.startswith("/"):
            endpoint = "/" + endpoint

        # Replace Django-style parameters: <int:id> -> {id}
        endpoint = re.sub(r"<(?:\w+:)?(\w+)>", r"{\1}", endpoint)

        # Replace regex groups with placeholders
        endpoint = re.sub(r"\([^)]+\)", "{param}", endpoint)

        return endpoint

    def mine_detailed(self, repo_path: str) -> List[Dict[str, Any]]:
        """
        Mine with detailed results including source file and framework info.

        Args:
            repo_path: Path to the git repository

        Returns:
            List of {endpoint, framework, source_file, line_number}
        """
        results = []
        seen = set()

        if not os.path.isdir(repo_path):
            return results

        for root, dirs, files in os.walk(repo_path):
            dirs[:] = [d for d in dirs if d not in SKIP_DIRS]

            for filename in files:
                ext = os.path.splitext(filename)[1].lower()
                if ext not in SCANNABLE_EXTENSIONS:
                    continue

                filepath = os.path.join(root, filename)
                try:
                    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                        lines = f.readlines()

                    for line_num, line in enumerate(lines, 1):
                        for fw_name, pattern in self.patterns.items():
                            matches = pattern.findall(line)
                            for match in matches:
                                cleaned = self._clean_endpoint(match)
                                if cleaned and cleaned not in seen:
                                    seen.add(cleaned)
                                    results.append({
                                        "endpoint": cleaned,
                                        "framework": fw_name,
                                        "source_file": filepath,
                                        "line_number": line_num,
                                    })
                except Exception:
                    continue

        return results
