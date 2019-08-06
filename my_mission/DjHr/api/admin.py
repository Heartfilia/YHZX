from django.contrib import admin
from .models import *


class InfoAdmin(admin.ModelAdmin):
    list_display = ('info', 'isRemind', 'lateRemind')
    list_editable = ('isRemind', 'lateRemind')
    list_filter = ('isRemind',)


# Register your models here.
admin.site.register(Info, InfoAdmin)