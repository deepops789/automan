from rest_framework.permissions import BasePermission

class AllowWhiteListed(BasePermission):
    """
    允许白名单 API 免认证，其他 API 需要 JWT
    """
    WHITE_LISTED_URLS = [
        "/user/auth/",
        "/api/token/refresh/",
        "/api/public/",
        "/user/logout",
    ]

    def has_permission(self, request, view):
        if any(request.path.startswith(url) for url in self.WHITE_LISTED_URLS):
            return True  # 允许匿名访问

        return request.user and request.user.is_authenticated
