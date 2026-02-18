# =============================================================================
# GHOSTMAP Comprehensive Wordlists
# =============================================================================
# Curated payloads for Smart Fuzzing, organized by technology stack.
# These are used by the TechDetector to select relevant paths only.
# =============================================================================

# =============================================================================
# COMMON - Always checked regardless of technology
# =============================================================================
COMMON = [
    # Configuration & Secrets
    ".env", ".env.local", ".env.dev", ".env.development", ".env.prod",
    ".env.production", ".env.staging", ".env.test", ".env.backup",
    ".env.old", ".env.save", ".env.bak", ".env.example", ".env.sample",
    "env.js", "env.json", "config.json", "config.yaml", "config.yml",
    "config.xml", "config.ini", "config.php", "config.js", "config.ts",
    "configuration.php", "settings.json", "settings.yaml", "settings.py",
    "settings.ini", "secrets.json", "secrets.yaml", "secrets.yml",
    "credentials.json", "credentials.xml",
    
    # Version Control
    ".git/", ".git/HEAD", ".git/config", ".git/index", ".git/logs/HEAD",
    ".git/COMMIT_EDITMSG", ".gitignore", ".gitattributes",
    ".svn/", ".svn/entries", ".svn/wc.db",
    ".hg/", ".hg/hgrc", ".bzr/", "CVS/", "CVS/Root", "CVS/Entries",
    
    # IDE & Editor
    ".vscode/", ".vscode/settings.json", ".vscode/launch.json",
    ".idea/", ".idea/workspace.xml", ".idea/modules.xml",
    ".project", ".classpath", ".settings/", ".editorconfig",
    
    # Backup Files
    "backup/", "backups/", "backup.zip", "backup.tar.gz", "backup.sql",
    "backup.sql.gz", "backup.tar", "backup.rar", "db_backup.sql",
    "database.sql", "database_backup.sql", "dump.sql", "dump.sql.gz",
    "data.sql", "mysql.sql", "site_backup.zip", "www.zip", "html.zip",
    "public_html.zip", "httpdocs.zip", "web.zip", "old/", "old.zip",
    "archive/", "archive.zip", "temp/", "tmp/", "cache/", "bak/", "copy/",
    
    # Logs
    "logs/", "log/", "log.txt", "logs.txt", "error.log", "errors.log",
    "error_log", "debug.log", "access.log", "access_log", "app.log",
    "application.log", "server.log", "system.log", "storage/logs/", "var/log/",
    
    # Documentation & API Specs
    "swagger.json", "swagger.yaml", "swagger.yml", "swagger/", "swagger-ui/",
    "swagger-ui.html", "api-docs", "api-docs/", "api-docs.json", "api-docs.yaml",
    "openapi.json", "openapi.yaml", "openapi.yml", "openapi/",
    "docs/", "doc/", "documentation/", "api/", "api/v1/", "api/v2/", "api/v3/",
    "api/docs", "api/swagger", "api/openapi", "redoc", "rapidoc",
    
    # Admin & Auth
    "admin/", "admin.php", "admin.html", "administrator/", "administration/",
    "admin-panel/", "adminpanel/", "panel/", "controlpanel/", "control-panel/",
    "cpanel/", "dashboard/", "manage/", "manager/", "management/",
    "backend/", "backoffice/", "cms/", "console/", "portal/",
    "login/", "login.php", "login.html", "signin/", "sign-in/",
    "auth/", "authenticate/", "authentication/", "oauth/", "oauth2/",
    "sso/", "saml/", "logout/", "signout/", "sign-out/",
    "register/", "signup/", "sign-up/", "registration/",
    "forgot-password/", "reset-password/", "password-reset/", "recover/",
    "2fa/", "mfa/",
    
    # User & Profile
    "user/", "users/", "profile/", "profiles/", "account/", "accounts/",
    "member/", "members/", "me/", "my-account/", "myaccount/",
    "settings/", "preferences/",
    
    # Server Info
    "server-status", "server-info", "status", "status/", "health", "health/",
    "healthcheck", "healthcheck/", "health-check", "ping", "ping/",
    "version", "version/", "info", "info/", "about",
    "metrics", "metrics/", "stats", "stats/", "statistics/",
    
    # Common Files
    "robots.txt", "sitemap.xml", "sitemap_index.xml", "sitemaps/",
    "crossdomain.xml", "clientaccesspolicy.xml", "security.txt",
    ".well-known/", ".well-known/security.txt", ".well-known/openid-configuration",
    ".well-known/jwks.json", ".well-known/assetlinks.json",
    ".well-known/apple-app-site-association",
    "favicon.ico", "manifest.json", "browserconfig.xml", "humans.txt",
    "ads.txt", "app-ads.txt", "license.txt", "readme.txt", "readme.md",
    "README.md", "CHANGELOG.md", "changelog.txt", "VERSION", "version.txt",
    
    # Debug & Test
    "debug/", "debug.php", "test/", "test.php", "test.html", "tests/",
    "testing/", "phpunit/", "spec/", "specs/", "example/", "examples/",
    "sample/", "samples/", "demo/", "sandbox/", "dev/", "development/",
    "staging/", "stage/", "uat/", "qa/", "trace/", "trace.axd", "elmah.axd",
    
    # File Uploads
    "upload/", "uploads/", "file/", "files/", "media/", "images/", "img/",
    "assets/", "static/", "resources/", "attachments/", "documents/",
    "download/", "downloads/", "export/", "exports/", "import/", "imports/",
    
    # Database
    "phpmyadmin/", "phpMyAdmin/", "pma/", "mysql/", "myadmin/",
    "adminer/", "adminer.php", "db/", "database/", "sql/",
    "pgadmin/", "mongo/", "mongodb/", "redis/", "memcached/",
    "elasticsearch/", "_elastic/", "solr/",
    
    # WebSocket & Real-time
    "ws/", "wss/", "socket/", "sockets/", "websocket/", "websockets/",
    "socket.io/", "sockjs/", "signalr/", "hub/", "hubs/",
    "realtime/", "live/", "events/", "stream/", "streaming/",
    "sse/", "push/", "notifications/",
    
    # GraphQL
    "graphql", "graphql/", "graphiql", "graphiql/", "playground", "playground/",
    "graphql-playground", "altair", "voyager", "graphql/schema",
    "graphql/console", "__graphql",
    
    # Webhooks & Callbacks
    "webhook/", "webhooks/", "callback/", "callbacks/", "hook/", "hooks/",
    "notify/", "notification/", "ipn/", "postback/",
    
    # Internal/Private
    "internal/", "private/", "secret/", "hidden/", "restricted/",
    "secure/", "protected/",
    
    # Error Pages
    "error/", "errors/", "404", "404.html", "500", "500.html",
    "error.html", "error.php",
]

