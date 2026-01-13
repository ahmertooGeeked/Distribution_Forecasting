from django.contrib import admin

from .models import SalesItem, SalesOrder


class SalesItemInline(admin.TabularInline):
    model = SalesItem
    extra = 0


class SalesOrderAdmin(admin.ModelAdmin):
    list_display = ("id", "customer", "date", "status", "total_amount")
    list_filter = ("status", "date")
    search_fields = ("customer__name",)
    inlines = [SalesItemInline]


admin.site.register(SalesOrder, SalesOrderAdmin)
admin.site.register(SalesItem)
