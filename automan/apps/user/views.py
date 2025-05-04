from django.shortcuts import render
from rest_framework import viewsets
from django.contrib.auth import get_user_model, authenticate
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from .serializers import UserListSerializer, MenuSerializer, PermissionSerializer
from django.shortcuts import HttpResponse
from django.utils.timezone import localtime, now
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Menu, Permission

User = get_user_model()


class UserAuthView(APIView):
    """
    用户认证获取Token
    """

    def get(self, request):
        # request.user.id if request.user.is_authenticated else None

        users = User.objects.all()
        serializer = UserListSerializer(users, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        username = request.data.get("username")
        password = request.data.get("password")
        user = authenticate(username=username, password=password)

        if user is not None:
            if user.is_active:
                user.last_login = now()  # 更新最后登录时间
                user.last_login_ip = self.get_client_ip(request)  # 更新登录 IP
                user.save(
                    update_fields=["last_login", "last_login_ip"]
                )  # 只更新这两个字段，提高性能
                refresh = RefreshToken.for_user(user)
                response = {
                    "code": 0,
                    "data": {
                        "id": user.id,
                        "username": user.username,
                        "accessToken": str(refresh.access_token),
                    },
                    "error": None,
                    "message": "ok",
                }
                return Response(data=response, status=status.HTTP_200_OK)
            else:
                return Response(
                    {
                        "code": 1,
                        "message": "用户被禁用",
                        "data": {},
                        "error": "用户被禁用",
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )
        else:
            return Response(
                {
                    "code": 1,
                    "message": "用户或密码错误",
                    "data": {},
                    "error": "用户或密码错误",
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )

    def get_client_ip(self, request):
        """
        获取客户端的 IP 地址
        """
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]  # 取第一个 IP
        else:
            ip = request.META.get("REMOTE_ADDR")  # 直接获取 IP
        return ip


class UserInfoView(APIView):

    def get(self, request):
        user_id = request.user.id if request.user.is_authenticated else None
        response = {
            "code": 0,
            "data": {
                "id": 0,
                "realName": "Admin1",
                "Email": "admin@qq.com",
                "homePath": "/test",
                "roles": ["super"],
            },
            "error": "",
            "message": "ok",
        }
        # return Response('200')
        return Response(data=response, status=status.HTTP_200_OK)


class UserCodesView(APIView):
    def get(self, request):
        resp = {
            "code": 0,
            "data": ["AC_100100", "AC_100110", "AC_100120", "AC_100010"],
            "error": "null",
            "message": "ok",
        }

        return Response(data=resp, status=status.HTTP_200_OK)


class LogoutView(APIView):
    def get(self, request):
        # print(request.headers)
        # print(request.data)
        return Response(
            data={"code": 0, "data": {}, "error": None, "message": "ok"},
            status=status.HTTP_200_OK,
        )

    def post(self, request):
        print(request.data)
        try:
            refresh_token = request.data.get(
                "accessToken"
            )  # 获取前端传来的 refresh_token
            token = RefreshToken(refresh_token)
            token.blacklist()  # 把 refresh_token 加入黑名单
            return Response(
                {"message": "注销成功"}, status=status.HTTP_205_RESET_CONTENT
            )
        except Exception as e:
            return Response({"error": "注销失败"}, status=status.HTTP_400_BAD_REQUEST)


class PermView(APIView):
    permission_classes = [AllowAny]
    """
    根据用户角色权限 & 额外权限获取菜单
    """

    def get(self, request):
        # 定义响应数据结构
        user = request.user
        # print(user.roles)
        if user.is_superuser:
            role_permissions = Permission.objects.all()
        elif user.roles:
            role_permissions = user.roles.permissions.all()
        else:
            role_permissions = Permission.objects.none()
        extra_permissions = user.extra_permissions.all()
        all_permissions = (role_permissions | extra_permissions).distinct()
        permissions = all_permissions.distinct()
        menu_data = []  # 最终存储菜单数据
        menu_dict = {}  # 用于存储不同菜单，key 为 menu.id
        for perm in permissions:
            menu_id = perm.menu.id  # 以 menu.id 作为唯一标识
            if menu_id not in menu_dict:
                menu_dict[menu_id] = {
                    "meta": {
                        # "icon": perm.menu.icon,  # 菜单图标
                        "order": "-1",
                        "title": perm.menu.title,  # 以菜单名称作为标题
                    },
                    "name": perm.menu.title,  # 菜单名称
                    "path": (
                        perm.menu.path if perm.menu.path else "/"
                    ),  # 菜单路径，默认为 "/"
                    "redirect": "/test",
                    "children": [],  # 存储子权限
                }
            menu_dict[menu_id]["children"].append(
                {
                    "name": perm.name,
                    "path": perm.path,
                    "component": perm.component,
                    "meta": {
                        "icon": perm.icon,
                        "title": perm.name,
                    },
                }
            )
        # 转换为列表格式，便于前端处理
        menu_data = list(menu_dict.values())
        print(menu_data)
        return Response(
            {"code": 0, "data": menu_data, "error": "null", "message": "ok"},
            status=status.HTTP_200_OK,
        )

        # # 返回响应
        # return Response(data=resp, status=status.HTTP_200_OK)