# =============================================================================
# CLOUD & DEVOPS
# =============================================================================
CLOUD_DEVOPS = [
    # AWS
    ".aws/", ".aws/credentials", ".aws/config", "aws.yml", "aws.yaml",
    "aws-config.json", "s3/", "lambda/", "cloudformation/",
    ".elasticbeanstalk/", "ecs-params.yml", "task-definition.json",
    "appspec.yml", "appspec.yaml", "buildspec.yml", "buildspec.yaml",
    "samconfig.toml", "template.yaml", "template.yml",
    "serverless.yml", "serverless.yaml", "amplify.yml", "amplify/",
    "cdk.json", "cdk.context.json",
    
    # Azure
    ".azure/", "azure-pipelines.yml", "azure-pipelines.yaml",
    "azuredeploy.json", "azuredeploy.parameters.json", ".deployment",
    "host.json", "local.settings.json", "proxies.json", "extensions.json",
    
    # GCP
    ".gcloud/", "app.yaml", "app.yml", "cloudbuild.yaml", "cloudbuild.yml",
    ".gcloudignore", "service-account.json", "credentials.json", "gcp-key.json",
    "firebase.json", ".firebaserc", "firestore.rules", "storage.rules",
    "remoteconfig.template.json",
    
    # Docker
    "Dockerfile", "Dockerfile.dev", "Dockerfile.prod", "Dockerfile.test",
    "docker-compose.yml", "docker-compose.yaml", "docker-compose.dev.yml",
    "docker-compose.prod.yml", "docker-compose.override.yml",
    ".dockerignore", "docker/", ".docker/", "containers/",
    
    # Kubernetes
    "kubernetes/", "k8s/", "kube/", "manifests/", "deployment.yaml",
    "deployment.yml", "service.yaml", "service.yml", "ingress.yaml",
    "ingress.yml", "configmap.yaml", "secret.yaml", "kustomization.yaml",
    "kustomization.yml", "Chart.yaml", "values.yaml", "values.yml",
    "helmfile.yaml", "skaffold.yaml", "tilt.json", "Tiltfile", "garden.yml",
    
    # Terraform
    "terraform/", "main.tf", "variables.tf", "outputs.tf", "providers.tf",
    "backend.tf", "terraform.tfvars", "terraform.tfstate",
    "terraform.tfstate.backup", ".terraform/", ".terraform.lock.hcl",
    "terragrunt.hcl",
    
    # Ansible
    "ansible/", "playbook.yml", "playbooks/", "inventory/", "inventory.ini",
    "hosts", "ansible.cfg", "group_vars/", "host_vars/", "roles/",
    "vault.yml", ".vault_pass",
    
    # CI/CD
    ".github/", ".github/workflows/", ".gitlab-ci.yml", ".gitlab/",
    "Jenkinsfile", "jenkins/", ".jenkins/", ".circleci/", ".circleci/config.yml",
    ".travis.yml", "travis.yml", ".drone.yml", "drone.yml",
    "bitbucket-pipelines.yml", "wercker.yml", "codefresh.yml", ".codefresh/",
    "codeship-services.yml", "codeship-steps.yml", "tekton/", "argocd/",
    "flux/", "buildkite/", ".buildkite/", "pipeline.yml", "buddy.yml",
    ".buddy/", "semaphore.yml", ".semaphore/", "appveyor.yml", ".appveyor.yml",
    "shippable.yml", "netlify.toml", "vercel.json", "now.json",
    "render.yaml", "heroku.yml", "Procfile", "app.json", "scalingo.json",
    "railway.json", "fly.toml", "dagger.cue", "earthly/", "Earthfile",
    
    # Monitoring
    "prometheus/", "prometheus.yml", "alertmanager.yml", "grafana/",
    "dashboards/", "datadog.yaml", "newrelic.yml", "sentry.properties",
    ".sentryclirc", "rollbar.json", "bugsnag.json", "airbrake.json",
    "honeybadger.yml", "elastic-apm.yml", "jaeger/", "zipkin/",
    "opentelemetry/", "otel-collector-config.yaml",
    
    # Vagrant
    "Vagrantfile", ".vagrant/", "vagrant/",
]

