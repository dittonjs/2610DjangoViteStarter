import os
from datetime import datetime
from django.contrib.auth.models import User
from django.db import models
from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest, HttpResponseForbidden, \
    HttpResponseNotFound
from django.shortcuts import redirect, render
from typing import Type

from ..models import CLASSES, HOSTILITY, Campaign, Location, Organization, Character, \
    PlayerCharacter, NonPlayerCharacter, Event, Note


ASSET_URL = os.environ.get("ASSET_URL", "")
TIME_FORMAT = "%Y-%m-%dT%H:%M"

# Context keys
ASSET                = "asset_url"
CSS                  = "css_file"
CSS_FILE             = "style.css"
CURRENT_USER         = "current_user"
USERS                = "users"
USER_IS_DM           = "is_dm"
CURRENT_CAMPAIGN     = "current_campaign"
CAMPAIGNS            = "campaigns"
CURRENT_LOCATION     = "current_location"
LOCATIONS            = "locations"
CURRENT_ORGANIZATION = "current_organization"
ORGANIZATIONS        = "organizations"
CURRENT_CHARACTER    = "current_character"
CHARACTERS           = "characters"
CURRENT_EVENT        = "current_event"
EVENTS               = "events"
CURRENT_NOTE         = "current_note"
NOTES                = "notes"
CONVERSION_TYPES     = "conversion_types"

HOME_PAGE = "/"
LOGIN_PAGE = "/users/login/"


def get_campaign_opt(campaign_id: int, user: User) -> Campaign | HttpResponse:
    """
    Attempts to find the given Campaign and verifies the given User has access to it.

    Args:
        campaign_id (int): The ID of the Campaign to find
        user (User):       The User to verify Campaign ownership for

    Returns:
        campaign_opt (Campaign | HttpResponse):
            The Campaign if found and the User has access, else a 4XX HttpResponse
    """
    if not Campaign.objects.filter(id=campaign_id).exists():
        return HttpResponseNotFound("Campaign does not exist")
    campaign = Campaign.objects.get(id=campaign_id)
    if not (campaign.is_public
            or user == campaign.dm
            or user in campaign.approved_users.all()):
        return HttpResponseForbidden("You do not have access to this campaign")
    return campaign


def get_campaign_field_opt(model_type: Type[models.Model], id: int, campaign: Campaign) \
                           -> models.Model | HttpResponse:
    """
    Attempts to find the given model and verifies it belongs to the given Campaign.

    Args:
        models_to_search (Type[models.Model]): The model type to search for (e.g. Location)
        id (int):                              The ID of the model to find
        campaign (Campaign):                   The Campaign to verify model belongs to

    Returns:
        field_opt (models.Model | HttpResponse):
            The field if found and it belongs to the Campaign, else a 4XX HttpResponse
    """
    if not model_type.objects.filter(id=id).exists():
        return HttpResponseNotFound(f"The requested {model_type.__name__} does not exist")
    found_model = model_type.objects.get(id=id)
    if found_model.campaign != campaign:
        return HttpResponseForbidden(f"The requested {model_type.__name__} does not belong "
                                     "to this campaign")
    return found_model


def campaign_form(req: HttpRequest, campaign: Campaign | None=None) -> HttpResponse:
    name = req.POST.get("name")
    if not name:
        return HttpResponseBadRequest("Missing campaign name")
    description = req.POST.get("description")
    is_public = req.POST.get("is_public") == "on"
    approved_users = req.POST.getlist("approved_users")
    if campaign:
        campaign.name = name
        campaign.description = description
        campaign.is_public = is_public
    else:
        campaign = Campaign(dm=req.user, name=name, description=description, is_public=is_public)
    campaign.approved_users.set(approved_users)
    campaign.save()
    return redirect(f"/campaigns/{campaign.id}/")


def location_form(req: HttpRequest, campaign: Campaign, location: Location | None=None) \
                  -> HttpResponse:
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
            location_opt = get_campaign_field_opt(Location, location_id, campaign)
            if isinstance(location_opt, HttpResponse):
                return location_opt
            neighboring_locations.append(location_opt)

    if location:
        location.name = name
        location.description = description
        location.hostility = hostility
        location.neighboring_locations.set(neighboring_locations)
    else:
        location = Location(campaign=campaign, name=name,
                            neighboring_locations=neighboring_locations, description=description,
                            hostility=hostility)
    location.save()
    return redirect(f"/campaigns/{campaign.id}/locations/{location.id}/")


