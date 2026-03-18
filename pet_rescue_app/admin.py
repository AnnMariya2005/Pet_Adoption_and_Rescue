from django.contrib import admin
from django.utils.html import format_html
from .models import PetReport, Notification

# ===== CUSTOMIZE ADMIN SITE BRANDING =====
admin.site.site_header  = "PetRescue Pro — Admin Portal"
admin.site.site_title   = "PetRescue Admin"
admin.site.index_title  = "Management Dashboard"


@admin.register(PetReport)
class PetReportAdmin(admin.ModelAdmin):

    list_display = (
        'pet_name', 'user', 'pet_image_preview', 'pet_type', 'breed', 'color',
        'report_type_badge', 'status_badge', 'status',
        'location', 'phone_number',
        'created_at',
    )

    list_filter  = ('status', 'report_type', 'pet_type', 'user', 'created_at')
    search_fields = ('pet_name', 'breed', 'location', 'color', 'user__username', 'phone_number')
    ordering = ('-created_at',)
    readonly_fields = ('user', 'created_at', 'updated_at')
    list_editable = ('status',)
    list_per_page = 25

    fieldsets = (
        ('Pet Details', {
            'fields': ('pet_name', 'pet_image', 'pet_type', 'breed', 'color', 'description')
        }),
        ('Report Info', {
            'fields': ('report_type', 'status', 'location', 'phone_number')
        }),
        ('System Information', {
            'fields': ('user', 'created_at', 'updated_at'),
        }),
    )

    def pet_image_preview(self, obj):
        if obj.pet_image:
            return format_html('<img src="{}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 5px;" />', obj.pet_image.url)
        return "No Image"
    pet_image_preview.short_description = 'Photo'

    def report_type_badge(self, obj):
        color = '#ef4444' if obj.report_type == 'Lost' else '#10b981'
        return format_html(
            '<span style="background:{};color:#fff;padding:3px 10px;'
            'border-radius:12px;font-size:11px;font-weight:700;">{}</span>',
            color, obj.report_type
        )
    report_type_badge.short_description = 'Type'

    def status_badge(self, obj):
        colors = {
            'Pending':  '#f59e0b',
            'Accepted': '#10b981',
            'Rejected': '#ef4444',
            'Closed':   '#6b7280',
        }
        color = colors.get(obj.status, '#6b7280')
        return format_html(
            '<span style="background:{};color:#fff;padding:3px 10px;'
            'border-radius:12px;font-size:11px;font-weight:700;">{}</span>',
            color, obj.status
        )
    status_badge.short_description = 'Status'

    def save_model(self, request, obj, form, change):
        if change:
            try:
                old_report = PetReport.objects.get(pk=obj.pk)
                if old_report.status != obj.status:
                    Notification.objects.create(
                        user=obj.user,
                        message=f"Your report '{obj.pet_name or 'unnamed pet'}' status changed to {obj.status}."
                    )
            except PetReport.DoesNotExist:
                pass
        super().save_model(request, obj, form, change)

    def save_changelist_model(self, request, obj, form, change):
        # Handle list_editable updates specially for pet notifications
        if change and 'status' in form.changed_data:
            Notification.objects.create(
                user=obj.user,
                message=f"Your report '{obj.pet_name or 'unnamed pet'}' status changed to {obj.status}."
            )
        super().save_changelist_model(request, obj, form, change)


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):

    list_display  = ('user', 'short_message', 'is_read', 'created_at')
    list_filter   = ('is_read', 'created_at')
    search_fields = ('message', 'user__username')
    ordering      = ('-created_at',)
    readonly_fields = ('user', 'message', 'created_at')
    list_per_page = 30

    def short_message(self, obj):
        return obj.message[:80] + '...' if len(obj.message) > 80 else obj.message
    short_message.short_description = 'Message'