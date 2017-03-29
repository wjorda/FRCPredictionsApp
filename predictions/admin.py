from django.contrib import admin

# Register your models here.
from .models import Event, Team, Match


class EventAdmin(admin.ModelAdmin):
    list_display = ('name', 'event_id', 'week', 'type', 'district')
    search_fields = ['name', 'event_id', 'district']


class MatchAdmin(admin.ModelAdmin):
    list_display = ('event', 'name', 'alliance', 'team1', 'team2', 'team3', 'score', 'kpa', 'rotor')
    search_fields = ['event__event_id', 'team1__team_id', 'team2__team_id', 'team3__team_id']


class TeamAdmin(admin.ModelAdmin):
    list_display = ('team_id', 'auto_fuel', 'auto_rotor', 'teleop_fuel', 'teleop_rotor', 'teleop_takeoff')
    search_fields = ['team_id']


admin.site.register(Event, EventAdmin)
admin.site.register(Team, TeamAdmin)
admin.site.register(Match, MatchAdmin)
