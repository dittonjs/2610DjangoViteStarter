from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render

from ..models import Location, Organization, Character, Event
from .utils import *


# /campaigns/<int:campaign_id>/events/
@login_required
def events(req: HttpRequest, campaign_id: int) -> HttpResponse:
    campaign_opt = get_campaign_opt(campaign_id, req.user)
    if isinstance(campaign_opt, HttpResponse):
        return campaign_opt

    context = {
        ASSET: ASSET_URL,
        CURRENT_USER: req.user,
        CURRENT_CAMPAIGN: campaign_opt,
        EVENTS: Event.objects.filter(campaign=campaign_opt),
    }
    return render(req, "campaigns/events/index.html", context)


# /campaigns/<int:campaign_id>/events/new/
@login_required
def events_new(req: HttpRequest, campaign_id: int) -> HttpResponse:
    campaign_opt = get_campaign_opt(campaign_id, req.user)
    if isinstance(campaign_opt, HttpResponse):
        return campaign_opt

    if req.method == "GET":
        context = {
            ASSET: ASSET_URL,
            CURRENT_USER: req.user,
            CURRENT_CAMPAIGN: campaign_opt,
            LOCATIONS: Location.objects.filter(campaign=campaign_opt),
            ORGANIZATIONS: Organization.objects.filter(campaign=campaign_opt),
            CHARACTERS: Character.objects.filter(campaign=campaign_opt),
        }
        return render(req, "campaigns/events/new.html", context)
    # else it's POST, and it's a new event request
    return event_form(req, campaign_opt)


# /campaigns/<int:campaign_id>/events/<int:event_id>/
@login_required
def events_id(req: HttpRequest, campaign_id: int, event_id: int) -> HttpResponse:
    campaign_opt = get_campaign_opt(campaign_id, req.user)
    if isinstance(campaign_opt, HttpResponse):
        return campaign_opt
    event_opt = get_campaign_field_opt(Event, event_id, campaign_opt)
    if isinstance(event_opt, HttpResponse):
        return event_opt

    context = {
        ASSET: ASSET_URL,
        CURRENT_USER: req.user,
        CURRENT_CAMPAIGN: campaign_opt,
        CURRENT_EVENT: event_opt,
        ORGANIZATIONS: Organization.objects.filter(event=event_opt),
        CHARACTERS: Character.objects.filter(event=event_opt),
    }
    return render(req, "campaigns/events/event.html", context)


# /campaigns/<int:campaign_id>/events/<int:event_id>/edit/
@login_required
def events_edit(req: HttpRequest, campaign_id: int, event_id: int) -> HttpResponse:
    campaign_opt = get_campaign_opt(campaign_id, req.user)
    if isinstance(campaign_opt, HttpResponse):
        return campaign_opt
    event_opt = get_campaign_field_opt(Event, event_id, campaign_opt)
    if isinstance(event_opt, HttpResponse):
        return event_opt

    if req.method == "GET":
        context = {
            ASSET: ASSET_URL,
            CURRENT_USER: req.user,
            CURRENT_CAMPAIGN: campaign_opt,
            CURRENT_EVENT: event_opt,
            LOCATIONS: Location.objects.filter(campaign=campaign_opt),
            ORGANIZATIONS: Organization.objects.filter(campaign=campaign_opt),
            CHARACTERS: Character.objects.filter(campaign=campaign_opt),
        }
        return render(req, "campaigns/events/edit.html", context)
    # else it's POST, and it's an edit event request
    return event_form(req, campaign_opt, event_opt)


# /campaigns/<int:campaign_id>/events/<int:event_id>/delete/
@login_required
def events_delete(req: HttpRequest, campaign_id: int, event_id: int) -> HttpResponse:
    campaign_opt = get_campaign_opt(campaign_id, req.user)
    if isinstance(campaign_opt, HttpResponse):
        return campaign_opt
    event_opt = get_campaign_field_opt(Event, event_id, campaign_opt)
    if isinstance(event_opt, HttpResponse):
        return event_opt

    event_opt.delete()
    return redirect(f"/campaigns/{campaign_id}/events/")
