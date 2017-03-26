import json

from django.http import Http404, HttpResponse
from django.shortcuts import render, get_object_or_404

from predictions import frc
from predictions.models import Event


def index(request):
    event_list = Event.objects.order_by('week').filter()
    context = {
        'event_list': event_list.filter(week__lte=4)
    }
    return render(request, 'predictions/index.html', context)


def event(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    matches = frc.get_matches(event)
    context = {
        'event': event,
        'matches': sorted(frc.make_predictions(matches), key=lambda m: m[0].sort_key())
    }
    return render(request, 'predictions/event.html', context)


def webhook(request):
    if not request.method == 'POST': raise Http404
    print(json.loads(request.body))
    return HttpResponse("OK")
