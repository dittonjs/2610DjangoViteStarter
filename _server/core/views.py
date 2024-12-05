import json
import os
from django.conf  import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest, HttpResponseForbidden, \
    HttpResponseNotFound
from django.shortcuts import redirect, render
from typing import Type
from .models import *


# Load manifest when server launches
MANIFEST = {}
if not settings.DEBUG:
    f = open(f"{settings.BASE_DIR}/core/static/manifest.json")
    MANIFEST = json.load(f)

ASSET_URL = os.environ.get("ASSET_URL", "")

ASSET = "asset_url"
CURRENT_USER = "user"
USERS = "users"
USER_IS_DM = "is_dm"
CURRENT_CAMPAIGN = "campaign"
CAMPAIGNS = "campaigns"
CURRENT_LOCATION = "location"
LOCATIONS = "locations"
CURRENT_ORGANIZATION = "organization"
ORGANIZATIONS = "organizations"
CURRENT_CHARACTER = "character"
CHARACTERS = "characters"
CURRENT_EVENT = "event"
EVENTS = "events"
NOTES = "notes"

HOME_PAGE = "/"
LOGIN_PAGE = "/users/login/"


def get_campaign_opt(campaign_id: int, user: User) -> Campaign | HttpResponse:
    if not Campaign.objects.filter(id=campaign_id).exists():
        return HttpResponseNotFound("Campaign does not exist")
    campaign = Campaign.objects.get(id=campaign_id)
    if not (campaign.is_public
            or user == campaign.dm
            or user in campaign.approved_users.all()):
        return HttpResponseForbidden("You do not have access to this campaign")
    return campaign


def get_campaign_field_opt(models_to_search: Type[models.Model], id: int, campaign: Campaign) \
                           -> models.Model | HttpResponse:
    if not models_to_search.objects.filter(id=id).exists():
        return HttpResponseNotFound(f"The requested {models_to_search.__name__} does not exist")
    found_model = models_to_search.objects.get(id=id)
    if found_model.campaign != campaign:
        return HttpResponseForbidden(f"The requested {models_to_search.__name__} does not belong "
                                     "to this campaign")
    return found_model


# / Welcome page
def index(req: HttpRequest) -> HttpResponse:
    return render(req, "core/index.html", {CURRENT_USER: req.user})


# /users/ redirecting
def users(req: HttpRequest) -> HttpResponse:
    if req.user.is_authenticated:
        return redirect(f"/users/{req.user.id}/")
    return redirect(LOGIN_PAGE)


# /users/login/
def users_login(req: HttpRequest) -> HttpResponse:
    if req.user.is_authenticated:
        return redirect(f"/users/{req.user.id}/")
    if req.method == "GET":
        return render(req, "users/login.html")

    # else it's POST, and it's a login request
    username = req.POST.get("username")
    password = req.POST.get("password")
    if not (username and password):
        return HttpResponseBadRequest("Missing username or password")

    user = authenticate(req, username=username, password=password)
    if user is None:
        return HttpResponseBadRequest("Invalid username or password")
    login(req, user)
    return redirect("/campaigns/")


# /users/new/
def users_new(req: HttpRequest) -> HttpResponse:
    if req.user.is_authenticated:
        return redirect(f"/users/{req.user.id}/")
    if req.method == "GET":
        return render(req, "users/new.html")

    # else it's POST, and it's a new user request
    username = req.POST.get("username")
    password = req.POST.get("password")
    if not (username and password):
        return HttpResponseBadRequest("Missing username or password")
    if User.objects.filter(username=username).exists():
        return HttpResponseForbidden("Username already taken")

    first_name = req.POST.get("first_name")
    last_name = req.POST.get("last_name")
    if not (first_name and last_name):
        return HttpResponseBadRequest("Missing first or last name")

    user = User.objects.create_user(username=username, password=password, first_name=first_name,
                                    last_name=last_name)

    user = authenticate(req, username=username, password=password)
    if user is None:
        return HttpResponseBadRequest("Invalid username or password")
    login(req, user)
    return redirect("/campaigns/")


# /users/<int:user_id>/
@login_required
def users_id(req: HttpRequest, user_id: int) -> HttpResponse:
    if req.user.id != user_id or not User.objects.filter(id=user_id).exists():
        return HttpResponseForbidden("You do not have access to this page")
    return render(req, "/users/user.html", {CURRENT_USER: req.user})


# /users/logout/
@login_required
def users_logout(req: HttpRequest) -> HttpResponse:
    logout(req)
    return redirect(HOME_PAGE)


# /users/<int:user_id>/delete/
@login_required
def users_delete(req: HttpRequest, user_id: int) -> HttpResponse:
    if req.user.id != user_id or not User.objects.filter(id=user_id).exists():
        return HttpResponseForbidden("You do not have access delete someone else's account")
    req.user.delete()
    return redirect(HOME_PAGE)


# /campaigns/
@login_required
def campaigns(req: HttpRequest) -> HttpResponse:
    context = {
        CURRENT_USER: req.user,
        CAMPAIGNS: Campaign.objects.filter(dm=req.user),
    }
    return render(req, "/campaigns/index.html", context)


# /campaigns/new/
@login_required
def campaigns_new(req: HttpRequest) -> HttpResponse:
    if req.method == "GET":
        context = {
            CURRENT_USER: req.user,
            USERS: User.objects.all(),  # useful for adding users to approved users
        }
        return render(req, "campaigns/new.html")

    # else it's POST, and it's a new campaign request
    name = req.POST.get("name")
    if not name:
        return HttpResponseBadRequest("Missing campaign name")
    description = req.POST.get("description")
    is_public = req.POST.get("is_public") == "on"
    approved_users = req.POST.getlist("approved_users")
    campaign = Campaign(dm=req.user, name=name, description=description, is_public=is_public,
                        approved_users=approved_users)
    campaign.save()
    return redirect(f"/campaigns/{campaign.id}/")


