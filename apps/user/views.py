import re
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
import random
import string
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
        user = request.user
        button_codes = []
        
        # 如果是超级管理员，遍历所有 Permission 的 button_codes
        if user.is_superuser:
            permissions = Permission.objects.all()
            for perm in permissions:
                if perm.button_codes:  # 确保 button_codes 不为空
                    # 从每个对象中提取 component 字段
                    for item in perm.button_codes:
                        if isinstance(item, dict) and 'component' in item:
                            button_codes.append(item['component'])
            # 去重并保持顺序
            button_codes = list(dict.fromkeys(button_codes))
        else:
            # 普通用户，从用户表读取 button_codes
            if user.is_authenticated:
                if user.button_codes:
                    # 从每个对象中提取 component 字段
                    for item in user.button_codes:
                        if isinstance(item, dict) and 'component' in item:
                            button_codes.append(item['component'])
            else:
                button_codes = []
        
        resp = {
            "code": 0,
            "data": button_codes,
            "error": "null",
            "message": "ok",
        }
        
        return Response(data=resp, status=status.HTTP_200_OK)

# class UserCodesView(APIView):
#     def get(self, request):
#         resp = {
#             "code": 0,
#             "data": ["AC_100100", "AC_100110", "AC_100120", "AC_100010","sys:Menu:Create"],
#             "error": "null",
#             "message": "ok",
#         }

#         return Response(data=resp, status=status.HTTP_200_OK)


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
        # 辅助函数：将 path 转换为 name（去掉开头的 /）
        # def path_to_name(path):
        #     if not path:
        #         return ""  # 如果 path 为空，返回空字符串
        #     return path.lstrip("/")  # 去掉开头的 /
        user = request.user
        menu_data = []  # 最终存储菜单数据
        menu_dict = {}  # 用于存储不同菜单，key 为 menu.id

        # 如果是超级用户，返回所有菜单和所属权限
        if user.is_superuser:
            menus = Menu.objects.all()
            # 遍历所有菜单，获取每个菜单下的所有权限
            for menu in menus:
                menu_id = menu.id
                # 获取该菜单下的所有权限
                menu_permissions = menu.permissions.all()
                # while True:
                #     random_suffix = generate_random_suffix()
                #     menu_path = f"/{random_suffix}"
                #     if menu_path not in used_paths:
                #         used_paths.add(menu_path)
                #         break
                menu_dict[menu_id] = {
                    "meta": {
                        "icon": menu.icon if menu.icon else "",
                        "order": str(menu.sort) if menu.sort else "-1",
                        "title": menu.title,
                    },
                    "id": menu.id,
                    "name": menu.title,
                    "path": menu.id,
                    "redirect": "/test",
                    "children": [],  # 存储子权限
                }
                
                # 添加该菜单下的所有权限
                for perm in menu_permissions:
                    menu_dict[menu_id]["children"].append(
                        {
                            "name": perm.id,
                            #"name": path_to_name(perm.path),
                            "path": perm.path if perm.path else "",
                            "component": perm.component if perm.component else "",
                            "meta": {
                                "icon": perm.icon if perm.icon else "",
                                "title": perm.title,
                            },
                        }
                    )
        else:
            # 非超级用户：根据角色权限和额外权限获取菜单
            if user.is_authenticated and user.roles:
                role_permissions = user.roles.permissions.all()
            else:
                role_permissions = Permission.objects.none()
            
            if user.is_authenticated:
                extra_permissions = user.extra_permissions.all()
            else:
                extra_permissions = Permission.objects.none()
            
            all_permissions = (role_permissions | extra_permissions).distinct()
            
            # 遍历权限，构建菜单结构
            for perm in all_permissions:
                # 检查权限是否关联了菜单
                if perm.menu is None:
                    continue  # 跳过没有关联菜单的权限
                
                menu_id = perm.menu.id
                if menu_id not in menu_dict:
                    menu_dict[menu_id] = {
                        "meta": {
                            "icon": perm.menu.icon if perm.menu.icon else "",
                            "order": str(perm.menu.sort) if perm.menu.sort else "-1",
                            "title": perm.menu.title,
                        },
                        "name": perm.menu.title,
                        "path": perm.menu.path if perm.menu.path else "/",
                        "redirect": "/test",
                        "children": [],
                    }
                menu_dict[menu_id]["children"].append(
                    {
                        "name": perm.title,
                        "path": perm.path if perm.path else "",
                        "component": perm.component if perm.component else "",
                        "meta": {
                            "icon": perm.icon if perm.icon else "",
                            "title": perm.title,
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


class testView(APIView):
    def get(self, request):
        return Response(
            {"code": 0, "data": "test", "error": "null", "message": "ok"},
            status=status.HTTP_200_OK,
        )