def character_form(req: HttpRequest, campaign: Campaign, character: Character | None=None) \
                   -> HttpResponse:
    name = req.POST.get("name")
    if not name:
        return HttpResponseBadRequest("Missing character name")
    race = req.POST.get("race")
    race = race if race else Character.race.default
    clazz = req.POST.get("class")
    level = req.POST.get("level")
    try:
        level = int(level) if level else Character.level.default
    except ValueError:
        return HttpResponseBadRequest("Invalid level: must be an integer")
    description = req.POST.get("description")

    location_id = req.POST.get("location")
    location_opt = None
    if location_id:
        try:
            location_id = int(req.POST.get("location"))
        except ValueError:
            return HttpResponseBadRequest("Invalid location")
        location_opt = get_campaign_field_opt(Location, location_id, campaign)
        if isinstance(location_opt, HttpResponse):
            return location_opt
    
    organization_ids = req.POST.getlist("organizations")
    organizations: list[Organization] = []
    if organization_ids:
        try:
            organization_ids = [int(organization) for organization in organization_ids]
        except ValueError:
            return HttpResponseBadRequest("Invalid organization")
        for organization_id in organization_ids:
            organization_opt = get_campaign_field_opt(Organization, organization_id, campaign)
            if isinstance(organization_opt, HttpResponse):
                return organization_opt
            organizations.append(organization_opt)

    character_ids = req.POST.getlist("characters")
    characters: list[Character] = []
    if character_ids:
        try:
            character_ids = [int(character) for character in character_ids]
        except ValueError:
            return HttpResponseBadRequest("Invalid character")
        for character_id in character_ids:
            character_opt = get_campaign_field_opt(Character, character_id, campaign)
            if isinstance(character_opt, HttpResponse):
                return character_opt
            characters.append(character_opt)

    if character:
        character.name = name
        character.race = race
        character.clazz = clazz
        character.level = level
        character.from_location = location_opt
        character.organizations.set(organizations)
        character.related_characters.set(characters)
        character.description = description
        if isinstance(character, PlayerCharacter):
            pc_id = req.POST.get("pc")
            pc_opt = None
            if pc_id:
                try:
                    pc_id = int(pc_id)
                except ValueError:
                    return HttpResponseBadRequest("Invalid player character")
                pc_opt = get_campaign_field_opt(User, pc_id, campaign)
                if isinstance(pc_opt, HttpResponse):
                    return pc_opt
            character.player = pc_opt
        if isinstance(character, NonPlayerCharacter):
            hostility = req.POST.get("hostility")
            if hostility not in dict(HOSTILITY).keys():
                return HttpResponseBadRequest("Invalid hostility level")
            character.hostility = hostility
    else:  # New character
        is_pc = req.POST.get("is_pc") == "on"
        if is_pc:
            pc_id = req.POST.get("pc")
            pc_opt = None
            if pc_id:
                try:
                    pc_id = int(pc_id)
                except ValueError:
                    return HttpResponseBadRequest("Invalid player character")
                pc_opt = get_campaign_field_opt(User, pc_id, campaign)
                if isinstance(pc_opt, HttpResponse):
                    return pc_opt
            character = PlayerCharacter(campaign=campaign, name=name, race=race, clazz=clazz,
                                        level=level, from_location=location_opt,
                                        organizations=organizations, related_characters=characters,
                                        description=description, player=pc_opt)
        else:  # NPC
            hostility = req.POST.get("hostility")
            if hostility not in dict(HOSTILITY).keys():
                return HttpResponseBadRequest("Invalid hostility level")
            character = NonPlayerCharacter(campaign=campaign, name=name, race=race, clazz=clazz,
                                           level=level, from_location=location_opt,
                                           organizations=organizations,
                                           related_characters=characters, description=description,
                                           hostility=hostility)
    character.save()
    return redirect(f"/campaigns/{campaign.id}/characters/{character.id}/")