# =============================================================================
# JAVA / SPRING BOOT
# =============================================================================
SPRING = [
    # Actuator Endpoints (Spring Boot 2.x+)
    "actuator", "actuator/", "actuator/health", "actuator/health/liveness",
    "actuator/health/readiness", "actuator/info", "actuator/env",
    "actuator/env.json", "actuator/beans", "actuator/beans.json",
    "actuator/configprops", "actuator/configprops.json", "actuator/mappings",
    "actuator/mappings.json", "actuator/metrics", "actuator/metrics.json",
    "actuator/loggers", "actuator/loggers.json", "actuator/heapdump",
    "actuator/threaddump", "actuator/conditions", "actuator/scheduledtasks",
    "actuator/httptrace", "actuator/trace", "actuator/auditevents",
    "actuator/caches", "actuator/flyway", "actuator/liquibase",
    "actuator/sessions", "actuator/shutdown", "actuator/startup",
    "actuator/prometheus", "actuator/jolokia", "actuator/logfile",
    "actuator/refresh", "actuator/restart", "actuator/pause", "actuator/resume",
    "actuator/gateway/", "actuator/gateway/routes", "actuator/gateway/globalfilters",
    "actuator/gateway/routefilters", "actuator/integrationgraph",
    "actuator/quartz", "actuator/sbom",
    
    # Legacy Spring Boot 1.x
    "health", "info", "env", "beans", "mappings", "metrics", "trace",
    "dump", "autoconfig", "configprops", "loggers",
    
    # Spring Security
    "login", "logout", "oauth/authorize", "oauth/token", "oauth/check_token",
    "oauth/token_key", "oauth/confirm_access", "oauth/error",
    ".well-known/jwks.json", "userinfo", "introspect", "revoke",
    
    # Spring Cloud
    "bus/refresh", "bus-refresh", "features", "decrypt", "encrypt",
    "refresh", "restart", "resume", "pause", "service-registry",
    "hystrix.stream", "turbine.stream", "clusters",
    
    # Spring Cloud Gateway
    "gateway/actuator", "gateway/routes", "routes",
    
    # H2 Console
    "h2-console", "h2-console/", "h2/", "database/", "db-console/",
    
    # Swagger/OpenAPI
    "swagger-ui/", "swagger-ui.html", "swagger-resources",
    "swagger-resources/", "swagger-resources/configuration/ui",
    "swagger-resources/configuration/security", "v2/api-docs",
    "v3/api-docs", "v3/api-docs.yaml", "webjars/",
    
    # Druid Monitor
    "druid/", "druid/index.html", "druid/login.html", "druid/sql.html",
    "druid/weburi.html", "druid/datasource.html",
    
    # Config Files
    "application.properties", "application.yml", "application.yaml",
    "bootstrap.properties", "bootstrap.yml", "application-dev.yml",
    "application-prod.yml", "application-local.yml",
]

# =============================================================================
# JAVA EE / JAKARTA EE
# =============================================================================
JAVA = [
    # Servlets & JSP
    "index.jsp", "default.jsp", "admin.jsp", "login.jsp", "error.jsp",
    "test.jsp", "info.jsp", "debug.jsp", "status.jsp", "version.jsp",
    "WEB-INF/", "WEB-INF/web.xml", "WEB-INF/classes/", "WEB-INF/lib/",
    "META-INF/", "META-INF/MANIFEST.MF", "META-INF/context.xml",
    
    # JAX-RS
    "rest/", "api/", "ws/", "services/", "resources/", "webresources/",
    "jersey/", "resteasy/",
    
    # JMX
    "jmx/", "jmx-console/", "jolokia/", "jolokia/read", "jolokia/list",
    "jolokia/exec", "jolokia/search", "jolokia/version",
    
    # Common
    "j_security_check", "j_spring_security_check", "j_acegi_security_check",
]

# =============================================================================
# TOMCAT
# =============================================================================
TOMCAT = [
    "manager/", "manager/html", "manager/html/", "manager/text", "manager/text/",
    "manager/jmxproxy", "manager/jmxproxy/", "manager/status", "manager/status/",
    "manager/status/all", "host-manager/", "host-manager/html", "host-manager/html/",
    "host-manager/text", "examples/", "examples/servlets/", "examples/jsp/",
    "examples/websocket/", "examples/async/", "docs/", "tomcat-docs/",
    "status", "server-status", "conf/", "conf/server.xml", "conf/tomcat-users.xml",
    "conf/context.xml", "conf/web.xml", "RELEASE-NOTES.txt",
]

# =============================================================================
# JBOSS / WILDFLY
# =============================================================================
JBOSS = [
    "jmx-console/", "jmx-console/HtmlAdaptor", "jmx-console/htmladaptor",
    "jmx-console/checkJNDI.jsp", "web-console/", "web-console/ServerInfo.jsp",
    "web-console/Invoker", "web-console/status", "admin-console/",
    "admin-console/login.seam", "invoker/", "invoker/EJBInvokerServlet",
    "invoker/JMXInvokerServlet", "invoker/JNDIFactory", "invoker/readonly",
    "jbossws/", "jbossws/services", "jmx-remoting/", "jndi/",
    "management/", "console/", "console/App.html", "seam/", "seam/resource/",
    "resteasy/", "hawtio/", "jolokia/",
]

# =============================================================================
# WEBLOGIC
# =============================================================================
WEBLOGIC = [
    "console/", "console/login/LoginForm.jsp", "console/j_security_check",
    "consolehelp/", "bea_wls_internal/", "bea_wls_deployment_internal/",
    "uddiexplorer/", "uddilistener/", "uddiadmin/", "ws_utc/", "_async/",
    "wls-wsat/", "wls-wsat/CoordinatorPortType", "wls-wsat/CoordinatorPortType11",
    "wls-wsat/ParticipantPortType", "wls-wsat/ParticipantPortType11",
    "wls-wsat/RegistrationPortTypeRPC", "wls-wsat/RegistrationPortTypeRPC11",
    "management/", "management/weblogic/", "HttpClusterServlet",
    "bea_wls_cluster_internal/",
]

# =============================================================================
# PYTHON / DJANGO
# =============================================================================
DJANGO = [
    "admin/", "admin/login/", "admin/logout/", "admin/password_change/",
    "admin/password_reset/", "admin/jsi18n/", "admin/r/", "admin/auth/",
    "admin/contenttypes/", "admin/sessions/",
    "__debug__/", "__debug__/sql/", "__debug__/request_sql/",
    "__debug__/template_source/", "debug/", "silk/",
    "static/", "static/admin/", "media/", "assets/",
    "api/", "api-auth/", "api-auth/login/", "api-auth/logout/",
    "api-token-auth/", "api-token-refresh/", "api-token-verify/",
    "docs/", "openapi/", "openapi.json", "openapi.yaml", "redoc/", "swagger/",
    "accounts/", "accounts/login/", "accounts/logout/", "accounts/signup/",
    "accounts/password/reset/", "accounts/social/",
    "manage.py", "settings.py", "urls.py", "wsgi.py", "asgi.py",
    "requirements.txt", "Pipfile", "Pipfile.lock", "pyproject.toml",
    "poetry.lock", "setup.py", "setup.cfg", "flower/",
]

