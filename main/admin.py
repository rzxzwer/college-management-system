from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Department, Student, Staff, Statistics

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('username', 'email', 'role', 'is_staff', 'is_active',)
    list_filter = ('role', 'is_staff', 'is_active',)
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        ('Роль', {'fields': ('role', 'department', 'group')}),
        ('Права', {'fields': ('is_staff', 'is_active', 'groups', 'user_permissions')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'role', 'department', 'group', 'is_staff', 'is_active')}
        ),
    )
    search_fields = ('username', 'email',)
    ordering = ('username',)

class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

class StudentAdmin(admin.ModelAdmin):
    list_display = ('user', 'group', 'course')
    list_filter = ('course',)
    search_fields = ('user__username', 'group')

class StaffAdmin(admin.ModelAdmin):
    list_display = ('user', 'department', 'position')
    list_filter = ('department',)
    search_fields = ('user__username', 'position')

class StatisticsAdmin(admin.ModelAdmin):
    list_display = ('department', 'date')
    list_filter = ('department', 'date')

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Department, DepartmentAdmin)
admin.site.register(Student, StudentAdmin)
admin.site.register(Staff, StaffAdmin)
admin.site.register(Statistics, StatisticsAdmin)
