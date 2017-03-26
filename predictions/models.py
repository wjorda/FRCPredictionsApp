from django.db import models


# Create your models here.
class Team(models.Model):
    team_id = models.CharField("Team ID", max_length=10, primary_key=True)
    auto_fuel = models.FloatField("Auto Fuel OPR")
    auto_rotor = models.FloatField("Auto Rotor OPR")
    teleop_fuel = models.FloatField("Teleop Fuel OPR")
    teleop_rotor = models.FloatField("Teleop Rotor OPR")
    teleop_takeoff = models.FloatField("Teleop Takeoff OPR")

    def __str__(self):
        return self.team_id


class Event(models.Model):
    EVENT_TYPES = (
        (0, 'Regional'),
        (1, 'District Qualifier'),
        (2, 'District Championship'),
        (3, 'Championship Division'),
        (4, 'Championship Finals'),
        (99, 'Offseason'),
        (100, 'Preseason'),
        (-1, 'Other')
    )

    DISTRICTS = (
        ('0', 'No District'),
        ('fim', 'Michigan'),
        ('mar', 'Mid-Atlantic'),
        ('ne', 'New England'),
        ('pnw', 'Pacifc Northwest'),
        ('in', 'Indiana'),
        ('chs', 'Chesapeake'),
        ('nc', 'North Carolina'),
        ('pch', 'Georgia'),
        ('ont', 'Ontario'),
        ('isr', 'Israel'),
    )

    event_id = models.CharField("Event ID", max_length=16, primary_key=True)
    name = models.CharField("Event Name", max_length=255)
    week = models.IntegerField("Event Week")
    type = models.IntegerField("Event Type", choices=EVENT_TYPES)
    district = models.CharField("District", choices=DISTRICTS, max_length=3, null=True)

    def __str__(self):
        return self.name + ' (' + self.event_id + ')'


class Match(models.Model):
    class Meta:
        verbose_name_plural = "matches"

    ROUNDS = (
        ('qm', 'Qualification'),
        ('ef', 'Octofinal'),
        ('qf', 'Quarterfinal'),
        ('sf', 'Semifinal'),
        ('f', 'Final')
    )

    match_id = models.CharField("Match / Alliance ID", max_length=64, primary_key=True)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='matches')
    match_num = models.CharField("Match #", max_length=8)
    round = models.CharField("Round", max_length=2, choices=ROUNDS)
    alliance = models.BooleanField("Red Alliance?")
    score = models.IntegerField("Match Score")
    kpa = models.NullBooleanField("40 KPA Reached?", blank=True, null=True, default=None)
    rotor = models.NullBooleanField("4 Rotors Active?", blank=True, null=True, default=None)

    team1 = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='matches1')
    team2 = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='matches2')
    team3 = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='matches3')

    def name(self) -> str:
        clean_number = self.match_num.replace(self.round, '')
        if self.round == 'qm':
            return 'Qual. ' + clean_number
        else:
            set, num = clean_number.split('m')
            if self.round == 'f':
                return 'Finals ' + num
            elif self.round == 'sf':
                return 'Semi. ' + set + ' Match ' + num
            elif self.round == 'qf':
                return 'Quarter. ' + set + ' Match ' + num
            elif self.round == 'ef':
                return 'Octo. ' + set + ' Match ' + num

    def sort_key(self):
        rounds = {'f': 5000, 'sf': 4000, 'qf': 2000, 'ef': 1000, 'qm': 0}
        clean_number = self.match_num.replace(self.round, '')
        if self.round == 'qm':
            r = int(clean_number) + (0.5 if not self.alliance else 0)
            return r
        else:
            set, num = clean_number.split('m')
            r = rounds[self.round] + 100 * int(set) + int(num) + (0.5 if not self.alliance else 0)
            return r

    def __str__(self):
        return self.match_id
