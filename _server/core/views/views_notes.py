from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render

from ..models import Location, Organization, Character, Event
from .utils import *


# /campaigns/<int:campaign_id>/notes/
@login_required
def notes(req: HttpRequest, campaign_id: int) -> HttpResponse:
    campaign_opt = get_campaign_opt(campaign_id, req.user)
    if isinstance(campaign_opt, HttpResponse):
        return campaign_opt

    context = {
        ASSET: ASSET_URL,
        CSS: CSS_FILE,
        CURRENT_USER: req.user,
        CURRENT_CAMPAIGN: campaign_opt,
        NOTES: Note.objects.filter(campaign=campaign_opt),
    }
    return render(req, "campaigns/notes/index.html", context)


# /campaigns/<int:campaign_id>/notes/new/
@login_required
def notes_new(req: HttpRequest, campaign_id: int) -> HttpResponse:
    campaign_opt = get_campaign_opt(campaign_id, req.user)
    if isinstance(campaign_opt, HttpResponse):
        return campaign_opt

    if req.method == "GET":
        context = {
            ASSET: ASSET_URL,
            CSS: CSS_FILE,
            CURRENT_USER: req.user,
            CURRENT_CAMPAIGN: campaign_opt,
            LOCATIONS: Location.objects.filter(campaign=campaign_opt),
            ORGANIZATIONS: Organization.objects.filter(campaign=campaign_opt),
            CHARACTERS: Character.objects.filter(campaign=campaign_opt),
        }
        return render(req, "campaigns/notes/new.html", context)
    # else it's POST, and it's a new note request
    return note_form(req, campaign_opt)


# /campaigns/<int:campaign_id>/notes/<int:note_id>/
@login_required
def notes_id(req: HttpRequest, campaign_id: int, note_id: int) -> HttpResponse:
    campaign_opt = get_campaign_opt(campaign_id, req.user)
    if isinstance(campaign_opt, HttpResponse):
        return campaign_opt
    note_opt = get_campaign_field_opt(Note, note_id, campaign_opt)
    if isinstance(note_opt, HttpResponse):
        return note_opt

    context = {
        ASSET: ASSET_URL,
        CSS: CSS_FILE,
        CURRENT_USER: req.user,
        CURRENT_CAMPAIGN: campaign_opt,
        CURRENT_NOTE: note_opt,
    }
    return render(req, "campaigns/notes/note.html", context)


# /campaigns/<int:campaign_id>/notes/<int:note_id>/edit/
@login_required
def notes_edit(req: HttpRequest, campaign_id: int, note_id: int) -> HttpResponse:
    campaign_opt = get_campaign_opt(campaign_id, req.user)
    if isinstance(campaign_opt, HttpResponse):
        return campaign_opt
    note_opt = get_campaign_field_opt(Note, note_id, campaign_opt)
    if isinstance(note_opt, HttpResponse):
        return note_opt

    if req.method == "GET":
        context = {
            ASSET: ASSET_URL,
            CSS: CSS_FILE,
            CURRENT_USER: req.user,
            CURRENT_CAMPAIGN: campaign_opt,
            CURRENT_NOTE: note_opt,
            LOCATIONS: Location.objects.filter(campaign=campaign_opt),
            ORGANIZATIONS: Organization.objects.filter(campaign=campaign_opt),
            CHARACTERS: Character.objects.filter(campaign=campaign_opt),
        }
        return render(req, "campaigns/notes/edit.html", context)
    # else it's POST, and it's an edit note request
    return note_form(req, campaign_opt, note_opt)


# /campaigns/<int:campaign_id>/notes/<int:note_id>/delete/
@login_required
def notes_delete(req: HttpRequest, campaign_id: int, note_id: int) -> HttpResponse:
    campaign_opt = get_campaign_opt(campaign_id, req.user)
    if isinstance(campaign_opt, HttpResponse):
        return campaign_opt
    note_opt = get_campaign_field_opt(Note, note_id, campaign_opt)
    if isinstance(note_opt, HttpResponse):
        return note_opt

    note_opt.delete()
    return redirect("campaigns_notes", campaign_id=campaign_id)


# /campaigns/<int:campaign_id>/notes/<int:note_id>/convert/
@login_required
def notes_convert(req: HttpRequest, campaign_id: int, note_id: int) -> HttpResponse:
    campaign_opt = get_campaign_opt(campaign_id, req.user)
    if isinstance(campaign_opt, HttpResponse):
        return campaign_opt
    note_opt = get_campaign_field_opt(Note, note_id, campaign_opt)
    if isinstance(note_opt, HttpResponse):
        return note_opt

    if req.method == "GET":
        conversion_types = get_conversion_types(note_opt)
        context = {
            ASSET: ASSET_URL,
            CSS: CSS_FILE,
            CURRENT_USER: req.user,
            CURRENT_CAMPAIGN: campaign_opt,
            CURRENT_NOTE: note_opt,
            CONVERSION_TYPES: conversion_types,
        }
        return render(req, "campaigns/notes/convert.html", context)
    # else it's POST, and it's a convert note request
    return note_convert(req, campaign_opt, note_opt, conversion_types)
