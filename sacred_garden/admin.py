from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .forms import UserCreationForm, UserChangeForm
from sacred_garden import emails
from sacred_garden import models


@admin.action(description="Invite user")
def invite_user(modeladmin, request, queryset):
    assert len(queryset) == 1, "Invitation works only for a single user"
    user = queryset[0]
    models.invite_user(user)
    emails.send_invite(user)


class UserAdmin(DjangoUserAdmin):
    add_form = UserCreationForm
    form = UserChangeForm
    model = models.User
    list_display = ("email", "is_staff", "is_active",)
    list_filter = ("is_staff", "is_active",)
    fieldsets = (
        (None, {"fields": ("email", "first_name", "password",
                           "partner_user", "partner_name", "partner_invite_code", "is_sample")}),
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
    list_filter = ('emotional_need', )
    list_display = ('__str__', 'created_at', 'is_current')
    ordering = ('-created_at', )


class EmotionalLetterAdmin(admin.ModelAdmin):
    list_display = ('sender', 'recipient', 'is_read')
    ordering = ('-created_at',)


admin.site.register(models.User, UserAdmin)
admin.site.register(models.EmotionalNeed)
admin.site.register(models.EmotionalNeedState, EmotionalNeedStateAdmin)
admin.site.register(models.EmotionalLetter, EmotionalLetterAdmin)
