from django.apps import AppConfig


class AppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app'
    verbose_name = '应用管理'

    def ready(self):
        from django.contrib.auth.signals import user_logged_in, user_login_failed
        from middleware.audit_middleware import get_client_ip

        def _on_login_success(sender, request, user, **kwargs):
            from app.model.auth.auth_model import LoginLog
            LoginLog.objects.create(
                username=getattr(user, 'username', ''),
                ip=get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', '')[:512],
                success=True,
            )

        def _on_login_failed(sender, credentials, request, **kwargs):
            from app.model.auth.auth_model import LoginLog
            if request is None:
                return
            LoginLog.objects.create(
                username=credentials.get('username', ''),
                ip=get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', '')[:512],
                success=False,
                reason='密码错误',
            )

        user_logged_in.connect(_on_login_success, dispatch_uid='login_log_success')
        user_login_failed.connect(_on_login_failed, dispatch_uid='login_log_failed')
