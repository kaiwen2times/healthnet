from django.contrib import admin

from healthnet.models import Location, Hospital, Account, Profile, Action, Appointment, MedicalTest, Statistics


class LocationAdmin(admin.ModelAdmin):
    fields = ['city', 'zip', 'state', 'country', 'address']
    list_display = ('address', 'city', 'state', 'country', 'zip')


admin.site.register(Location, LocationAdmin)


class HospitalAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Name', {'fields': ['name']}),
        ('Phone', {'fields': ['phone']}),
        ('Location', {'fields': ['location']}),
    ]
    list_display = ('name', 'location', 'phone')


admin.site.register(Hospital, HospitalAdmin)


class AccountAdmin(admin.ModelAdmin):
    fields = ['role', 'profile', 'user']
    list_display = ('role', 'profile')


admin.site.register(Account, AccountAdmin)


class ProfileAdmin(admin.ModelAdmin):
    fields = [
        'firstname',
        'lastname',
        'insurance',
        'emergencyContactName',
        'emergencyContactNumber',
        'sex',
        'birthday',
        'phone',
        'allergies',
    ]
    list_display = ('firstname', 'lastname', 'birthday', 'created')


admin.site.register(Profile, ProfileAdmin)


class ActionAdmin(admin.ModelAdmin):
    readonly_fields = ('timePerformed',)
    fields = [
        'type',
        'description',
        'user',
    ]
    list_display = ('user', 'type', 'description', 'timePerformed')
    list_filter = ('user', 'type', 'timePerformed')
    ordering = ('-timePerformed',)


admin.site.register(Action, ActionAdmin)


class AppointmentAdmin(admin.ModelAdmin):
    fields = [
        'doctor',
        'patient',
        'description',
        'active',
        'hospital',
        'startTime',
        'endTime',
        'date'
    ]
    list_display = ('description', 'hospital', 'date', 'doctor', 'patient', 'startTime', 'endTime', 'active')


admin.site.register(Appointment, AppointmentAdmin)


class MedicalTestAdmin(admin.ModelAdmin):
    fields = [
        'name',
        'date',
        'hospital',
        'description',
        'doctor',
        'patient',
        'private',
        'completed'
    ]
    list_display = ('name', 'doctor', 'patient', 'date')


admin.site.register(MedicalTest, MedicalTestAdmin)

class StatsAdmin(admin.ModelAdmin):
    readonly_fields = ('stats', 'freq')
    list_filter = ('stats','freq')

admin.site.register(Statistics, StatsAdmin)