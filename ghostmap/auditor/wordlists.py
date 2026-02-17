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
    ".well-known/security.txt",
    ".well-known/openid-configuration",
    "api-docs",
    "v2/api-docs",
    "swagger-ui.html",
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
    ".kube/config",
    "id_rsa",
    "id_rsa.pub",
    ".docker/config.json",
    "daemon.json",
]

# Web Servers
NGINX = [
    "nginx.conf",
    "nginx_status",
    "/usr/local/nginx/conf/nginx.conf",
    "etc/nginx/nginx.conf",
    ".nginx",
]

APACHE = [
    ".htaccess",
    ".htpasswd",
    "server-status",
    "server-info",
    "balancer-manager",
]

IIS = [
    "web.config",
    "Global.asax",
    "iisstart.htm",
    "Trace.axd",
]

# API & Modern Web
GRAPHQL = [
    "graphql",
    "graphiql",
    "api/graphql",
    "v1/graphql",
    "graphql/console",
    "explorer",
    "altair",
    "playground",
]

# CMS & Servers
WORDPRESS = [
    "wp-admin/",
    "wp-login.php",
    "wp-config.php",
    "wp-config.php.bak",
    "wp-includes/",
    "xmlrpc.php",
    "wp-content/uploads/",
    "readme.html",
    "license.txt",
    "wp-content/debug.log",
    "wp-json/wp/v2/users",  # User enumeration
    "wp-json/wp/v2/posts",
]

TOMCAT = [
    "manager/html",
    "manager/status",
    "host-manager/html",
    "examples/servlets/",
    "docs/",
    "RELEASE-NOTES.txt",
]

JBOSS = [
    "jmx-console/",
    "web-console/",
    "invoker/JMXInvokerServlet",
    "admin-console/",
]

DRUPAL = [
    "user/login",
    "CHANGELOG.txt",
    "sites/default/settings.php",
    "install.php",
    "UPGRADE.txt",
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
    "actuator/gateway/routes",
    "actuator/logfile",
    "actuator/prometheus",
    "actuator/threaddump",
    "actuator/conditions",
    "actuator/auditevents",
]

DJANGO = [
    "admin/",
    "admin/login/",
    "static/admin/",
    "__debug__/",
    "db.sqlite3",
]

RAILS = [
    "rails/info/properties",
    "rails/info/routes",
    "rails/info",
    "config/database.yml",
]

PHP = [
    "phpinfo.php",
    "info.php",
    "config.php",
    "wp-admin/",
    "wp-login.php",
    "composer.json",
    "composer.lock",
    "test.php",
]

NODE = [
    "package.json",
    "package-lock.json",
    "node_modules/",
    "npm-debug.log",
    "yarn.lock",
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
    "nginx": NGINX,
    "apache": APACHE,
    "iis": IIS,
    "graphql": GRAPHQL,
}

# Add Cloud/DevOps to Common?
# Or keep separate? Let's add them to COMMON for maximum coverage in standard scans
COMMON.extend(CLOUD_DEVOPS)
