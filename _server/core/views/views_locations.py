from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render

from ..models import HOSTILITY, Location, Organization, Character, Event, Note
from .utils import *
from ..forms import LocationForm


RELATED_LOCATIONS = "related_locations"


# /campaigns/<int:campaign_id>/locations/
@login_required
def locations(req: HttpRequest, campaign_id: int) -> HttpResponse:
    campaign_opt = get_campaign_opt(campaign_id, req.user)
    if isinstance(campaign_opt, HttpResponse):
        return campaign_opt

    context = {
        ASSET: ASSET_URL,
        CSS: CSS_FILE,
        CURRENT_USER: req.user,
        CURRENT_CAMPAIGN: campaign_opt,
        LOCATIONS: Location.objects.filter(campaign=campaign_opt),
    }
    return render(req, "campaigns/locations/index.html", context)


# /campaigns/<int:campaign_id>/locations/new/
# @login_required
# def locations_new(req: HttpRequest, campaign_id: int) -> HttpResponse:
#     campaign_opt = get_campaign_opt(campaign_id, req.user)
#     if isinstance(campaign_opt, HttpResponse):
#         return campaign_opt

#     if req.method == "GET":
#         context = {
#             ASSET: ASSET_URL,
#             CSS: CSS_FILE,
#             CURRENT_USER: req.user,
#             CURRENT_CAMPAIGN: campaign_opt,
#             LOCATIONS: Location.objects.filter(campaign=campaign_opt),
#         }
#         return render(req, "campaigns/locations/new.html", context)
#     # else it's POST, and it's a new location request
#     return location_form(req, campaign_opt)

### My version ###
@login_required
def locations_new(request, campaign_id):
    campaign = get_object_or_404(Campaign, id=campaign_id)

    if request.method == "POST":
        form = LocationForm(request.POST)
        if form.is_valid():
            # Save the location object first
            location = form.save(commit=False)
            location.campaign = campaign  # Assuming Location has a campaign ForeignKey
            location.save()
            form.save_m2m()

            # Add neighboring locations (if any)
            neighbors = form.cleaned_data.get("neighboring_locations")
            if neighbors:
                location.neighboring_locations.set(neighbors)

            return redirect("campaign_detail", campaign_id=campaign.id)
        else:
            return HttpResponseBadRequest("Invalid data in form")
    else:
        form = LocationForm()
    return render(request, "locations/new.html", {"form": form, "campaign": campaign})

### ###



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
        ASSET: ASSET_URL,
        CSS: CSS_FILE,
        CURRENT_USER: req.user,
        CURRENT_CAMPAIGN: campaign_opt,
        CURRENT_LOCATION: location_opt,
        RELATED_LOCATIONS: location_opt.neighboring_locations.all(),
        ORGANIZATIONS: Organization.objects.filter(location=location_opt),
        CHARACTERS: Character.objects.filter(from_location=location_opt),
        EVENTS: Event.objects.filter(location=location_opt),
        NOTES: Note.objects.filter(locations=location_opt),
    }
    return render(req, "campaigns/locations/location.html", context)


# /campaigns/<int:campaign_id>/locations/<int:location_id>/edit/
@login_required
def locations_edit(req: HttpRequest, campaign_id: int, location_id: int) -> HttpResponse:
    campaign_opt = get_campaign_opt(campaign_id, req.user)
    if isinstance(campaign_opt, HttpResponse):
        return campaign_opt
    location_opt = get_campaign_field_opt(Location, location_id, campaign_opt)
    if isinstance(location_opt, HttpResponse):
        return location_opt

    if req.method == "GET":
        context = {
            ASSET: ASSET_URL,
            CSS: CSS_FILE,
            CURRENT_USER: req.user,
            CURRENT_CAMPAIGN: campaign_opt,
            CURRENT_LOCATION: location_opt,
            RELATED_LOCATIONS: location_opt.neighboring_locations.all(),
            LOCATIONS: Location.objects.filter(campaign=campaign_opt).exclude(id=location_opt.id),
        }
        return render(req, "campaigns/locations/edit.html", context)
    # else it's POST, and it's an edit location request
    return location_form(req, campaign_opt, location_opt)


# /campaigns/<int:campaign_id>/locations/<int:location_id>/delete/
@login_required
def locations_delete(req: HttpRequest, campaign_id: int, location_id: int) -> HttpResponse:
    campaign_opt = get_campaign_opt(campaign_id, req.user)
    if isinstance(campaign_opt, HttpResponse):
        return campaign_opt
    location_opt = get_campaign_field_opt(Location, location_id, campaign_opt)
    if isinstance(location_opt, HttpResponse):
        return location_opt

    location_opt.delete()
    return redirect(f"/campaigns/{campaign_id}/locations/")
