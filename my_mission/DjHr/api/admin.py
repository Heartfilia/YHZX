from django.contrib import admin
from .models import *


class InfoAdmin(admin.ModelAdmin):
    list_display = ('info', 'isRemind', 'lateRemind')
    list_editable = ('isRemind', 'lateRemind')
    list_filter = ('isRemind', 'platform')
    list_per_page = 20
    fieldsets = (
        ('基本选项', {
            'fields': ('info', 'isRemind', 'lateRemind')
        }),
        ('高级选项', {
            'fields': ('account', 'platform'),
            'classes': ('collapse',)
        })
    )


# Register your models here.
admin.site.register(Info, InfoAdmin)
admin.site.site_title = "银河在线Hr后台管理系统"
admin.site.site_header = "银河在线Hr后台管理系统"