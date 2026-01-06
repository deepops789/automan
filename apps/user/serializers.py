from django.contrib.auth.models import User, Group  # 导入model中的数据库模块
from rest_framework import serializers  # 导入序列化器
from .models import Menu, Permission, Role, Profile

class MenuSerializer(serializers.ModelSerializer):
    meta = serializers.SerializerMethodField()
    children = serializers.SerializerMethodField()

    class Meta:
        model = Menu
        fields = ["id", "title", "path", "meta", "children"]

    def get_meta(self, obj):
        """返回 `meta` 字段"""
        return {
            "icon": obj.icon if obj.icon else "ic:baseline-view-in-ar",
            "order": obj.sort if obj.sort is not None else 0,
            "title": f"page.{obj.title.replace(' ', '_').lower()}.title",
        }

    def get_children(self, obj):
        """递归获取子菜单"""
        children = Menu.objects.filter(pid=obj).order_by("sort")
        return MenuSerializer(children, many=True).data


class PermissionSerializer(serializers.ModelSerializer):
    """权限序列化（包含 `component`）"""

    # menu = MenuSerializer()

    class Meta:
        model = Permission
        fields = "__all__"


class MenuSerializer1(serializers.ModelSerializer):
    """
    菜单序列化
    """

    class Meta:
        model = Menu
        fields = "__all__"  # 包含模型中的所有字段
        # extra_kwargs = {'name': {'required': True, 'error_messages': {'required': '必须填写菜单名'}}}


class RoleListSerializer(serializers.ModelSerializer):
    """
    角色序列化
    """

    class Meta:
        model = Role
        fields = "__all__"
        # depth = 1


class RoleModifySerializer(serializers.ModelSerializer):
    class Meta:
        model = Role


class PermissionListSerializer(serializers.ModelSerializer):
    """
    权限列表序列化
    """

    # menuname = serializers.ReadOnlyField(source='menus.title')

    class Meta:
        model = Permission
        fields = "__all__"


class UserListSerializer(serializers.ModelSerializer):
    """
    用户列表的序列化
    """

    # roles = serializers.SerializerMethodField()

    # def get_roles(self, obj):
    #    return obj.roles.values()

    class Meta:
        model = Profile
        fields = "__all__"
        # fields = ['id', 'username', 'name', 'mobile', 'email', 'image', 'department', 'position', 'superior',
        #          'is_active','roles']
        # depth = 1
