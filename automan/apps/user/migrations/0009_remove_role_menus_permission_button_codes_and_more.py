# Generated by Django 4.2 on 2025-03-15 17:09

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0008_menu_pid_profile_image'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='role',
            name='menus',
        ),
        migrations.AddField(
            model_name='permission',
            name='button_codes',
            field=models.JSONField(blank=True, default=list),
        ),
        migrations.AddField(
            model_name='profile',
            name='department',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='user.organization', verbose_name='部门'),
        ),
        migrations.AddField(
            model_name='profile',
            name='position',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='职位'),
        ),
        migrations.AddField(
            model_name='profile',
            name='superior',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='上级主管'),
        ),
        migrations.RemoveField(
            model_name='profile',
            name='roles',
        ),
        migrations.AddField(
            model_name='profile',
            name='roles',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='user.role', verbose_name='角色'),
        ),
    ]
