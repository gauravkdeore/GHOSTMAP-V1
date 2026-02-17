"""
GHOSTMAP Sanitizer — Remove sensitive data from collected footprints.
"""

import re
import json
import logging
from typing import Dict, Any, List, Optional
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from copy import deepcopy

logger = logging.getLogger("ghostmap.sanitizer")


# ===========================================================================
# Regex patterns for sensitive data detection
# ===========================================================================

PATTERNS = {
    "email": re.compile(
        r"[a-zA-Z0-9._%+\-]+(?:@|%40)[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}",
    ),
    "jwt_token": re.compile(
        r"eyJ[a-zA-Z0-9_\-]+\.eyJ[a-zA-Z0-9_\-]+\.[a-zA-Z0-9_\-]+",
    ),
    "api_key": re.compile(
        r"""(?:api[_\-]?key|apikey|access[_\-]?key)\s*[=:]\s*['"]?([a-zA-Z0-9_\-]{16,})['"]?""",
        re.IGNORECASE,
    ),
    "bearer_token": re.compile(
        r"""[Bb]earer\s+[a-zA-Z0-9_\-\.]+""",
    ),
    "session_id": re.compile(
        r"""(?:session[_\-]?id|sess[_\-]?id|PHPSESSID|JSESSIONID|ASP\.NET_SessionId)\s*[=:]\s*['"]?([a-zA-Z0-9_\-]{16,})['"]?""",
        re.IGNORECASE,
    ),
    "password_in_url": re.compile(
        r"""(?:password|passwd|pwd|pass)\s*=\s*[^&\s]+""",
        re.IGNORECASE,
    ),
    "aws_key": re.compile(
        r"""(?:AKIA|ASIA)[A-Z0-9]{16}""",
    ),
    "private_key": re.compile(
        r"""-----BEGIN (?:RSA |EC |DSA )?PRIVATE KEY-----""",
    ),
    "basic_auth": re.compile(
        r"""[Bb]asic\s+[a-zA-Z0-9+/=]{10,}""",
    ),
    "ip_address": re.compile(
        r"""\b(?:10|172\.(?:1[6-9]|2\d|3[01])|192\.168)\.\d{1,3}\.\d{1,3}\b""",
    ),
}

SUSPICIOUS_PATTERNS = {
    "encoded_payload": re.compile(
        r"""(?:eval|exec|system|passthru|shell_exec)\s*\(""",
        re.IGNORECASE,
    ),
    "script_injection": re.compile(
        r"""<script[^>]*>.*?</script>""",
        re.IGNORECASE | re.DOTALL,
    ),
    "sql_injection": re.compile(
        r"""(?:UNION\s+SELECT|OR\s+1\s*=\s*1|AND\s+1\s*=\s*1|DROP\s+TABLE)""",
        re.IGNORECASE,
    ),
    "path_traversal": re.compile(
        r"""(?:\.\.\/|\.\.\\){2,}""",
    ),
}


