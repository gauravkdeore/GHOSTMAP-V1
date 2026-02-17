# Default Fuzzing Wordlists
# These are used by the Smart Fuzzer

COMMON = [
    ".env",
    "robots.txt",
    "sitemap.xml",
    ".git/HEAD",
    ".vscode/settings.json",
    "backup.zip",
    "backup.sql",
    "dump.sql",
    "admin/",
    "administrator/",
    "login/",
    "dashboard/",
    "api/",
    "api/v1/",
    "graphql",
    "swagger.json",
    "openapi.json",
    ".DS_Store",
    "server-status",
    "elmah.axd",
    "web.config",
    "manifest.json",
]

# Cloud & DevOps (Always useful to check)
CLOUD_DEVOPS = [
    ".aws/credentials",
    ".aws/config",
    ".env",
    ".env.local",
    ".env.dev",
    ".env.prod",
    "docker-compose.yml",
    "Dockerfile",
    ".gitlab-ci.yml",
    ".circleci/config.yml",
    ".travis.yml",
    "jenkins/",
    "kube-system/",
    "config/k8s.yml",
]

# CMS & Servers
WORDPRESS = [
    "wp-admin/",
    "wp-login.php",
    "wp-config.php",
    "wp-config.php.bak",
    "wp-includes/",
    "xmlrpc.php",
]

TOMCAT = [
    "manager/html",
    "manager/status",
    "host-manager/html",
    "examples/servlets/",
]

JBOSS = [
    "jmx-console/",
    "web-console/",
    "invoker/JMXInvokerServlet",
]

DRUPAL = [
    "user/login",
    "CHANGELOG.txt",
    "sites/default/settings.php",
]

SPRING = [
    "actuator",
    "actuator/health",
    "actuator/info",
    "actuator/env",
    "actuator/heapdump",
    "actuator/mappings",
    "actuator/metrics",
    "actuator/beans",
    "actuator/configprops",
    "h2-console",
]

DJANGO = [
    "admin/",
    "admin/login/",
    "static/admin/",
    "__debug__/",
]

RAILS = [
    "rails/info/properties",
    "rails/info/routes",
    "rails/info",
]

PHP = [
    "phpinfo.php",
    "info.php",
    "config.php",
    "wp-admin/",
    "wp-login.php",
    "composer.json",
    "composer.lock",
]

NODE = [
    "package.json",
    "package-lock.json",
    "node_modules/",
]

LIFERAY = [
    "api/jsonws",
    "api/jsonws/invoke",
    "c/portal/login",
    "web/guest/home",
    "group/control_panel",
    "image/image_gallery",
]

# Map technology tags to wordlists
WORDLISTS = {
    "common": COMMON,
    "spring": SPRING,
    "django": DJANGO,
    "rails": RAILS,
    "php": PHP,
    "node": NODE,
    "liferay": LIFERAY,
    "wordpress": WORDPRESS,
    "tomcat": TOMCAT,
    "jboss": JBOSS,
    "drupal": DRUPAL,
}

# Add Cloud/DevOps to Common?
# Or keep separate? Let's add them to COMMON for maximum coverage in standard scans
COMMON.extend(CLOUD_DEVOPS)
