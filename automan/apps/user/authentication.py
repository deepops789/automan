from rest_framework_simplejwt.authentication import JWTAuthentication

class CustomJWTAuthentication(JWTAuthentication):
    """
    自定义 JWT 认证类，允许白名单 URL 免认证
    """
    WHITE_LISTED_URLS = [
        "/user/auth/",
        "/api/token/refresh/",
        "/api/public/",
    ]

    def authenticate(self, request):
        print(f"🔍 Checking authentication for: {request.path}")  # 调试输出

        # 确保路径匹配白名单
        if any(request.path.startswith(url) for url in self.WHITE_LISTED_URLS):
            print(f"✅ {request.path} 在白名单内，跳过 JWT 认证")
            return None  # 跳过认证，允许访问

        return super().authenticate(request)