# =============================================================================
# PYTHON / FLASK
# =============================================================================
FLASK = [
    "admin/", "flask-admin/", "login", "logout", "register", "reset",
    "change", "confirm", "api/", "swagger/", "swagger.json", "apidocs/",
    "doc/", "console", "debugger", "__debugger__",
    "app.py", "wsgi.py", "config.py", "requirements.txt", "Procfile",
    "db/", "migrate/", "migrations/",
]

# =============================================================================
# PYTHON / FASTAPI
# =============================================================================
FASTAPI = [
    "docs", "docs/", "redoc", "redoc/", "openapi.json", "openapi/",
    "health", "health/", "healthz", "readiness", "liveness",
    "api/", "api/v1/", "api/v2/", "auth/", "token", "token/",
    "login", "logout", "users/me", "users/me/", "ws/", "ws",
    "static/", "main.py", "app.py", "requirements.txt", "pyproject.toml",
    "alembic/", "alembic.ini",
]

# =============================================================================
# PHP COMMON
# =============================================================================
PHP = [
    "phpinfo.php", "info.php", "php_info.php", "i.php", "test.php",
    "debug.php", "status.php", "php-info.php", "phpversion.php",
    "version.php", "check.php", "apc.php", "opcache.php", "opcache-status.php",
    "config.php", "configuration.php", "settings.php", "config.inc.php",
    "db.php", "database.php", "connect.php", "conn.php", "connection.php",
    "db.inc.php", "db_connect.php", "dbconfig.php", "constants.php",
    "defines.php", "global.php", "globals.php", "common.php", "init.php",
    "bootstrap.php", "autoload.php", "functions.php",
    "composer.json", "composer.lock", "vendor/", "vendor/autoload.php",
    "index.php", "admin.php", "login.php", "logout.php", "register.php",
    "user.php", "users.php", "member.php", "profile.php", "account.php",
    "search.php", "download.php", "upload.php", "file.php", "page.php",
    "api.php", "ajax.php", "action.php", "process.php", "handler.php",
    "callback.php", "cron.php", "install.php", "setup.php", "update.php",
    "upgrade.php", "installer.php", "maintenance.php",
    "config.php.bak", "config.php.old", "config.php.save", "config.php~",
    "config.php.swp", ".config.php.swp", "config.old.php", "config.backup.php",
    ".htaccess", "web.config", "php.ini", ".user.ini",
]

# =============================================================================
# LARAVEL
# =============================================================================
LARAVEL = [
    "_debugbar/", "telescope/", "telescope/api/", "horizon/", "horizon/api/",
    "nova/", "nova-api/", "api/", "api/user", "api/v1/",
    "sanctum/csrf-cookie", "broadcasting/auth",
    "login", "logout", "register", "password/email", "password/reset",
    "email/verify", "email/resend", "two-factor-challenge",
    "storage/", "storage/logs/", "storage/app/", "storage/framework/",
    "storage/logs/laravel.log", "public/", "css/", "js/", "build/", "vendor/",
    ".env", ".env.example", ".env.local", ".env.testing", "artisan",
    "composer.json", "composer.lock", "package.json", "webpack.mix.js",
    "vite.config.js", "_ignition/", "_ignition/health-check",
    "_ignition/execute-solution", "_ignition/share-report",
    "_ignition/scripts/", "_ignition/styles/", "laravel.log",
]

# =============================================================================
# SYMFONY
# =============================================================================
SYMFONY = [
    "_profiler/", "_profiler/phpinfo", "_profiler/open", "_profiler/info",
    "_profiler/latest", "_wdt/", "_error/", "_configurator/",
    "_check_requirements", "login", "logout", "login_check",
    "_security_check", "api/login", "api/register",
    "api/", "api/docs", "api/docs.json", "api/docs.jsonld", "api/docs.html",
    "api/contexts/", "api/entrypoint", "api/graphql", "api/graphql/graphiql",
    "bundles/", "build/", "public/", "config/", "var/", "var/log/",
    "var/cache/", "vendor/", "composer.json", "composer.lock", "symfony.lock",
    ".env", ".env.local", ".env.dev", ".env.prod", ".env.test",
]

# =============================================================================
# WORDPRESS
# =============================================================================
WORDPRESS = [
    "wp-admin/", "wp-admin/admin-ajax.php", "wp-admin/admin-post.php",
    "wp-admin/options-general.php", "wp-admin/users.php", "wp-admin/plugins.php",
    "wp-admin/themes.php", "wp-admin/update-core.php", "wp-admin/install.php",
    "wp-admin/setup-config.php", "wp-admin/upgrade.php",
    "wp-login.php", "wp-signup.php", "wp-register.php", "wp-cron.php",
    "wp-mail.php", "wp-links-opml.php", "wp-trackback.php", "wp-comments-post.php",
    "wp-config.php", "wp-config.php.bak", "wp-config.php.old", "wp-config.php.save",
    "wp-config.php.swp", "wp-config.php~", "wp-config-sample.php", "wp-settings.php",
    "wp-content/", "wp-content/plugins/", "wp-content/themes/",
    "wp-content/uploads/", "wp-content/debug.log", "wp-content/upgrade/",
    "wp-content/cache/", "wp-content/backups/", "wp-content/backup-db/",
    "wp-content/mu-plugins/",
    "wp-includes/", "wp-includes/version.php", "wp-includes/css/", "wp-includes/js/",
    "wp-json/", "wp-json/wp/v2/", "wp-json/wp/v2/users", "wp-json/wp/v2/posts",
    "wp-json/wp/v2/pages", "wp-json/wp/v2/categories", "wp-json/wp/v2/tags",
    "wp-json/wp/v2/comments", "wp-json/wp/v2/media", "wp-json/wp/v2/types",
    "wp-json/wp/v2/statuses", "wp-json/wp/v2/taxonomies", "wp-json/wp/v2/settings",
    "wp-json/oembed/", "wp-json/wc/", "xmlrpc.php", "readme.html", "license.txt",
]

