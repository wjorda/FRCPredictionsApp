from django.contrib import admin

# Register your models here.
from .models import Event, Team, Match


class EventAdmin(admin.ModelAdmin):
    list_display = ('name', 'event_id', 'week', 'type', 'district')


class MatchAdmin(admin.ModelAdmin):
    list_display = ('event', 'name', 'alliance', 'team1', 'team2', 'team3', 'score', 'kpa', 'rotor')


class TeamAdmin(admin.ModelAdmin):
    list_display = ('team_id', 'auto_fuel', 'auto_rotor', 'teleop_fuel', 'teleop_rotor', 'teleop_takeoff')


admin.site.register(Event, EventAdmin)
admin.site.register(Team, TeamAdmin)
admin.site.register(Match, MatchAdmin)
