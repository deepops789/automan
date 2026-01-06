from user.models import Menu, Permission
from rest_framework import serializers


class PermissionSerializer(serializers.ModelSerializer):
    permissions = serializers.SerializerMethodField()
    class Meta:
        model = Permission
        fields = ['id', 'title', 'icon','path', 'component', 'method', 'permissions','menu','button_codes']
    def get_permissions(self, obj):
        # button_codes 字段是原始存储，直接返回即可
        return obj.button_codes


class MenuSerializer(serializers.ModelSerializer):
    permissions = PermissionSerializer(many=True, read_only=True)  # 默认 related_name

    class Meta:
        model = Menu
        fields = ['id', 'title', 'icon', 'path', 'is_frame', 'is_show', 'sort', 'permissions']

# class PermissionSerializer(serializers.ModelSerializer):
#     menu_id = serializers.IntegerField(source='menu.id', read_only=True)  # 指定变量名为 menu_id 可以改成parentid 搭配vxe table另一个树形层级模式使用

#     class Meta:
#         model = Permission
#         fields = ['id', 'title', 'icon', 'path', 'component', 'method', 'button_codes', 'menu_id']  # 添加 menu_id 到字段列表中