# =============================================================================
# DRUPAL
# =============================================================================
DRUPAL = [
    "admin/", "admin/config", "admin/structure", "admin/modules",
    "admin/appearance", "admin/people", "admin/content", "admin/reports",
    "admin/reports/status", "admin/reports/status/php", "admin/reports/dblog",
    "user/", "user/login", "user/logout", "user/register", "user/password",
    "CHANGELOG.txt", "COPYRIGHT.txt", "INSTALL.txt", "INSTALL.mysql.txt",
    "INSTALL.pgsql.txt", "INSTALL.sqlite.txt", "LICENSE.txt", "MAINTAINERS.txt",
    "README.txt", "UPGRADE.txt", "core/CHANGELOG.txt", "web.config",
    "core/", "core/misc/", "core/modules/", "core/themes/",
    "core/install.php", "core/rebuild.php", "core/authorize.php",
    "modules/", "modules/contrib/", "modules/custom/", "themes/",
    "themes/contrib/", "themes/custom/", "profiles/", "libraries/",
    "sites/", "sites/default/", "sites/default/settings.php",
    "sites/default/settings.local.php", "sites/default/default.settings.php",
    "sites/default/services.yml", "sites/default/files/", "sites/all/",
    "update.php", "install.php", "authorize.php", "cron.php", "xmlrpc.php",
    "jsonapi/", "rest/", "files/", "private/", "tmp/",
]

# =============================================================================
# JOOMLA
# =============================================================================
JOOMLA = [
    "administrator/", "administrator/index.php", "administrator/manifests/",
    "administrator/components/", "administrator/modules/",
    "administrator/templates/", "administrator/logs/", "administrator/cache/",
    "README.txt", "LICENSE.txt", "htaccess.txt", "web.config.txt", "joomla.xml",
    "configuration.php", "configuration.php-dist", "configuration.php.bak",
    "configuration.php.old", "libraries/", "components/", "modules/",
    "plugins/", "templates/", "includes/", "language/", "layouts/",
    "cli/", "api/", "cache/", "logs/", "tmp/", "media/", "images/",
    "installation/", "installation/index.php",
    "api/index.php/v1/", "api/index.php/v1/content/articles", "api/index.php/v1/users",
]

# =============================================================================
# NODE.JS / EXPRESS
# =============================================================================
NODE = [
    "package.json", "package-lock.json", "yarn.lock", "pnpm-lock.yaml",
    "node_modules/", "npm-debug.log", "yarn-error.log",
    ".npmrc", ".yarnrc", ".nvmrc", ".node-version",
    "tsconfig.json", "jsconfig.json", ".babelrc", ".babelrc.json",
    "babel.config.js", "babel.config.json", ".eslintrc", ".eslintrc.js",
    ".eslintrc.json", ".eslintignore", ".prettierrc", ".prettierrc.js",
    "prettier.config.js", "webpack.config.js", "webpack.config.ts",
    "rollup.config.js", "vite.config.js", "vite.config.ts",
    "esbuild.config.js", "turbo.json", "nx.json", "lerna.json", "rush.json",
    "server.js", "server.ts", "app.js", "app.ts", "index.js", "index.ts",
    "main.js", "main.ts", "src/", "dist/", "build/", "out/", "lib/",
    "routes/", "controllers/", "middleware/", "models/", "views/",
    "public/", "static/", "ecosystem.config.js", "pm2.config.js",
    "nodemon.json", ".pm2/", "logs/", "jest.config.js", "jest.config.ts",
    "mocha.opts", ".mocharc.js", ".mocharc.json", "karma.conf.js",
    "cypress.json", "cypress.config.js", "playwright.config.js",
    "playwright.config.ts", "coverage/", "__tests__/", "test/", "tests/", "spec/",
    ".env", ".env.local", ".env.development", ".env.production", ".env.test",
    "newrelic.js", "newrelic_agent.log", "sentry.properties",
]

# =============================================================================
# NEXT.JS
# =============================================================================
NEXTJS = [
    "next.config.js", "next.config.ts", "next.config.mjs", "next-env.d.ts",
    ".next/", "api/", "api/auth/", "api/auth/[...nextauth]", "api/health",
    "api/graphql", "_next/", "_next/static/", "_next/data/", "_next/image/",
    "404", "500", "_error", "__next_data__",
    "api/auth/session", "api/auth/signin", "api/auth/signout",
    "api/auth/callback", "api/auth/csrf", "api/auth/providers",
    "package.json", ".env.local", ".env.development", ".env.production",
    "middleware.ts", "middleware.js",
]

# =============================================================================
# ANGULAR
# =============================================================================
ANGULAR = [
    "angular.json", ".angular/", "dist/", "build/", ".angular/cache/",
    "src/", "src/app/", "src/assets/", "src/environments/",
    "src/environments/environment.ts", "src/environments/environment.prod.ts",
    "package.json", "tsconfig.json", "tsconfig.app.json", "tsconfig.spec.json",
    "karma.conf.js", "protractor.conf.js", "ngsw.json", "ngsw-worker.js",
    "manifest.webmanifest", "3rdpartylicenses.txt", "polyfills.ts",
    "main.ts", "index.html", "styles.css", "styles.scss", "e2e/", "coverage/",
]

# =============================================================================
# REACT
# =============================================================================
REACT = [
    "manifest.json", "robots.txt", "asset-manifest.json", "service-worker.js",
    "build/", "dist/", "static/", "static/js/", "static/css/", "static/media/",
    "src/", "public/", "package.json", "tsconfig.json", "jsconfig.json",
    ".env", ".env.local", ".env.development", ".env.production",
    "craco.config.js", "config-overrides.js", "setupTests.ts", "setupTests.js",
    "jest.config.js", ".storybook/", "storybook-static/",
]

# =============================================================================
# VUE.JS
# =============================================================================
VUEJS = [
    "vue.config.js", "vite.config.js", "vite.config.ts", "quasar.config.js",
    "quasar.conf.js", "dist/", ".output/", "src/", "public/",
    "package.json", "tsconfig.json", "jsconfig.json",
    ".env", ".env.local", ".env.development", ".env.production", "index.html",
    "src/store/", "src/stores/",
]