class FootprintSanitizer:
    """
    Sanitizes collected footprint data by removing sensitive information
    before internal transfer.
    """

    def __init__(self, strict: bool = False):
        """
        Args:
            strict: If True, applies more aggressive sanitization
                    (strips all query values, removes IPs, etc.)
        """
        self.strict = strict
        self._report = {
            "emails_removed": 0,
            "tokens_removed": 0,
            "sessions_removed": 0,
            "query_values_stripped": 0,
            "suspicious_patterns": 0,
            "urls_modified": 0,
            "total_processed": 0,
        }

    def sanitize(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitize an entire footprint JSON document.

        Args:
            data: The public_footprint.json data

        Returns:
            Sanitized copy of the data
        """
        sanitized = deepcopy(data)

        # Add sanitization metadata
        sanitized["meta"] = sanitized.get("meta", {})
        sanitized["meta"]["sanitized"] = True
        sanitized["meta"]["sanitization_mode"] = "strict" if self.strict else "standard"

        # Sanitize each endpoint
        endpoints = sanitized.get("endpoints", [])
        cleaned_endpoints = []

        for ep in endpoints:
            cleaned = self._sanitize_endpoint(ep)
            if cleaned is not None:
                cleaned_endpoints.append(cleaned)
            self._report["total_processed"] += 1

        sanitized["endpoints"] = cleaned_endpoints
        sanitized["meta"]["sanitization_report"] = self._report.copy()

        logger.info(
            f"Sanitization complete: {self._report['total_processed']} processed, "
            f"{self._report['urls_modified']} modified"
        )
        return sanitized

    def _sanitize_endpoint(self, entry: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Sanitize a single endpoint entry."""
        url = entry.get("url", "") or entry.get("normalized_url", "")
        if not url:
            return entry

        # Check for suspicious patterns (flag but don't remove)
        for name, pattern in SUSPICIOUS_PATTERNS.items():
            if pattern.search(url):
                entry.setdefault("warnings", []).append(f"suspicious:{name}")
                self._report["suspicious_patterns"] += 1

        # Sanitize the URL
        sanitized_url = self._sanitize_url(url)
        if sanitized_url != url:
            entry["url"] = sanitized_url
            entry["original_url_modified"] = True
            self._report["urls_modified"] += 1

        # Sanitize normalized_url too
        if "normalized_url" in entry:
            entry["normalized_url"] = self._sanitize_url(entry["normalized_url"])

        # Remove sensitive strings from all string fields
        for key, value in list(entry.items()):
            if isinstance(value, str):
                entry[key] = self._sanitize_string(value)
            elif isinstance(value, list):
                entry[key] = [
                    self._sanitize_string(v) if isinstance(v, str) else v
                    for v in value
                ]

        return entry

    def _sanitize_url(self, url: str) -> str:
        """Sanitize a URL by stripping sensitive query params and values."""
        if not url or not any(c in url for c in "?="):
            return url

        try:
            parsed = urlparse(url)
            if not parsed.query:
                return url

            params = parse_qs(parsed.query, keep_blank_values=True)

            # Sensitive parameter names to remove entirely
            sensitive_params = {
                "token", "access_token", "api_key", "apikey", "key",
                "secret", "password", "passwd", "pwd", "pass",
                "session", "sessionid", "session_id", "sid",
                "auth", "authorization", "bearer",
                "email", "user", "username",
            }

            sanitized_params = {}
            for key, values in params.items():
                key_lower = key.lower()
                if key_lower in sensitive_params:
                    self._report["tokens_removed"] += 1
                    continue  # Remove entirely

                if self.strict:
                    # Strip all values in strict mode
                    sanitized_params[key] = ["REDACTED"]
                    self._report["query_values_stripped"] += 1
                else:
                    sanitized_params[key] = values

            new_query = urlencode(sanitized_params, doseq=True)
            return urlunparse((
                parsed.scheme, parsed.netloc, parsed.path,
                parsed.params, new_query, "",
            ))

        except Exception:
            return url

    def _sanitize_string(self, text: str) -> str:
        """Remove sensitive patterns from a string."""
        if not text:
            return text

        # Remove emails
        count = len(PATTERNS["email"].findall(text))
        if count:
            text = PATTERNS["email"].sub("[EMAIL_REDACTED]", text)
            self._report["emails_removed"] += count

        # Remove JWT tokens
        count = len(PATTERNS["jwt_token"].findall(text))
        if count:
            text = PATTERNS["jwt_token"].sub("[JWT_REDACTED]", text)
            self._report["tokens_removed"] += count

        # Remove bearer tokens
        count = len(PATTERNS["bearer_token"].findall(text))
        if count:
            text = PATTERNS["bearer_token"].sub("Bearer [TOKEN_REDACTED]", text)
            self._report["tokens_removed"] += count

        # Remove basic auth
        count = len(PATTERNS["basic_auth"].findall(text))
        if count:
            text = PATTERNS["basic_auth"].sub("Basic [AUTH_REDACTED]", text)
            self._report["tokens_removed"] += count

        # Remove session IDs
        count = len(PATTERNS["session_id"].findall(text))
        if count:
            text = PATTERNS["session_id"].sub("[SESSION_REDACTED]", text)
            self._report["sessions_removed"] += count

        # Remove AWS keys
        text = PATTERNS["aws_key"].sub("[AWS_KEY_REDACTED]", text)

        # In strict mode, also remove internal IPs
        if self.strict:
            text = PATTERNS["ip_address"].sub("[IP_REDACTED]", text)

        return text

    def get_report(self) -> Dict[str, int]:
        """Get the sanitization report with counts."""
        return self._report.copy()

    def validate_json(self, data: Dict[str, Any]) -> bool:
        """
        Validate that sanitized JSON maintains structural integrity.

        Args:
            data: Sanitized data dict

        Returns:
            True if valid
        """
        try:
            # Test round-trip JSON serialization
            json_str = json.dumps(data, default=str)
            reparsed = json.loads(json_str)

            # Verify essential structure
            assert "endpoints" in reparsed, "Missing 'endpoints' key"
            assert isinstance(reparsed["endpoints"], list), "'endpoints' is not a list"

            # Check no raw sensitive data leaked
            json_lower = json_str.lower()
            for pattern_name, pattern in PATTERNS.items():
                matches = pattern.findall(json_str)
                if matches and pattern_name not in ("ip_address",):
                    logger.warning(
                        f"Potential sensitive data leak: {pattern_name} "
                        f"({len(matches)} matches found after sanitization)"
                    )
                    return False

            return True

        except Exception as e:
            logger.error(f"JSON validation failed: {e}")
            return False
