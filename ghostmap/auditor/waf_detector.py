"""
GHOSTMAP WAF Detector — Identify Web Application Firewalls and protection mechanisms.
"""

import logging
import requests
import time
from typing import Dict, Tuple, Optional
from ghostmap.utils.http_client import RateLimitedClient

logger = logging.getLogger("ghostmap.auditor.waf_detector")

class WafDetector:
    """
    Detects if a target is protected by a WAF or rate limiting system.
    """

    def __init__(self, config=None):
        self.config = config
        self.client = RateLimitedClient(config)

    def detect(self, url: str) -> Tuple[bool, str, float]:
        """
        Check for WAF presence.
        
        Returns:
            (is_waf_detected, waf_name, suggested_rate_limit)
        """
        is_waf = False
        waf_name = "Unknown WAF"
        suggested_limit = 0.0  # 0 means no suggestion/change

        try:
            # 1. Passive Header Analysis
            response = self.client.get(url, timeout=10, verify=False)
            headers = response.headers
            
            # Known WAF Headers
            server = headers.get("Server", "").lower()
            via = headers.get("Via", "").lower()
            x_cdn = headers.get("X-CDN", "").lower()
            cf_ray = headers.get("CF-RAY", "")

            if "cloudflare" in server or cf_ray:
                is_waf = True
                waf_name = "Cloudflare"
            elif "akamai" in server or "akamai" in via:
                is_waf = True
                waf_name = "Akamai"
            elif "aws" in server or "cloudfront" in via:
                is_waf = True
                waf_name = "AWS CloudFront"
            elif "imperva" in server or "incapsula" in via:
                is_waf = True
                waf_name = "Imperva/Incapsula"
            
            if is_waf:
                logger.info(f"Passive WAF Detection: {waf_name}")
                return True, waf_name, 2.0  # Conservative limit for known CDNs

            # 2. Active Behavior Analysis (Benign Payloads)
            # Send a payload that WAFs hate but is harmless
            payloads = [
                "<script>alert(1)</script>",
                "' OR 1=1 --"
            ]
            
            for p in payloads:
                # Append to URL query
                test_url = f"{url}/?id={p}"
                resp = self.client.get(test_url, timeout=5, verify=False)
                
                # If blocked (403/406) but normal request was 200/404 -> WAF
                if resp.status_code in (403, 406, 501) and response.status_code not in (403, 406, 501):
                    is_waf = True
                    waf_name = "Generic WAF (Behavioral)"
                    logger.info(f"Active WAF Detection: Blocked payload '{p}' with {resp.status_code}")
                    return True, waf_name, 1.0  # Very conservative for strict WAFs
                
                time.sleep(0.5)

        except Exception as e:
            logger.warning(f"WAF detection failed: {e}")

        return False, "", 0.0