# /campaigns/<int:campaign_id>/
@login_required
def campaigns_id(req: HttpRequest, campaign_id: int) -> HttpResponse:
    campaign_opt = get_campaign_opt(campaign_id, req.user)
    if isinstance(campaign_opt, HttpResponse):
        return campaign_opt

    context = {
        CURRENT_USER: req.user,
        USER_IS_DM: req.user == campaign_opt.dm,
        CURRENT_CAMPAIGN: campaign_opt,
        LOCATIONS: Location.objects.filter(campaign=campaign_opt),
        ORGANIZATIONS: Organization.objects.filter(campaign=campaign_opt),
        CHARACTERS: Character.objects.filter(campaign=campaign_opt),
        EVENTS: Event.objects.filter(campaign=campaign_opt),
        NOTES: Note.objects.filter(campaign=campaign_opt),
    }
    return render(req, "/campaigns/campaign.html", context)


# /campaigns/<int:campaign_id>/edit/
@login_required
def campaigns_edit(req: HttpRequest, campaign_id: int) -> HttpResponse:
    campaign_opt = get_campaign_opt(campaign_id, req.user)
    if isinstance(campaign_opt, HttpResponse):
        return campaign_opt

    if req.method == "GET":
        context = {
            CURRENT_USER: req.user,
            CURRENT_CAMPAIGN: campaign_opt,
            USERS: User.objects.all(),  # useful for adding users to approved users
        }
        return render(req, "/campaigns/edit.html", context)

    # else it's POST, and it's an edit campaign request
    name = req.POST.get("name")
    if not name:
        return HttpResponseBadRequest("Missing campaign name")
    description = req.POST.get("description")
    is_public = req.POST.get("is_public") == "on"
    approved_users = req.POST.getlist("approved_users")
    campaign_opt.name = name
    campaign_opt.description = description
    campaign_opt.is_public = is_public
    campaign_opt.approved_users.set(approved_users)
    campaign_opt.save()
    return redirect(f"/campaigns/{campaign_opt.id}/")


# /campaigns/<int:campaign_id>/delete/
@login_required
def campaigns_delete(req: HttpRequest, campaign_id: int) -> HttpResponse:
    campaign_opt = get_campaign_opt(campaign_id, req.user)
    if isinstance(campaign_opt, HttpResponse):
        return campaign_opt

    campaign_opt.delete()
    return redirect("/campaigns/")


# /campaigns/<int:campaign_id>/locations/
@login_required
def locations(req: HttpRequest, campaign_id: int) -> HttpResponse:
    campaign_opt = get_campaign_opt(campaign_id, req.user)
    if isinstance(campaign_opt, HttpResponse):
        return campaign_opt

    context = {
        CURRENT_USER: req.user,
        CURRENT_CAMPAIGN: campaign_opt,
        LOCATIONS: Location.objects.filter(campaign=campaign_opt),
    }
    return render(req, "/campaigns/locations/index.html", context)


# /campaigns/<int:campaign_id>/locations/new/
@login_required
def locations_new(req: HttpRequest, campaign_id: int) -> HttpResponse:
    campaign_opt = get_campaign_opt(campaign_id, req.user)
    if isinstance(campaign_opt, HttpResponse):
        return campaign_opt

    if req.method == "GET":
        context = {
            CURRENT_USER: req.user,
            CURRENT_CAMPAIGN: campaign_opt,
            LOCATIONS: Location.objects.filter(campaign=campaign_opt),
        }
        return render(req, "/campaigns/locations/new.html", context)

    # else it's POST, and it's a new location request
    name = req.POST.get("name")
    if not name:
        return HttpResponseBadRequest("Missing location name")
    description = req.POST.get("description")

    hostility = req.POST.get("hostility")
    if hostility not in dict(HOSTILITY).keys():
        return HttpResponseBadRequest("Invalid hostility level")

    location_ids = req.POST.getlist("locations")
    neighboring_locations: list[Location] = []
    if location_ids:
        try:
            location_ids = [int(location) for location in location_ids]
        except ValueError:
            return HttpResponseBadRequest("Invalid neighboring location")
        for location_id in location_ids:
            location_opt = get_campaign_field_opt(Location, location_id, campaign_opt)
            if isinstance(location_opt, HttpResponse):
                return location_opt
            neighboring_locations.append(location_opt)
            
    location = Location(campaign=campaign_opt, name=name,
                        neighboring_locations=neighboring_locations, description=description,
                        hostility=hostility)
    location.save()
    return redirect(f"/campaigns/{campaign_id}/locations/{location.id}/")


# /campaigns/<int:campaign_id>/locations/<int:location_id>/
@login_required
def locations_id(req: HttpRequest, campaign_id: int, location_id: int) -> HttpResponse:
    campaign_opt = get_campaign_opt(campaign_id, req.user)
    if isinstance(campaign_opt, HttpResponse):
        return campaign_opt
    location_opt = get_campaign_field_opt(Location, location_id, campaign_opt)
    if isinstance(location_opt, HttpResponse):
        return location_opt

    context = {
        CURRENT_USER: req.user,
        CURRENT_CAMPAIGN: campaign_opt,
        CURRENT_LOCATION: location_opt,
        LOCATIONS: Location.objects.filter(campaign=campaign_opt),  # Related locations
        ORGANIZATIONS: Organization.objects.filter(location=location_opt),
        CHARACTERS: Character.objects.filter(from_location=location_opt),
        EVENTS: Event.objects.filter(location=location_opt),
        NOTES: Note.objects.filter(location=location_opt),
    }
    return render(req, "/campaigns/locations/location.html", context)
