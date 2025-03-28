from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render

from ..models import HOSTILITY_CHOICES, Location, Organization, Character, Event, Note
from .utils import *
from ..forms import OrganizationForm


RELATED_ORGANIZATIONS = "related_organizations"


# /campaigns/<int:campaign_id>/organizations/
@login_required
def organizations(req: HttpRequest, campaign_id: int) -> HttpResponse:
    campaign_opt = get_campaign_opt(campaign_id, req.user)
    if isinstance(campaign_opt, HttpResponse):
        return campaign_opt

    context = {
        ASSET: ASSET_URL,
        CSS: CSS_FILE,
        CURRENT_USER: req.user,
        CURRENT_CAMPAIGN: campaign_opt,
        ORGANIZATIONS: Organization.objects.filter(campaign=campaign_opt),
    }
    return render(req, "campaigns/organizations/index.html", context)


# /campaigns/<int:campaign_id>/organizations/new/
### My Version ###
@login_required
def organizations_new(request, campaign_id):
    campaign = get_object_or_404(Campaign, id=campaign_id)

    if request.method == "POST":
        form = OrganizationForm(request.POST)
        if form.is_valid():
            # Save first
            organization = form.save(commit=False)
            organization.campaign = campaign
            organization.save()
            form.save_m2m()

            related_orgs = form.cleaned_data.get("related_organizations")
            if related_orgs:
                organization.related_organizations.set(related_orgs)

            return redirect(f"/campaigns/{campaign.id}/organizations/")
        else:
            return HttpResponseBadRequest("Invalid data in form")
    else:
        form = OrganizationForm()
    return render(request, "campaigns/organizations/new.html", {"form": form, "campaign": campaign})


###  ###


# @login_required
# def organizations_new(req: HttpRequest, campaign_id: int) -> HttpResponse:
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
#             ORGANIZATIONS: Organization.objects.filter(campaign=campaign_opt),
#         }
#         return render(req, "campaigns/organizations/new.html", context)

#     # else it's POST, and it's a new organization request
#     name = req.POST.get("name")
#     if not name:
#         return HttpResponseBadRequest("Missing organization name")
#     description = req.POST.get("description")

#     hostility = req.POST.get("hostility")
#     if hostility not in dict(HOSTILITY).keys():
#         return HttpResponseBadRequest("Invalid hostility level")

#     try:
#         location_id = int(req.POST.get("location"))
#     except ValueError:
#         return HttpResponseBadRequest("Invalid location")
#     location_opt = get_campaign_field_opt(Location, location_id, campaign_opt)
#     if isinstance(location_opt, HttpResponse):
#         return location_opt

#     organization_ids = req.POST.getlist("organizations")
#     associated_organizations: list[Organization] = []
#     if organization_ids:
#         try:
#             organization_ids = [int(organization) for organization in organization_ids]
#         except ValueError:
#             return HttpResponseBadRequest("Invalid associated organization")
#         for organization_id in organization_ids:
#             organization_opt = get_campaign_field_opt(Organization, organization_id, campaign_opt)
#             if isinstance(organization_opt, HttpResponse):
#                 return organization_opt
#             associated_organizations.append(organization_opt)


#     organization = Organization(campaign=campaign_opt, name=name, location=location_opt,
#                                 related_organizations=associated_organizations,
#                                 description=description, hostility=hostility)
#     organization.save()
#     return redirect(f"/campaigns/{campaign_id}/organizations/{organization.id}/")




# /campaigns/<int:campaign_id>/organizations/<int:organization_id>/
@login_required
def organizations_id(req: HttpRequest, campaign_id: int, organization_id: int) -> HttpResponse:
    campaign_opt = get_campaign_opt(campaign_id, req.user)
    if isinstance(campaign_opt, HttpResponse):
        return campaign_opt
    organization_opt = get_campaign_field_opt(Organization, organization_id, campaign_opt)
    if isinstance(organization_opt, HttpResponse):
        return organization_opt

    context = {
        ASSET: ASSET_URL,
        CSS: CSS_FILE,
        CURRENT_USER: req.user,
        CURRENT_CAMPAIGN: campaign_opt,
        CURRENT_ORGANIZATION: organization_opt,
        RELATED_ORGANIZATIONS: organization_opt.related_organizations.all(),
        CHARACTERS: Character.objects.filter(organization=organization_opt),
        EVENTS: Event.objects.filter(organization=organization_opt),
        NOTES: Note.objects.filter(organization=organization_opt),
    }
    return render(req, "campaigns/organizations/organization.html", context)


# /campaigns/<int:campaign_id>/organizations/<int:organization_id>/edit/
@login_required
def organizations_edit(req: HttpRequest, campaign_id: int, organization_id: int) -> HttpResponse:
    campaign_opt = get_campaign_opt(campaign_id, req.user)
    if isinstance(campaign_opt, HttpResponse):
        return campaign_opt
    organization_opt = get_campaign_field_opt(Organization, organization_id, campaign_opt)
    if isinstance(organization_opt, HttpResponse):
        return organization_opt

    if req.method == "GET":
        context = {
            ASSET: ASSET_URL,
            CSS: CSS_FILE,
            CURRENT_USER: req.user,
            CURRENT_CAMPAIGN: campaign_opt,
            CURRENT_ORGANIZATION: organization_opt,
            RELATED_ORGANIZATIONS: organization_opt.related_organizations.all(),
            LOCATIONS: Location.objects.filter(campaign=campaign_opt),
            ORGANIZATIONS: Organization.objects.filter(campaign=campaign_opt)\
                                               .exclude(id=organization_opt.id),
        }
        return render(req, "campaigns/organizations/edit.html", context)

    # else it's POST, and it's an edit organization request
    name = req.POST.get("name")
    if not name:
        return HttpResponseBadRequest("Missing organization name")
    description = req.POST.get("description")

    hostility = req.POST.get("hostility")
    if hostility not in dict(HOSTILITY).keys():
        return HttpResponseBadRequest("Invalid hostility level")

    try:
        location_id = int(req.POST.get("location"))
    except ValueError:
        return HttpResponseBadRequest("Invalid location")
    location_opt = get_campaign_field_opt(Location, location_id, campaign_opt)
    if isinstance(location_opt, HttpResponse):
        return location_opt

    organization_ids = req.POST.getlist("organizations")
    associated_organizations: list[Organization] = []
    if organization_ids:
        try:
            organization_ids = [int(organization) for organization in organization_ids]
        except ValueError:
            return HttpResponseBadRequest("Invalid associated organization")
        for organization_id in organization_ids:
            organization_opt = get_campaign_field_opt(Organization, organization_id, campaign_opt)
            if isinstance(organization_opt, HttpResponse):
                return organization_opt
            associated_organizations.append(organization_opt)

    organization_opt.name = name
    organization_opt.location = location_opt
    organization_opt.related_organizations = associated_organizations
    organization_opt.description = description
    organization_opt.hostility = hostility
    organization_opt.save()
    return redirect(f"/campaigns/{campaign_id}/organizations/{organization_id}/")


# /campaigns/<int:campaign_id>/organizations/<int:organization_id>/delete/
@login_required
def organizations_delete(req: HttpRequest, campaign_id: int, organization_id: int) -> HttpResponse:
    campaign_opt = get_campaign_opt(campaign_id, req.user)
    if isinstance(campaign_opt, HttpResponse):
        return campaign_opt
    organization_opt = get_campaign_field_opt(Organization, organization_id, campaign_opt)
    if isinstance(organization_opt, HttpResponse):
        return organization_opt

    organization_opt.delete()
    return redirect(f"/campaigns/{campaign_id}/organizations/")
