from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Task


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """Admin interface for CustomUser."""
    fieldsets = UserAdmin.fieldsets + (
        ('Phone Information', {'fields': ('phone_number',)}),
    )
    list_display = ('username', 'phone_number', 'email', 'first_name', 'last_name', 'is_active')
    search_fields = ('username', 'phone_number', 'email')


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    """Admin interface for Task."""
    list_display = ('title', 'user', 'due_date', 'is_completed', 'created_at')
    list_filter = ('is_completed', 'due_date', 'created_at')
    search_fields = ('title', 'description', 'user__username')
    date_hierarchy = 'due_date'
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Task Information', {
            'fields': ('user', 'title', 'description')
        }),
        ('Dates', {
            'fields': ('due_date', 'created_at', 'updated_at')
        }),
        ('Status', {
            'fields': ('is_completed',)
        }),
    )
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            qs = qs.filter(user=request.user)
        return qs
