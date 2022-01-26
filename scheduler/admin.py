from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.conf import settings
from .models import Profile, Schedule, Event


@admin.register(Profile)
class ProfileAdmin(UserAdmin):
    list_display = ("email",)

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "username",
                    "password",
                )
            },
        ),
        (
            "User details",
            {
                "fields": (
                    ("first_name", "last_name"),
                    "email",
                    "phone_number",
                )
            },
        ),
    )

    def has_add_permission(self, request):
        # disable add due to singleton model
        return False

    def has_delete_permission(self, request, obj=None):
        # disable delete due to singleton model
        return False


@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "sun_off",
        "mon_off",
        "tue_off",
        "wed_off",
        "thu_off",
        "fri_off",
        "sat_off",
    )

    def has_add_permission(self, request):
        # don't allow if there's already an instance
        if Schedule.objects.exists():
            return False
        return super().has_add_permission(request)

    def has_delete_permission(self, request, obj=None):
        # disable delete due to singleton model
        return False

    def add_view(self, request, form_url="", extra_context=None):
        extra_context = {
            "show_save_and_add_another": False,
        }
        return super().add_view(request, form_url, extra_context)

    def change_view(self, request, object_id, form_url="", extra_context=None):
        self.fieldsets = (
            (
                None,
                {
                    "fields": (
                        "sun_off",
                        ("sun_start", "sun_end"),
                        "mon_off",
                        ("mon_start", "mon_end"),
                        "tue_off",
                        ("tue_start", "tue_end"),
                        "wed_off",
                        ("wed_start", "wed_end"),
                        "thu_off",
                        ("thu_start", "thu_end"),
                        "fri_off",
                        ("fri_start", "fri_end"),
                        "sat_off",
                        ("sat_start", "sat_end"),
                    )
                },
            ),
        )
        return super().change_view(request, object_id, form_url, extra_context)


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = (
        "booker_name",
        "booker_email",
        "start_time",
        "end_time",
    )

    def has_add_permission(self, request):
        # only allow add in DEBUG mode
        if settings.DEBUG:
            return super().has_add_permission(request)
        return False

    def has_delete_permission(self, request, obj=None):
        # only allow delete in DEBUG mode
        if settings.DEBUG:
            return super().has_delete_permission(request, obj)
        return False