def event_form(req: HttpRequest, campaign: Campaign, event: Event | None=None) -> HttpResponse:
    title = req.POST.get("title")
    if not title:
        return HttpResponseBadRequest("Missing event title")
    description = req.POST.get("description")

    start_time = req.POST.get("start_time")
    if not start_time:
        return HttpResponseBadRequest("Missing event start time")
    end_time = req.POST.get("end_time")
    try:
        start_time = datetime.strptime(start_time, TIME_FORMAT)
        end_time = datetime.strptime(end_time, TIME_FORMAT) if end_time else None
    except ValueError:
        return HttpResponseBadRequest("Invalid time format")

    location_id = req.POST.get("location")
    location_opt = None
    if location_id:
        try:
            location_id = int(req.POST.get("location"))
        except ValueError:
            return HttpResponseBadRequest("Invalid location")
        location_opt = get_campaign_field_opt(Location, location_id, campaign)
        if isinstance(location_opt, HttpResponse):
            return location_opt

    organization_ids = req.POST.getlist("organizations")
    organizations: list[Organization] = []
    if organization_ids:
        try:
            organization_ids = [int(organization) for organization in organization_ids]
        except ValueError:
            return HttpResponseBadRequest("Invalid organization")
        for organization_id in organization_ids:
            organization_opt = get_campaign_field_opt(Organization, organization_id, campaign)
            if isinstance(organization_opt, HttpResponse):
                return organization_opt
            organizations.append(organization_opt)

    character_ids = req.POST.getlist("characters")
    characters: list[Character] = []
    if character_ids:
        try:
            character_ids = [int(character) for character in character_ids]
        except ValueError:
            return HttpResponseBadRequest("Invalid character")
        for character_id in character_ids:
            character_opt = get_campaign_field_opt(Character, character_id, campaign)
            if isinstance(character_opt, HttpResponse):
                return character_opt
            characters.append(character_opt)

    if event:
        event.title = title
        event.start_time = start_time
        event.end_time = end_time
        event.location = location_opt
        event.involved_organizations.set(organizations)
        event.involved_characters.set(characters)
        event.description = description
    else:
        event = Event(campaign=campaign, title=title, start_time=start_time, end_time=end_time,
                      location=location_opt, involved_organizations=organizations,
                      involved_characters=characters, description=description)
    event.save()
    return redirect(f"/campaigns/{campaign.id}/events/{event.id}/")


def note_form(req: HttpRequest, campaign: Campaign, note: Note | None=None) -> HttpResponse:
    title = req.POST.get("title")
    if not title:
        return HttpResponseBadRequest("Missing note title")
    content = req.POST.get("content")

    start_time = req.POST.get("start_time")
    end_time = req.POST.get("end_time")
    try:
        start_time = datetime.strptime(start_time, TIME_FORMAT) if start_time else None
        end_time = datetime.strptime(end_time, TIME_FORMAT) if end_time else None
    except ValueError:
        return HttpResponseBadRequest("Invalid time format")
    
    race = req.POST.get("race")
    race = race if race else None  # prevents empty field
    clazz = req.POST.get("class")
    clazz = clazz if clazz else None  # prevents empty field
    if clazz:
        if clazz not in dict(CLASSES).keys():
            return HttpResponseBadRequest("Invalid class")
    level = req.POST.get("level")
    try:
        level = int(level) if level else None
    except ValueError:
        return HttpResponseBadRequest("Invalid level: must be an integer")
    
    hostility = req.POST.get("hostility")
    hostility = hostility if hostility else None  # prevents empty field
    if hostility:
        if hostility not in dict(HOSTILITY).keys():
            return HttpResponseBadRequest("Invalid hostility level")
        
    location_ids = req.POST.getlist("locations")
    locations: list[Location] = []
    if location_ids:
        try:
            location_ids = [int(location) for location in location_ids]
        except ValueError:
            return HttpResponseBadRequest("Invalid location")
        for location_id in location_ids:
            location_opt = get_campaign_field_opt(Location, location_id, campaign)
            if isinstance(location_opt, HttpResponse):
                return location_opt
            locations.append(location_opt)

    organization_ids = req.POST.getlist("organizations")
    organizations: list[Organization] = []
    if organization_ids:
        try:
            organization_ids = [int(organization) for organization in organization_ids]
        except ValueError:
            return HttpResponseBadRequest("Invalid organization")
        for organization_id in organization_ids:
            organization_opt = get_campaign_field_opt(Organization, organization_id, campaign)
            if isinstance(organization_opt, HttpResponse):
                return organization_opt
            organizations.append(organization_opt)

    character_ids = req.POST.getlist("characters")
    characters: list[Character] = []
    if character_ids:
        try:
            character_ids = [int(character) for character in character_ids]
        except ValueError:
            return HttpResponseBadRequest("Invalid character")
        for character_id in character_ids:
            character_opt = get_campaign_field_opt(Character, character_id, campaign)
            if isinstance(character_opt, HttpResponse):
                return character_opt
            characters.append(character_opt)

    if note:
        note.title = title
        note.start_time = start_time
        note.end_time = end_time
        note.race = race
        note.clazz = clazz
        note.level = level
        note.hostility = hostility
        note.locations.set(locations)
        note.organizations.set(organizations)
        note.characters.set(characters)
        note.content = content
    else:
        note = Note(campaign=campaign, title=title, start_time=start_time, end_time=end_time,
                    race=race, clazz=clazz, level=level, hostility=hostility, locations=locations,
                    organizations=organizations, characters=characters, content=content)
    note.save()
    return redirect(f"/campaigns/{campaign.id}/notes/{note.id}/")


