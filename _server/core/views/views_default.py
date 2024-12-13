from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest
from django.shortcuts import redirect, render

from ..models import Campaign, Location, Organization, Character, Event, Note
from .utils import *


# / Welcome page
def index(req: HttpRequest) -> HttpResponse:
    return render(req, "core/index.html", {ASSET: ASSET_URL, CSS: CSS_FILE, CURRENT_USER: req.user})


# /campaigns/
@login_required
def campaigns(req: HttpRequest) -> HttpResponse:
    context = {
        ASSET: ASSET_URL,
        CSS: CSS_FILE,
        CURRENT_USER: req.user,
        CAMPAIGNS: Campaign.objects.filter(dm=req.user),
    }
    return render(req, "campaigns/index.html", context)


# /campaigns/new/
@login_required
def campaigns_new(req: HttpRequest) -> HttpResponse:
    if req.method == "GET":
        context = {
            ASSET: ASSET_URL,
            CSS: CSS_FILE,
            CURRENT_USER: req.user,
            # Normally, the user would input a username manually, or use a Friends list
            USERS: User.objects.exclude(id=req.user.id),  # useful for adding users to approved users
        }
        return render(req, "campaigns/new.html", context)
    # else it's POST, and it's a new campaign request
    return campaign_form(req)


# /campaigns/<int:campaign_id>/
@login_required
def campaigns_id(req: HttpRequest, campaign_id: int) -> HttpResponse:
    campaign_opt = get_campaign_opt(campaign_id, req.user)
    if isinstance(campaign_opt, HttpResponse):
        return campaign_opt

    context = {
        ASSET: ASSET_URL,
        CSS: CSS_FILE,
        CURRENT_USER: req.user,
        USER_IS_DM: req.user == campaign_opt.dm,
        CURRENT_CAMPAIGN: campaign_opt,
        LOCATIONS: Location.objects.filter(campaign=campaign_opt),
        ORGANIZATIONS: Organization.objects.filter(campaign=campaign_opt),
        CHARACTERS: Character.objects.filter(campaign=campaign_opt),
        EVENTS: Event.objects.filter(campaign=campaign_opt),
        NOTES: Note.objects.filter(campaign=campaign_opt),
    }
    return render(req, "campaigns/campaign.html", context)


# /campaigns/<int:campaign_id>/edit/
@login_required
def campaigns_edit(req: HttpRequest, campaign_id: int) -> HttpResponse:
    campaign_opt = get_campaign_opt(campaign_id, req.user)
    if isinstance(campaign_opt, HttpResponse):
        return campaign_opt

    if req.method == "GET":
        context = {
            ASSET: ASSET_URL,
            CSS: CSS_FILE,
            CURRENT_USER: req.user,
            CURRENT_CAMPAIGN: campaign_opt,
            USERS: User.objects.exclude(id=req.user.id),  # useful for adding users to approved users
        }
        return render(req, "campaigns/edit.html", context)
    # else it's POST, and it's an edit campaign request
    return campaign_form(req, campaign_opt)


# /campaigns/<int:campaign_id>/delete/
@login_required
def campaigns_delete(req: HttpRequest, campaign_id: int) -> HttpResponse:
    campaign_opt = get_campaign_opt(campaign_id, req.user)
    if isinstance(campaign_opt, HttpResponse):
        return campaign_opt

    campaign_opt.delete()
    return redirect("/campaigns/")

