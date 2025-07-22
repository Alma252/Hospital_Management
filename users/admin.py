from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Doctor, Patient


# شخصی‌سازی نمایش مدل User در پنل ادمین
class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'full_name', 'role', 'is_active', 'is_staff')
    list_filter = ('role', 'is_active', 'is_staff')
    search_fields = ('email', 'full_name')
    ordering = ('email',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('اطلاعات شخصی', {'fields': ('full_name', 'role')}),
        ('سطوح دسترسی', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        ('تاریخچه', {'fields': ('last_login',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'full_name', 'role', 'password1', 'password2'),
        }),
    )

@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('user', 'specialty', 'hospital', 'approved', 'approval_date')
    list_filter = ('approved', 'specialty', 'hospital')
    search_fields = ('user__username', 'user__email', 'specialty', 'hospital')


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('user', 'age', 'gender', 'phone_number')
    search_fields = ('user__email', 'phone_number')


# ثبت مدل User با کلاس سفارشی‌شده
admin.site.register(User, UserAdmin)
