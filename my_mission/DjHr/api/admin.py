from django.contrib import admin
from .models import *


class InfoAdmin(admin.ModelAdmin):
    list_display = ('info', 'isRemind', 'lateRemind', 'lastFresh')
    list_editable = ('isRemind', 'lateRemind')
    list_filter = ('isRemind', 'platform', 'account')
    list_per_page = 20
    fieldsets = (
        ('基本选项', {
            'fields': ('info', 'isRemind', 'lateRemind')
        }),
        ('高级选项', {
            'fields': ('account', 'platform', 'lastFresh'),
            'classes': ('collapse',)
        })
    )

class RateAdmin(admin.ModelAdmin):
    list_display = ('keyword', 'pageinfo', 'posi_nums')
    list_filter = ('plateform',)


# Register your models here.
admin.site.register(Info, InfoAdmin)
admin.site.register(Rate, RateAdmin)
admin.site.site_title = "银河在线Hr后台管理系统"
admin.site.site_header = "银河在线Hr后台管理系统"