from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .forms import UserCreationForm, UserChangeForm
from sacred_garden import models


@admin.action(description="Invite user")
def invite_user(modeladmin, request, queryset):
    assert len(queryset) == 1, "Invitation works only for a single user"
    models.invite_user(queryset[0])


class UserAdmin(DjangoUserAdmin):
    add_form = UserCreationForm
    form = UserChangeForm
    model = models.User
    list_display = ("email", "is_staff", "is_active",)
    list_filter = ("email", "is_staff", "is_active",)
    fieldsets = (
        (None, {"fields": ("email", "first_name", "password",
                           "partner_user", "partner_name", "partner_invite_code")}),
        ("Invite", {"fields": ("is_invited", "invite_code")}),
        ("Permissions", {"fields": ("is_staff", "is_active", "groups", "user_permissions")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": (
                "email", "password1", "password2", "is_staff",
                "is_active", "groups", "user_permissions"
            )}
        ),
    )
    search_fields = ("email",)
    ordering = ("email",)
    actions = [invite_user]


class EmotionalNeedStateAdmin(admin.ModelAdmin):
    list_filter = ('emotional_need__name', )
    list_display = ('__str__', 'created_at', )
    ordering = ('-created_at', )


class EmotionalLetterAdmin(admin.ModelAdmin):
    list_display = ('sender', 'recipient', 'is_read')
    ordering = ('-created_at',)


admin.site.register(models.User, UserAdmin)
admin.site.register(models.EmotionalNeed)
admin.site.register(models.EmotionalNeedState, EmotionalNeedStateAdmin)
admin.site.register(models.EmotionalLetter, EmotionalLetterAdmin)
