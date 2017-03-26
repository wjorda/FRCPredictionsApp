import json

from django.db import transaction
from django.http import Http404, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from predictions import frc
from predictions.models import Event, Match


def index(request):
    event_list = Event.objects.order_by('week').filter()
    context = {
        'event_list': event_list.filter(week__lte=4)
    }
    return render(request, 'predictions/index.html', context)


def event(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    matches = frc.get_matches(event, 'force' in request.GET)
    context = {
        'event': event,
        'matches': sorted(frc.make_predictions(matches), key=lambda m: m[0].sort_key())
    }
    return render(request, 'predictions/event.html', context)


@csrf_exempt
@require_POST
def webhook(request):
    content = json.loads(request.body)
    message_type = content['message_type']
    print(message_type)
    if message_type == 'match_score':
        m = content['message_data']
        event = get_object_or_404(Event, pk=m['event_key'])
        m = m['match']
        with transaction.atomic():
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
                team1 = frc.get_team(allies[0])
                team2 = frc.get_team(allies[1])
                team3 = frc.get_team(allies[2])
                score = m['alliances'][color]['score']

                match = Match(match_id=match_id, event=event, match_num=match_num, round=round, alliance=alliance,
                              score=score, kpa=kpa, rotor=rotor, team1=team1, team2=team2, team3=team3)
                match.save()
        return HttpResponse("OK")
    elif message_type == "schedule_updated":
        m = content['message_data']
        event = get_object_or_404(Event, pk=m['event_key'])
        frc.get_matches(event, force=True)
        return HttpResponse("OK")
    else:
        raise Http404