def get_conversion_types(note: Note) -> list[Type[models.Model]]:
    """
    Determines which models a Note can be converted to.

    Args:
        note (Note): The Note to determine conversion types for

    Returns:
        conversion_types (list[Type[models.Model]]): The models the Note can be converted to
    """
    possible_types: list[Type[models.Model]] = [Location, Organization, Character, Event]
    if note.start_time is not None or note.end_time is not None:
        if note.hostility is not None:
            possible_types = []
            return possible_types
        possible_types = [Event]
    else:
        possible_types.remove(Event)
    if note.race is not None or note.clazz is not None or note.level is not None:
        if Character in possible_types:
            possible_types = [Character]
        else:
            possible_types = []
            return possible_types
    if len(note.locations.all()) > 1:  # only a Location can link to multiple (i.e., neighbors)
        if Location in possible_types:
            possible_types = [Location]
        else:
            possible_types = []
    return possible_types


def note_convert(req: HttpRequest, campaign: Campaign, note: Note) -> HttpResponse:
    possible_conversions = get_conversion_types(note)
    conversion_type = req.POST.get("conversion_type")
    if not conversion_type or conversion_type not in [model.__name__
                                                      for model in possible_conversions]:
        return HttpResponseBadRequest("Can't convert to the requested type")

    if conversion_type == "Location":
        name = note.title
        neighboring_locations = note.locations.all()
        description = note.content
        hostility = note.hostility if note.hostility else Location.hostility.default
        location = Location(campaign=note.campaign, name=name,
                            neighboring_locations=neighboring_locations, description=description,
                            hostility=hostility)
        location.save()
        rval = redirect(f"/campaigns/{campaign.id}/locations/{location.id}/")
    elif conversion_type == "Organization":
        name = note.title
        location = note.locations.first()
        hostility = note.hostility if note.hostility else Organization.hostility.default
        related_organizations = note.organizations.all()
        description = note.content
        organization = Organization(campaign=note.campaign, name=name, location=location,
                                    related_organizations=related_organizations,
                                    description=description, hostility=hostility)
        organization.save()
        rval = redirect(f"/campaigns/{campaign.id}/organizations/{organization.id}/")
    elif conversion_type == "Character":
        name = note.title
        race = note.race if note.race else Character.race.default
        clazz = note.clazz
        level = note.level if note.level else Character.level.default
        from_location = note.locations.first()
        organizations = note.organizations.all()
        related_characters = note.characters.all()
        description = note.content

        is_pc = req.POST.get("is_pc") == "on"
        if is_pc:
            pc_id = req.POST.get("pc")
            pc_opt = None
            if pc_id:
                try:
                    pc_id = int(pc_id)
                except ValueError:
                    return HttpResponseBadRequest("Invalid player character")
                pc_opt = get_campaign_field_opt(User, pc_id, campaign)
                if isinstance(pc_opt, HttpResponse):
                    return pc_opt
            character = PlayerCharacter(campaign=campaign, name=name, race=race, clazz=clazz,
                                        level=level, from_location=from_location,
                                        organizations=organizations,
                                        related_characters=related_characters,
                                        description=description, player=pc_opt)
        else:  # NPC
            hostility = note.hostility if note.hostility else NonPlayerCharacter.hostility.default
            character = NonPlayerCharacter(campaign=campaign, name=name, race=race, clazz=clazz,
                                           level=level, from_location=from_location,
                                           organizations=organizations,
                                           related_characters=related_characters,
                                           description=description, hostility=hostility)
        character.save()
        rval = redirect(f"/campaigns/{campaign.id}/characters/{character.id}/")
    elif conversion_type == "Event":
        title = note.title
        # if no start, end must have been populated per get_conversion_types
        start_time = note.start_time if note.start_time else note.end_time
        end_time = note.end_time
        location = note.locations.first()
        involved_organizations = note.organizations.all()
        involved_characters = note.characters.all()
        description = note.content
        event = Event(campaign=campaign, title=title, start_time=start_time, end_time=end_time,
                      location=location, involved_organizations=involved_organizations,
                      involved_characters=involved_characters, description=description)
        event.save()
        rval = redirect(f"/campaigns/{campaign.id}/events/{event.id}/")
    # Wait til the very end to delete the note, in case of some error occurring
    note.delete()
    return rval