# =============================================================================
# RUBY ON RAILS
# =============================================================================
RAILS = [
    "rails/info", "rails/info/properties", "rails/info/routes", "rails/mailers",
    "rails/conductor/", "cable",
    "rails/active_storage/", "rails/active_storage/direct_uploads",
    "rails/active_storage/disk/", "rails/active_storage/blobs/",
    "rails/active_storage/representations/", "rails/action_mailbox/",
    "packs/", "packs-test/", "api/", "api/v1/", "api/v2/",
    "admin/", "admin/dashboard", "rails_admin/",
    "sidekiq/", "sidekiq/busy", "sidekiq/queues", "sidekiq/retries",
    "sidekiq/scheduled", "sidekiq/dead", "resque/", "delayed_job/",
    "good_job/", "mission_control-jobs/", "flipper/", "blazer/",
    "users/sign_in", "users/sign_out", "users/sign_up", "users/password/new",
    "users/password/edit", "users/confirmation", "users/unlock",
    "Gemfile", "Gemfile.lock", "Rakefile", "config.ru",
    "config/", "config/routes.rb", "config/database.yml", "config/secrets.yml",
    "config/master.key", "config/credentials.yml.enc", "config/application.rb",
    "config/environment.rb", "config/environments/", "config/initializers/",
    "config/locales/", "config/storage.yml", "config/cable.yml", "config/puma.rb",
    "app/", "bin/", "db/", "lib/", "log/", "public/", "storage/", "tmp/", "vendor/",
    "log/development.log", "log/production.log", "log/test.log",
    "tmp/cache/", "tmp/pids/", "tmp/sessions/", "tmp/sockets/",
]

# =============================================================================
# GO
# =============================================================================
GO = [
    "go.mod", "go.sum", "go.work", "go.work.sum", "Gopkg.toml", "Gopkg.lock",
    "glide.yaml", "glide.lock", "vendor/", "bin/", "pkg/", "main.go", "main",
    "config.yaml", "config.yml", "config.json", "config.toml", ".env",
    "health", "healthz", "readyz", "livez", "ready", "live", "metrics",
    "debug/pprof/", "debug/pprof/goroutine", "debug/pprof/heap",
    "debug/pprof/threadcreate", "debug/pprof/block", "debug/pprof/mutex",
    "debug/pprof/profile", "debug/pprof/trace", "debug/vars",
    "swagger/", "swagger/index.html", "swagger.json", "swagger.yaml",
    "docs/", "docs/doc.json", "docs/swagger.json",
]

# =============================================================================
# .NET / ASP.NET
# =============================================================================
ASPNET = [
    "web.config", "Web.config", "web.config.bak", "applicationHost.config",
    "machine.config", "Global.asax", "global.asax",
    "trace.axd", "elmah.axd", "glimpse.axd",
    "default.aspx", "Default.aspx", "index.aspx", "login.aspx", "Login.aspx",
    "admin.aspx", "Admin.aspx", "error.aspx", "Error.aspx",
    "Views/", "Controllers/", "Models/", "Content/", "Scripts/", "Areas/",
    "App_Data/", "App_Code/", "App_GlobalResources/", "App_LocalResources/",
    "App_Browsers/", "App_WebReferences/", "App_Start/",
    "bin/", "obj/", "packages/",
    "appsettings.json", "appsettings.Development.json",
    "appsettings.Production.json", "appsettings.Staging.json",
    "launchSettings.json", "bundleconfig.json", "libman.json",
    "nuget.config", "packages.config",
    "wwwroot/", "runtimeconfig.json", "deps.json", "Program.cs", "Startup.cs",
    "health", "healthz", "ready", "swagger/", "swagger/v1/swagger.json", "api-docs/",
    "Identity/", "Account/", "Account/Login", "Account/Logout",
    "Account/Register", "Account/Manage",
    "signalr/", "hubs/", "hangfire", "hangfire/",
]

# =============================================================================
# IIS
# =============================================================================
IIS = [
    "iisstart.htm", "iisstart.png", "welcome.png",
    "default.htm", "default.html", "default.asp", "default.aspx",
    "index.htm", "index.html", "index.asp", "index.aspx",
    "web.config", "applicationHost.config",
    "aspnet_client/", "scripts/", "cgi-bin/", "isapi/",
    "_vti_bin/", "_vti_inf.html", "_vti_log/", "_vti_pvt/", "_vti_txt/", "_vti_cnf/",
    "ntlm/", "auth/", "ftp/", "404.html", "500.html", "trace.axd",
]

# =============================================================================
# APACHE
# =============================================================================
APACHE = [
    "server-status", "server-info", "balancer-manager", "ldap-status",
    ".htaccess", ".htpasswd", "httpd.conf", "apache2.conf",
    "icons/", "manual/", "cgi-bin/", "cgi-bin/test-cgi",
    "cgi-bin/printenv", "cgi-sys/", "test/", "phpinfo.php",
]

# =============================================================================
# NGINX
# =============================================================================
NGINX = [
    "nginx_status", "nginx-status", "status", "stub_status", "basic_status",
    "nginx.conf", "conf/", "50x.html", "404.html", "index.html", "welcome.html",
]

# =============================================================================
# LIFERAY
# =============================================================================
LIFERAY = [
    "api/jsonws", "api/jsonws/invoke", "api/jsonws/", "api/axis/",
    "c/portal/login", "c/portal/logout", "c/portal/json_service",
    "c/portal/layout", "c/portal/update_language",
    "web/guest/home", "web/guest/", "group/control_panel",
    "group/control_panel/manage", "group/guest/",
    "image/image_gallery", "image/", "documents/", "documents/portlet_file_entry/",
    "html/themes/", "html/common/themes/", "html/taglib/", "html/js/", "html/css/",
    "tunnel-web/", "api/liferay/", "o/graphql", "o/headless-admin-user/",
    "o/headless-delivery/", "o/oauth2/", "o/oauth2/authorize", "o/oauth2/token",
]

