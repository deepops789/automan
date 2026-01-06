from django.db import models
from django.contrib.auth.models import AbstractUser


# Create your models here.
class Profile(AbstractUser):
    last_login_ip = models.GenericIPAddressField(blank=True, null=True)
    wechat = models.CharField(max_length=32, blank=True, null=True)
    image = models.ImageField(
        upload_to="static/%Y/%m",
        default="image/default.png",
        max_length=100,
        null=True,
        blank=True,
    )
    department = models.ForeignKey(
        "Organization",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name="部门",
    )
    position = models.CharField(
        max_length=50, null=True, blank=True, verbose_name="职位"
    )
    superior = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name="上级主管",
    )
    roles = models.ForeignKey(
        "Role", on_delete=models.SET_NULL, null=True, verbose_name="角色", blank=True
    )
    extra_permissions = models.ManyToManyField(
        "Permission", blank=True, related_name="extra_users"
    )
    
    button_codes = models.JSONField(default=list, blank=True, verbose_name="按钮权限")
    # def __str__(self):
    #     return self.name
    class Meta:
        db_table = "user"
        verbose_name = "Userinfo"
        verbose_name_plural = verbose_name


class Organization(models.Model):
    """
    组织架构
    """

    organization_type_choices = (("company", "公司"), ("department", "部门"))
    name = models.CharField(max_length=60, verbose_name="名称")
    type = models.CharField(
        max_length=20,
        choices=organization_type_choices,
        default="company",
        verbose_name="类型",
    )
    pid = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name="父类组织",
    )

    class Meta:
        verbose_name = "zzjg"
        verbose_name_plural = verbose_name


class Role(models.Model):
    """
    角色
    """

    name = models.CharField(max_length=32, unique=True, verbose_name="角色")
    permissions = models.ManyToManyField("Permission", blank=True, verbose_name="权限")
    desc = models.CharField(max_length=50, blank=True, null=True, verbose_name="描述")
    button_codes = models.JSONField(default=list, blank=True)
    class Meta:
        verbose_name = "角色"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class Menu(models.Model):
    """
    菜单
    """

    title = models.CharField(max_length=30, unique=True, verbose_name="菜单名")
    icon = models.CharField(max_length=50, null=True, blank=True, verbose_name="图标")
    path = models.CharField(
        max_length=158, null=True, blank=True, verbose_name="链接地址"
    )
    is_frame = models.BooleanField(default=False, verbose_name="外部菜单")
    is_show = models.BooleanField(default=True, verbose_name="显示标记")
    sort = models.IntegerField(null=True, blank=True, verbose_name="排序标记")
    pid = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.SET_NULL, verbose_name="父菜单"
    )

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "菜单"
        verbose_name_plural = verbose_name
        ordering = ["id"]


class Permission(models.Model):
    """
    权限
    """

    title = models.CharField(max_length=30, unique=True, verbose_name="权限名")
    menu = models.ForeignKey(
        "Menu", null=True, blank=True, verbose_name="所属菜单", on_delete=models.RESTRICT,related_name="permissions"
    )
    path = models.CharField(
        max_length=32, unique=True, null=True, blank=True, verbose_name="API Path"
    )
    component = models.CharField(
        max_length=64, null=True, blank=True, verbose_name="组件"
    )
    method = models.CharField(max_length=64, null=True, blank=True, verbose_name="方法")
    pid = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.SET_NULL, verbose_name="父权限"
    )
    button_codes = models.JSONField(default=list, blank=True)  # 按钮权限（JSON 存储）
    icon = models.CharField(max_length=50, null=True, blank=True, verbose_name="图标")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "权限"
        verbose_name_plural = verbose_name
        ordering = ["id"]
