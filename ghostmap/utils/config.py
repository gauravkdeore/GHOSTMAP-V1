"""
GHOSTMAP Configuration — Global settings and defaults.
"""

import os
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class GhostMapConfig:
    """Central configuration for all GHOSTMAP components."""

    # --- General ---
    output_dir: str = "data"
    verbose: bool = False

    # --- HTTP Client ---
    rate_limit: float = 2.0          # requests per second
    max_retries: int = 3
    retry_backoff: float = 1.5       # exponential backoff multiplier
    request_timeout: int = 30        # seconds
    user_agents: list = field(default_factory=lambda: [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
        "GhostMap/1.0 (Security Research Tool)",
    ])
    headers: dict = field(default_factory=dict)  # Custom headers (e.g. Auth)

    # --- Collector ---
    wayback_timeout: int = 60
    commoncrawl_timeout: int = 60
    max_js_file_size: int = 5 * 1024 * 1024  # 5MB
    js_download_concurrency: int = 5

    # --- Auditor ---
    probe_timeout: int = 10
    probe_concurrency: int = 10
    probe_methods: list = field(default_factory=lambda: ["HEAD", "GET"])

    # --- Risk Scoring Weights ---
    weight_undocumented: int = 30
    weight_active: int = 25
    weight_sensitive_keywords: int = 20
    weight_no_auth: int = 15
    weight_staleness: int = 10

    # --- Sensitive Keywords ---
    sensitive_keywords: list = field(default_factory=lambda: [
        "debug", "admin", "internal", "test", "staging", "dev",
        "backup", "old", "temp", "tmp", "secret", "private",
        "config", "setup", "install", "phpinfo", "console",
        "actuator", "health", "metrics", "env", "swagger",
        "graphql", "graphiql", "playground",
    ])

    def ensure_output_dir(self):
        """Create output directory if it doesn't exist."""
        os.makedirs(self.output_dir, exist_ok=True)


    @classmethod
    def load_from_file(cls, path: str) -> "GhostMapConfig":
        """Load configuration from a YAML or JSON file."""
        import yaml
        import json

        if not os.path.exists(path):
            raise FileNotFoundError(f"Config file not found: {path}")

        with open(path, "r", encoding="utf-8") as f:
            if path.endswith((".yaml", ".yml")):
                data = yaml.safe_load(f)
            elif path.endswith(".json"):
                data = json.load(f)
            else:
                raise ValueError("Config file must be .yaml or .json")

        # Filter out unknown keys
        known_keys = cls.__dataclass_fields__.keys()
        filtered_data = {k: v for k, v in data.items() if k in known_keys}
        
        return cls(**filtered_data)

    def update(self, overrides: dict):
        """Update configuration with values from a dictionary."""
        for key, value in overrides.items():
            if value is not None and hasattr(self, key):
                setattr(self, key, value)


# Global default config instance
DEFAULT_CONFIG = GhostMapConfig()
