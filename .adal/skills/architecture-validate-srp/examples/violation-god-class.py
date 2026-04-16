"""
Example 2: God Class Violations
Classes with too many dependencies and low cohesion
"""

# ❌ VIOLATION: God Class (8+ constructor parameters)
class UserService:
    """Violates SRP - serves too many actors"""
    def __init__(
        self,
        db_conn,            # Actor: DBA
        cache,              # Actor: Infrastructure
        logger,             # Actor: Monitoring
        email_service,      # Actor: Communication
        auth_service,       # Actor: Security
        notification_service,  # Actor: Communication
        analytics,          # Actor: Analytics
        config,             # Actor: Configuration
        metrics             # Actor: Monitoring
    ):
        # Too many dependencies → doing too much
        self.db = db_conn
        self.cache = cache
        self.logger = logger
        self.email = email_service
        self.auth = auth_service
        self.notifications = notification_service
        self.analytics = analytics
        self.config = config
        self.metrics = metrics


# ✅ FIX: Split by responsibility
class UserAuthService:
    """Actor: Security team"""
    def __init__(self, auth_service, logger):
        self.auth = auth_service
        self.logger = logger

    def login(self, credentials):
        pass

    def logout(self, user):
        pass


class UserNotificationService:
    """Actor: Communication team"""
    def __init__(self, email_service, notification_service):
        self.email = email_service
        self.notifications = notification_service

    def send_welcome_email(self, user):
        pass

    def send_notification(self, user, message):
        pass


class UserAnalytics:
    """Actor: Analytics team"""
    def __init__(self, analytics, metrics):
        self.analytics = analytics
        self.metrics = metrics

    def track_login(self, user):
        pass

    def record_metrics(self, event):
        pass
