from django.urls import path
from .views import views_characters, views_default, views_events, views_locations, views_notes, \
    views_organizations, views_users

urlpatterns = [
    path('', view=views_default.index, name="index"),
    path('campaigns/', view=views_default.campaigns, name="campaigns"),
    path('campaigns/new/', view=views_default.campaigns_new, name="campaigns_new"),
    path('campaigns/<int:campaign_id>/', view=views_default.campaigns_id, name="campaigns_id"),
    path('campaigns/<int:campaign_id>/edit/', view=views_default.campaigns_edit, name="campaigns_edit"),
    path('campaigns/<int:campaign_id>/delete/', view=views_default.campaigns_delete, name="campaigns_delete"),

    path('campaigns/<int:campaign_id>/locations/', view=views_locations.locations, name="locations"),
    path('campaigns/<int:campaign_id>/locations/new/', view=views_locations.locations_new, name="locations_new"),
    path('campaigns/<int:campaign_id>/locations/<int:location_id>/', view=views_locations.locations_id, name="locations_id"),
    path('campaigns/<int:campaign_id>/locations/<int:location_id>/edit/', view=views_locations.locations_edit, name="locations_edit"),
    path('campaigns/<int:campaign_id>/locations/<int:location_id>/delete/', view=views_locations.locations_delete, name="locations_delete"),

    path('campaigns/<int:campaign_id>/organizations/', view=views_organizations.organizations, name="organizations"),
    path('campaigns/<int:campaign_id>/organizations/new/', view=views_organizations.organizations_new, name="organizations_new"),
    path('campaigns/<int:campaign_id>/organizations/<int:organization_id>/', view=views_organizations.organizations_id, name="organizations_id"),
    path('campaigns/<int:campaign_id>/organizations/<int:organization_id>/edit/', view=views_organizations.organizations_edit, name="organizations_edit"),
    path('campaigns/<int:campaign_id>/organizations/<int:organization_id>/delete/', view=views_organizations.organizations_delete, name="organizations_delete"),

    path('campaigns/<int:campaign_id>/characters/', view=views_characters.characters, name="characters"),
    path('campaigns/<int:campaign_id>/characters/new/', view=views_characters.characters_new, name="characters_new"),
    path('campaigns/<int:campaign_id>/characters/<int:character_id>/', view=views_characters.characters_id, name="characters_id"),
    path('campaigns/<int:campaign_id>/characters/<int:character_id>/edit/', view=views_characters.characters_edit, name="characters_edit"),
    path('campaigns/<int:campaign_id>/characters/<int:character_id>/delete/', view=views_characters.characters_delete, name="characters_delete"),

    path('campaigns/<int:campaign_id>/events/', view=views_events.events, name="events"),
    path('campaigns/<int:campaign_id>/events/new/', view=views_events.events_new, name="events_new"),
    path('campaigns/<int:campaign_id>/events/<int:event_id>/', view=views_events.events_id, name="events_id"),
    path('campaigns/<int:campaign_id>/events/<int:event_id>/edit/', view=views_events.events_edit, name="events_edit"),
    path('campaigns/<int:campaign_id>/events/<int:event_id>/delete/', view=views_events.events_delete, name="events_delete"),

    path('campaigns/<int:campaign_id>/notes/', view=views_notes.notes, name="notes"),
    path('campaigns/<int:campaign_id>/notes/new/', view=views_notes.notes_new, name="notes_new"),
    path('campaigns/<int:campaign_id>/notes/<int:note_id>/', view=views_notes.notes_id, name="notes_id"),
    path('campaigns/<int:campaign_id>/notes/<int:note_id>/edit/', view=views_notes.notes_edit, name="notes_edit"),
    path('campaigns/<int:campaign_id>/notes/<int:note_id>/delete/', view=views_notes.notes_delete, name="notes_delete"),
    path('campaigns/<int:campaign_id>/notes/<int:note_id>/convert/', view=views_notes.notes_convert, name="notes_convert"),
]
