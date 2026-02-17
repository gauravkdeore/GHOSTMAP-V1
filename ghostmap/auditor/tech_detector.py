import logging
import requests
from typing import List, Dict

logger = logging.getLogger("ghostmap.tech_detector")

class TechDetector:
    """
    Identifies the technology stack of a target URL to enable smart fuzzing.
    """

    def __init__(self, config=None):
        self.config = config

    def detect(self, url: str, headers: Dict[str, str] = None) -> List[str]:
        """
        Detect technologies based on headers and response signatures.
        Returns a list of tags: ['spring', 'php', 'django', 'nginx', etc.]
        """
        tags = set()
        tags.add("common")  # Always include common payloads

        try:
            # Send a simple GET request
            # We use verify=False to avoid SSL issues during probing
            # Use short timeout
            response = requests.get(url, headers=headers, timeout=5, verify=False)
            
            # 1. Analyze Headers
            server = response.headers.get("Server", "").lower()
            x_powered_by = response.headers.get("X-Powered-By", "").lower()
            cookies = response.headers.get("Set-Cookie", "").lower()

            if "php" in x_powered_by or "php" in cookies or "phpsessid" in cookies:
                tags.add("php")
            
            if "asp.net" in x_powered_by or "asp.net" in cookies or "aspnet" in cookies:
                tags.add("asp")

            if "express" in x_powered_by or "node" in x_powered_by:
                tags.add("node")

            if "gunicorn" in server or "python" in server or "django" in cookies or "csrftoken" in cookies:
                tags.add("django")  # Broad python/django assumption
            
            # 2. Analyze Body for fingerprints
            text = response.text.lower()
            
            if "whitelabel error page" in text or "spring boot" in text:
                tags.add("spring")

            if "laravel" in text:
                tags.add("php")
                tags.add("laravel")

            if "rails" in text:
                tags.add("rails")

            if "liferay" in text or "liferay" in headers.get("Liferay-Portal", "").lower():
                tags.add("liferay")

            # CMS / Server Detection
            if "wordpress" in text or "wp-content" in text:
                tags.add("wordpress")
                tags.add("php")
            
            if "drupal" in text or "drupal" in headers.get("X-Generator", "").lower():
                tags.add("drupal")
                tags.add("php")

            if "apache-coyote" in server or "tomcat" in text:
                tags.add("tomcat")
                tags.add("java")

            if "jboss" in server or "jboss" in text:
                tags.add("jboss")
                tags.add("java")

        except Exception as e:
            logger.debug(f"Tech detection failed for {url}: {e}")

        logger.info(f"Detected technologies for {url}: {list(tags)}")
        return list(tags)
