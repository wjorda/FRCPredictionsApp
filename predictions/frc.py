import pandas as pandas
from django.db import transaction
from pytba.api import TBAClient
from sklearn.externals import joblib

from predictions.stats_stuff import get_overlap
from .models import Team, Match, Event

tba = TBAClient('wjordan', 'predictons_import', '0.1')

opr_data16 = None
means2017 = pandas.Series({
    'autoRotorPoints': 5.865,
    'autoFuelPoints': 0.218192,
    'teleopRotorPoints': 24.773390,
    'teleopTakeoffPoints': 18.892727,
    'teleopFuelPoints': 0.310983
})
std2017 = pandas.Series({
    'autoRotorPoints': 10.432360,
    'autoFuelPoints': 1.270938,
    'teleopRotorPoints': 10.443990,
    'teleopTakeoffPoints': 18.516841,
    'teleopFuelPoints': 1.526010
})
rookie2017 = pandas.Series({
    'autoRotorPoints': 3.832922,
    'autoFuelPoints': -0.011375,
    'teleopRotorPoints': 22.424046,
    'teleopTakeoffPoints': 9.586984,
    'teleopFuelPoints': 0.008998
})


def get_team(team_id: str) -> Team:
    team = Team.objects.filter(pk=team_id)
    if len(team) > 0: return team.first()

    global opr_data16
    if opr_data16 is None:
        opr_data16 = pandas.read_csv('records2016.csv')
        opr_data16.index = opr_data16.Team
        opr_data16 = opr_data16.groupby('Team').mean()
        opr_data16 = (opr_data16 - opr_data16.mean()) / opr_data16.std()

    with transaction.atomic():
        if team_id not in opr_data16.index:
            row = rookie2017.copy()
        else:
            row = opr_data16.loc[team_id]
            row = (row.total * std2017 * 0.666) + means2017

        team = Team(
            team_id=team_id, auto_fuel=row.autoFuelPoints, auto_rotor=row.autoRotorPoints,
            teleop_fuel=row.teleopFuelPoints,
            teleop_rotor=row.teleopRotorPoints, teleop_takeoff=row.teleopTakeoffPoints
        )

        team.save()

    return team


def get_matches(event: Event):
    matches = event.matches.all()
    if len(matches) > 0: return matches

    matches_tba = tba.tba_get('event/%s/matches' % event.event_id)
    matches = []

    with transaction.atomic():
        for m in matches_tba:
            for color in ['red', 'blue']:
                match_id = m['key'] + '_' + color
                match_num = m['key'].split('_')[1]
                round = m['comp_level']
                alliance = color == 'red'

                if m['score_breakdown'] is not None:
                    score = m['score_breakdown'][color]
                    kpa = (score['kPaBonusPoints'] > 0 or score['kPaRankingPointAchieved'])
                    rotor = (score['rotorBonusPoints'] > 0 or score['rotorRankingPointAchieved'])
                else:
                    kpa = None
                    rotor = None

                allies = m['alliances'][color]['teams']
                team1 = get_team(allies[0])
                team2 = get_team(allies[1])
                team3 = get_team(allies[2])
                score = m['alliances'][color]['score']

                match = Match(match_id=match_id, event=event, match_num=match_num, round=round, alliance=alliance,
                              score=score, kpa=kpa, rotor=rotor, team1=team1, team2=team2, team3=team3)
                matches.append(match)
                match.save()

    return matches


model = None


def make_predictions(matches):
    global model
    if model is None:
        print(__file__)
        model = joblib.load('steamworks_pred.p')

    def sum_oprs(m: Match):
        auto_fuel = m.team1.auto_fuel + m.team2.auto_fuel + m.team3.auto_fuel
        auto_rotor = m.team1.auto_rotor + m.team2.auto_rotor + m.team3.auto_rotor
        teleop_fuel = m.team1.teleop_fuel + m.team2.teleop_fuel + m.team3.teleop_fuel
        teleop_rotor = m.team1.teleop_rotor + m.team2.teleop_rotor + m.team3.teleop_rotor
        teleop_takeoff = m.team1.teleop_takeoff + m.team2.teleop_takeoff + m.team3.teleop_takeoff
        return auto_fuel, auto_rotor, teleop_fuel, teleop_rotor, teleop_takeoff

    opr_sums = [sum_oprs(m) for m in matches]
    pred_scores = model.predict(opr_sums) * 1.5
    probs = []

    for i, score in enumerate(pred_scores):
        if i % 2 == 0:
            opp_score = pred_scores[i + 1]
        else:
            opp_score = pred_scores[i - 1]

        prob = get_overlap(score, opp_score, 44.1, 44.1) * 100
        probs.append(prob)

    return zip(matches, pred_scores, probs)
