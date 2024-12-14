from django.contrib.auth.models import User
from django.db import models


HOSTILITY = (
    ("H", "Hostile"),
    ("N", "Neutral"),
    ("F", "Friendly"),
)

CLASSES = (
    (None, ""),
    ("A",  "Artificer"),
    ("B",  "Barbarian"),
    ("Bd", "Bard"),
    ("C",  "Cleric"),
    ("D",  "Druid"),
    ("F",  "Fighter"),
    ("M",  "Monk"),
    ("P",  "Paladin"),
    ("R",  "Ranger"),
    ("Rg", "Rogue"),
    ("S",  "Sorcerer"),
    ("W",  "Wizard"),
)


class Campaign(models.Model):
    id = models.BigAutoField(primary_key=True)
    dm = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.TextField()
    description = models.TextField(null=True, blank=True)
    is_public = models.BooleanField()
    approved_users = models.ManyToManyField(User, related_name='campaign_users')


class Location(models.Model):
    FRIENDLY = 'F'
    NEUTRAL = 'N'
    HOSTILE = 'H'

    HOSTILITY_CHOICES = [
        (FRIENDLY, 'Friendly'),
        (NEUTRAL, 'Neutral'),
        (HOSTILE, 'Hostile'),
    ]

    id = models.BigAutoField(primary_key=True)
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name="locations")
    name = models.TextField()
    neighboring_locations = models.ManyToManyField('self', related_name='neighbors', symmetrical=True, blank=True)
    description = models.TextField(null=True, blank=True)
    hostility = models.TextField(choices=HOSTILITY_CHOICES, default="N")


class Organization(models.Model):
    id = models.BigAutoField(primary_key=True)
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE)
    name = models.TextField()
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, blank=True)
    related_organizations = models.ManyToManyField('self', related_name='related_organizations')
    description = models.TextField(null=True, blank=True)
    hostility = models.TextField(choices=HOSTILITY, default="N")


class Character(models.Model):
    id = models.BigAutoField(primary_key=True)
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE)
    name = models.TextField()
    race = models.TextField(default="Human", blank=True)
    clazz = models.TextField(choices=CLASSES, null=True, blank=True)
    level = models.PositiveSmallIntegerField(default=0, blank=True)
    from_location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, blank=True)
    organizations = models.ManyToManyField(Organization, related_name='character_organizations')
    related_characters = models.ManyToManyField('self', related_name='related_characters')
    description = models.TextField(null=True, blank=True)


class PlayerCharacter(Character):
    player = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)


class NonPlayerCharacter(Character):
    hostility = models.TextField(choices=HOSTILITY, default="N")


class Event(models.Model):
    id = models.BigAutoField(primary_key=True)
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE)
    title = models.TextField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, blank=True)
    involved_organizations = models.ManyToManyField(Organization,
                                                    related_name='event_organizations')
    involved_characters = models.ManyToManyField(Character, related_name='event_characters')
    description = models.TextField(null=True, blank=True)


class Note(models.Model):
    id = models.BigAutoField(primary_key=True)
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE)
    title = models.TextField()
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    race = models.TextField(null=True, blank=True)
    clazz = models.TextField(choices=CLASSES, null=True, blank=True)
    level = models.PositiveSmallIntegerField(default=0, null=True, blank=True)
    hostility = models.TextField(choices=HOSTILITY, default="N", null=True, blank=True)
    locations = models.ManyToManyField(Location, related_name='note_locations', blank=True)
    organizations = models.ManyToManyField(Organization, related_name='note_organizations',
                                           blank=True)
    characters = models.ManyToManyField(Character, related_name='note_characters', blank=True)
    content = models.TextField(null=True, blank=True)
