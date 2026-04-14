from __future__ import annotations

from setup.modules.admin_panel import AdminPanelModule
from setup.modules.api_mode import APIModeModule
from setup.modules.authentication import AuthenticationModule
from setup.modules.cicd import CICDModule
from setup.modules.cors import CORSModule
from setup.modules.database import DatabaseModule
from setup.modules.docker import DockerModule
from setup.modules.email_support import EmailSupportModule
from setup.modules.project_name import ProjectNameModule
from setup.modules.rate_limiting import RateLimitingModule
from setup.modules.security_headers import SecurityHeadersModule
from setup.modules.sentry import SentryModule
from setup.modules.testing import TestingModule

# Ordered: project → database → features → devops → testing
MODULES = [
    ProjectNameModule(),
    DatabaseModule(),
    AuthenticationModule(),
    AdminPanelModule(),
    EmailSupportModule(),
    RateLimitingModule(),
    CORSModule(),
    APIModeModule(),
    SecurityHeadersModule(),
    SentryModule(),
    DockerModule(),
    CICDModule(),
    TestingModule(),
]
