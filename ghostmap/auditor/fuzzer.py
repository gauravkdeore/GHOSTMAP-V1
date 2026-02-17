import logging
from typing import List, Dict
from ghostmap.auditor.tech_detector import TechDetector
from ghostmap.auditor.wordlists import WORDLISTS, COMMON
from ghostmap.utils.http_client import RateLimitedClient

logger = logging.getLogger("ghostmap.fuzzer")

class GhostFuzzer:
    """
    Active Reconnaissance engine for discovering hidden endpoints via wordlists.
    """

    def __init__(self, config):
        self.config = config
        self.detector = TechDetector(config)

    def fuzz(self, base_url: str, mode: str = "auto") -> List[Dict]:
        """
        Fuzz the target base URL for common hidden files and directories.
        
        Args:
            base_url: The root URL (e.g., https://example.com)
            mode: "all" (brute-force all lists) or "auto" (detect tech first)
        
        Returns:
            List of found endpoints with metadata.
        """
        if not base_url.startswith("http"):
            base_url = f"https://{base_url}"
        
        base_url = base_url.rstrip("/")
        normalized_url = base_url
        
        # Determine wordlists
        target_lists = []
        
        if mode == "auto":
            # Detect technology
            tags = self.detector.detect(base_url, headers=self.config.headers)
            logger.info(f"Fuzzing mode: AUTO. Detected tags: {tags}")
            
            for tag in tags:
                if tag in WORDLISTS:
                    target_lists.extend(WORDLISTS[tag])
        else:
            # ALL mode
            logger.info("Fuzzing mode: ALL. Enabling all wordlists.")
            for lst in WORDLISTS.values():
                target_lists.extend(lst)
        
        # Deduplicate payloads
        payloads = sorted(list(set(target_lists)))
        logger.info(f"Generated {len(payloads)} payloads for fuzzing.")
        
        found_endpoints = []
        
        with RateLimitedClient(self.config) as client:
            # Step 1: Establish Baseline (Soft 404 Detection)
            import uuid
            baseline = None
            try:
                # Probe a random non-existent path
                rand_path = f"{normalized_url}/{uuid.uuid4()}"
                b_resp = client.get(rand_path, timeout=5, allow_redirects=False)
                baseline = {
                    "status": b_resp.status_code,
                    "length": len(b_resp.content),
                    "location": b_resp.headers.get("Location", "")
                }
                logger.info(f"Baseline (Random Path) response: Status={baseline['status']}, Len={baseline['length']}, Loc={baseline['location']}")
            except Exception as e:
                logger.warning(f"Failed to establish baseline: {e}")

            # Step 2: Fuzz Loop
            for payload in payloads:
                target = f"{normalized_url}/{payload}"
                try:
                    response = client.get(target, timeout=5, allow_redirects=False)
                    status = response.status_code
                    length = len(response.content)
                    location = response.headers.get("Location", "")
                    
                    # Interest criteria: Not 404
                    if status != 404:
                        # Soft 404 Check
                        if baseline:
                            # If status matches baseline
                            if status == baseline["status"]:
                                # If it's a redirect, check if location is similar
                                if status in (301, 302, 307, 308):
                                    if location == baseline["location"]:
                                        logger.debug(f"SOFT 404 ignored: {target} (Redirect match)")
                                        continue
                                
                                # If response length is very close (within 10%)
                                len_diff = abs(length - baseline["length"])
                                if len_diff < (baseline["length"] * 0.1) + 10:  # +10 bytes tolerance
                                    logger.debug(f"SOFT 404 ignored: {target} (Length match)")
                                    continue
                        
                        logger.info(f"FOUND: {target} [{status}]")
                        
                        found_endpoints.append({
                            "endpoint": target,
                            "status": status,
                            "source": "ghost_fuzzer",
                            "method": "GET",
                            "payload": payload,
                            "length": length
                        })
                except Exception as e:
                    logger.debug(f"Failed to probe {target}: {e}")
        
        return found_endpoints