# =============================================================================
# JENKINS
# =============================================================================
JENKINS = [
    "jenkins/", "ci/", "api/", "api/json", "api/xml", "api/python",
    "script", "scriptText", "scriptApproval/",
    "me/", "user/", "people/", "asynchPeople/", "whoAmI/",
    "job/", "jobs/", "view/", "computer/", "queue/", "builds/",
    "manage/", "configure", "configureSecurity/", "pluginManager/",
    "updateCenter/", "systemInfo", "log/", "about/",
    "cli/", "jnlpJars/", "jnlpJars/jenkins-cli.jar",
    "credentials/", "credential-store/",
    "restart", "safeRestart", "exit", "safeExit",
    "wsagents/", "tcpSlaveAgentListener/", "env-vars.html",
]

# =============================================================================
# GITLAB
# =============================================================================
GITLAB = [
    "api/v4/", "api/v4/projects", "api/v4/users", "api/v4/groups",
    "api/v4/version", "api/v3/", "api/graphql", "-/graphql-explorer",
    "admin/", "admin/application_settings", "admin/users", "admin/groups",
    "admin/projects", "admin/health_check", "admin/background_jobs",
    "admin/logs", "admin/system_info",
    "users/", "users/sign_in", "users/sign_out", "users/sign_up", "users/password/new",
    "explore/", "explore/projects", "explore/groups", "explore/snippets",
    "health", "readiness", "liveness", "-/health", "-/readiness", "-/liveness",
    "metrics", "-/metrics", "assets/", "uploads/", "help/", "help/docs",
    "oauth/", "oauth/authorize", "oauth/token", "jwt/auth",
]

# =============================================================================
# GRAFANA
# =============================================================================
GRAFANA = [
    "api/", "api/admin/", "api/admin/settings", "api/admin/stats",
    "api/admin/users", "api/datasources", "api/dashboards/", "api/org/",
    "api/orgs/", "api/users/", "api/alerts/", "api/annotations/",
    "api/search/", "api/frontend/", "api/health", "api/live/",
    "api/plugins/", "api/snapshots/", "api/teams/",
    "login", "logout", "signup", "d/", "dashboard/", "dashboards/",
    "explore/", "alerting/", "admin/", "admin/settings", "admin/users",
    "admin/orgs", "admin/ldap", "admin/plugins", "metrics", "healthz", "public/",
]

# =============================================================================
# PROMETHEUS
# =============================================================================
PROMETHEUS = [
    "graph", "status", "targets", "rules", "alerts", "config", "flags",
    "tsdb-status", "service-discovery",
    "api/v1/", "api/v1/query", "api/v1/query_range", "api/v1/series",
    "api/v1/labels", "api/v1/label/", "api/v1/targets", "api/v1/rules",
    "api/v1/alerts", "api/v1/alertmanagers", "api/v1/status/config",
    "api/v1/status/flags", "api/v1/status/runtimeinfo", "api/v1/status/buildinfo",
    "api/v1/status/tsdb", "metrics", "-/healthy", "-/ready",
]

# =============================================================================
# ELASTICSEARCH
# =============================================================================
ELASTICSEARCH = [
    "_cluster/health", "_cluster/state", "_cluster/stats", "_cluster/settings",
    "_cluster/nodes", "_cluster/allocation/explain",
    "_nodes/", "_nodes/stats", "_nodes/info", "_nodes/hot_threads",
    "_cat/", "_cat/indices", "_cat/nodes", "_cat/health", "_cat/master",
    "_cat/shards", "_cat/allocation", "_cat/plugins",
    "_search", "_msearch", "_count", "_analyze",
    "_mapping", "_settings", "_aliases", "_alias", "_template",
    "_index_template", "_component_template",
    "_security/", "_security/user", "_security/role", "_security/api_key",
    "_xpack/", "_xpack/security/", "_xpack/license", "_xpack/watcher/", "_xpack/ml/",
    "_snapshot/", "_plugins/",
    "kibana/", "app/kibana", "app/discover", "app/visualize", "app/dashboard",
    "app/dev_tools", "app/management", "status", "api/status",
    "api/kibana/settings", "bundles/",
]

# =============================================================================
# VAULT
# =============================================================================
VAULT = [
    "v1/", "v1/sys/health", "v1/sys/seal-status", "v1/sys/init",
    "v1/sys/config/state/sanitized", "v1/sys/host-info", "v1/sys/leader",
    "v1/sys/mounts", "v1/sys/auth", "v1/sys/policies/", "v1/sys/audit",
    "v1/sys/internal/counters/", "v1/sys/internal/ui/mounts",
    "ui/", "ui/vault/auth", "ui/vault/secrets", "ui/vault/policies",
    "v1/sys/metrics",
]

# =============================================================================
# CONSUL
# =============================================================================
CONSUL = [
    "ui/", "v1/", "v1/agent/members", "v1/agent/self", "v1/agent/checks",
    "v1/agent/services", "v1/catalog/nodes", "v1/catalog/services",
    "v1/catalog/datacenters", "v1/health/node/", "v1/health/service/",
    "v1/kv/", "v1/status/leader", "v1/status/peers", "v1/acl/tokens",
    "v1/agent/metrics",
]

# =============================================================================
# AIRFLOW
# =============================================================================
AIRFLOW = [
    "admin/", "home", "dags/", "dagrun/", "task/", "taskinstance/",
    "log/", "variable/", "connection/", "pool/", "xcom/",
    "configuration/", "version/",
    "api/v1/", "api/v1/dags", "api/v1/dagRuns", "api/v1/tasks",
    "api/v1/config", "api/v1/connections", "api/v1/pools",
    "api/v1/variables", "api/v1/health", "api/v1/version",
    "flower/", "health", "healthz",
]

# =============================================================================
# JUPYTER
# =============================================================================
JUPYTER = [
    "notebooks/", "tree/", "terminals/", "files/", "view/", "edit/",
    "api/", "api/contents/", "api/sessions/", "api/kernels/",
    "api/kernelspecs/", "api/terminals/", "api/config/", "api/status",
    "hub/", "hub/login", "hub/logout", "hub/token", "hub/api/", "hub/admin",
    "lab/", "lab/api/",
]

