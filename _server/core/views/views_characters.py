from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render

from ..models import CLASSES, Location, Organization, Character, Event, Note
from .utils import *


# /campaigns/<int:campaign_id>/characters/
@login_required
def characters(req: HttpRequest, campaign_id: int) -> HttpResponse:
    campaign_opt = get_campaign_opt(campaign_id, req.user)
    if isinstance(campaign_opt, HttpResponse):
        return campaign_opt

    context = {
        ASSET: ASSET_URL,
        CURRENT_USER: req.user,
        CURRENT_CAMPAIGN: campaign_opt,
        CHARACTERS: Character.objects.filter(campaign=campaign_opt),
    }
    return render(req, "campaigns/characters/index.html", context)


# /campaigns/<int:campaign_id>/characters/new/
@login_required
def characters_new(req: HttpRequest, campaign_id: int) -> HttpResponse:
    campaign_opt = get_campaign_opt(campaign_id, req.user)
    if isinstance(campaign_opt, HttpResponse):
        return campaign_opt

    if req.method == "GET":
        context = {
            ASSET: ASSET_URL,
            CURRENT_USER: req.user,
            CURRENT_CAMPAIGN: campaign_opt,
            CLASSES: dict(CLASSES),
            LOCATIONS: Location.objects.filter(campaign=campaign_opt),
            ORGANIZATIONS: Organization.objects.filter(campaign=campaign_opt),
            CHARACTERS: Character.objects.filter(campaign=campaign_opt),
            USERS: User.objects.all(),
        }
        return render(req, "campaigns/characters/new.html", context)
    # else it's POST, and it's a new character request
    return character_form(req, campaign_opt)


# /campaigns/<int:campaign_id>/characters/<int:character_id>/
@login_required
def characters_id(req: HttpRequest, campaign_id: int, character_id: int) -> HttpResponse:
    campaign_opt = get_campaign_opt(campaign_id, req.user)
    if isinstance(campaign_opt, HttpResponse):
        return campaign_opt
    character_opt = get_campaign_field_opt(Character, character_id, campaign_opt)
    if isinstance(character_opt, HttpResponse):
        return character_opt

    context = {
        ASSET: ASSET_URL,
        CURRENT_USER: req.user,
        CURRENT_CAMPAIGN: campaign_opt,
        CURRENT_CHARACTER: character_opt,
        EVENTS: Event.objects.filter(involved_characters=character_opt),
        NOTES: Note.objects.filter(involved_characters=character_opt),
    }
    return render(req, "campaigns/characters/character.html", context)


# /campaigns/<int:campaign_id>/characters/<int:character_id>/edit/
@login_required
def characters_edit(req: HttpRequest, campaign_id: int, character_id: int) -> HttpResponse:
    campaign_opt = get_campaign_opt(campaign_id, req.user)
    if isinstance(campaign_opt, HttpResponse):
        return campaign_opt
    character_opt = get_campaign_field_opt(Character, character_id, campaign_opt)
    if isinstance(character_opt, HttpResponse):
        return character_opt

    if req.method == "GET":
        context = {
            ASSET: ASSET_URL,
            CURRENT_USER: req.user,
            CURRENT_CAMPAIGN: campaign_opt,
            CURRENT_CHARACTER: character_opt,
            CLASSES: dict(CLASSES),
            LOCATIONS: Location.objects.filter(campaign=campaign_opt),
            ORGANIZATIONS: Organization.objects.filter(campaign=campaign_opt),
            CHARACTERS: Character.objects.filter(campaign=campaign_opt)\
                                         .exclude(id=character_opt.id),
            USERS: User.objects.all(),
        }
        return render(req, "campaigns/characters/edit.html", context)
    # else it's POST, and it's an edit character request
    return character_form(req, campaign_opt, character_opt)


# /campaigns/<int:campaign_id>/characters/<int:character_id>/delete/
@login_required
def characters_delete(req: HttpRequest, campaign_id: int, character_id: int) -> HttpResponse:
    campaign_opt = get_campaign_opt(campaign_id, req.user)
    if isinstance(campaign_opt, HttpResponse):
        return campaign_opt
    character_opt = get_campaign_field_opt(Character, character_id, campaign_opt)
    if isinstance(character_opt, HttpResponse):
        return character_opt

    character_opt.delete()
    return redirect(f"/campaigns/{campaign_id}/characters/")