# =============================================================================
# SWAGGER / OPENAPI COMMON
# =============================================================================
SWAGGER_COMMON = [
    "swagger/", "swagger-ui/", "swagger-ui.html", "swagger/index.html",
    "swagger/ui/", "swagger/ui/index.html", "api/swagger/", "api/swagger-ui/",
    "api/swagger.json", "api/swagger.yaml", "api/swagger/v1/swagger.json",
    "api/swagger/v2/swagger.json", "swagger-resources/",
    "swagger-resources/configuration/ui", "swagger-resources/configuration/security",
    "openapi/", "openapi.json", "openapi.yaml", "openapi.yml",
    "openapi/v1/openapi.json", "openapi/v2/openapi.json", "openapi/v3/openapi.json",
    "api/openapi.json", "api/openapi.yaml",
    "v1/api-docs", "v1/swagger.json", "v2/api-docs", "v2/swagger.json",
    "v3/api-docs", "v3/swagger.json", "api/v1/docs", "api/v1/swagger",
    "api/v2/docs", "api/v2/swagger", "api/v3/docs", "api/v3/swagger",
    "redoc", "redoc/", "api/redoc", "rapidoc", "rapidoc/", "api/rapidoc",
    "elements/", "api/elements",
    "graphql", "graphiql", "playground", "altair", "voyager",
]

# =============================================================================
# MAP TECHNOLOGY TAGS TO WORDLISTS
# =============================================================================
WORDLISTS = {
    "common": COMMON,
    "cloud": CLOUD_DEVOPS,
    "devops": CLOUD_DEVOPS,
    "aws": CLOUD_DEVOPS,
    "azure": CLOUD_DEVOPS,
    "gcp": CLOUD_DEVOPS,
    "docker": CLOUD_DEVOPS,
    "kubernetes": CLOUD_DEVOPS,
    "k8s": CLOUD_DEVOPS,
    "spring": SPRING,
    "springboot": SPRING,
    "java": JAVA + SPRING,
    "tomcat": TOMCAT + JAVA,
    "jboss": JBOSS + JAVA,
    "wildfly": JBOSS + JAVA,
    "weblogic": WEBLOGIC + JAVA,
    "django": DJANGO,
    "flask": FLASK,
    "fastapi": FASTAPI,
    "python": DJANGO + FLASK + FASTAPI,
    "php": PHP,
    "laravel": LARAVEL + PHP,
    "symfony": SYMFONY + PHP,
    "wordpress": WORDPRESS + PHP,
    "drupal": DRUPAL + PHP,
    "joomla": JOOMLA + PHP,
    "node": NODE,
    "nodejs": NODE,
    "express": NODE,
    "nextjs": NEXTJS + NODE,
    "next": NEXTJS + NODE,
    "angular": ANGULAR + NODE,
    "react": REACT + NODE,
    "vue": VUEJS + NODE,
    "vuejs": VUEJS + NODE,
    "rails": RAILS,
    "ruby": RAILS,
    "go": GO,
    "golang": GO,
    "asp": ASPNET,
    "aspnet": ASPNET,
    "dotnet": ASPNET,
    "iis": IIS + ASPNET,
    "apache": APACHE,
    "nginx": NGINX,
    "liferay": LIFERAY + JAVA,
    "jenkins": JENKINS,
    "gitlab": GITLAB,
    "grafana": GRAFANA,
    "prometheus": PROMETHEUS,
    "elasticsearch": ELASTICSEARCH,
    "elastic": ELASTICSEARCH,
    "kibana": ELASTICSEARCH,
    "vault": VAULT,
    "consul": CONSUL,
    "airflow": AIRFLOW,
    "jupyter": JUPYTER,
    "swagger": SWAGGER_COMMON,
    "openapi": SWAGGER_COMMON,
}

# =============================================================================
# COMBINED WORDLIST FOR "ALL" MODE
# =============================================================================
def get_all_payloads():
    """Return all unique payloads combined."""
    all_payloads = set()
    all_payloads.update(COMMON)
    all_payloads.update(CLOUD_DEVOPS)
    all_payloads.update(SPRING)
    all_payloads.update(JAVA)
    all_payloads.update(TOMCAT)
    all_payloads.update(JBOSS)
    all_payloads.update(WEBLOGIC)
    all_payloads.update(DJANGO)
    all_payloads.update(FLASK)
    all_payloads.update(FASTAPI)
    all_payloads.update(PHP)
    all_payloads.update(LARAVEL)
    all_payloads.update(SYMFONY)
    all_payloads.update(WORDPRESS)
    all_payloads.update(DRUPAL)
    all_payloads.update(JOOMLA)
    all_payloads.update(NODE)
    all_payloads.update(NEXTJS)
    all_payloads.update(ANGULAR)
    all_payloads.update(REACT)
    all_payloads.update(VUEJS)
    all_payloads.update(RAILS)
    all_payloads.update(GO)
    all_payloads.update(ASPNET)
    all_payloads.update(IIS)
    all_payloads.update(APACHE)
    all_payloads.update(NGINX)
    all_payloads.update(LIFERAY)
    all_payloads.update(JENKINS)
    all_payloads.update(GITLAB)
    all_payloads.update(GRAFANA)
    all_payloads.update(PROMETHEUS)
    all_payloads.update(ELASTICSEARCH)
    all_payloads.update(VAULT)
    all_payloads.update(CONSUL)
    all_payloads.update(AIRFLOW)
    all_payloads.update(JUPYTER)
    all_payloads.update(SWAGGER_COMMON)
    return sorted(list(all_payloads))


def get_stats():
    """Print wordlist statistics."""
    all_payloads = get_all_payloads()
    print(f"Total unique payloads: {len(all_payloads)}")
    print(f"Technology categories: {len(WORDLISTS)}")
    print("\nPayloads per category:")
    for name in sorted(WORDLISTS.keys()):
        lst = WORDLISTS[name]
        if isinstance(lst, list):
            print(f"  {name}: {len(lst)}")


if __name__ == "__main__":
    get_stats()
