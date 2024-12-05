from django.db import models


HOSTILITY = (
    ("H", "Hostile"),
    ("N", "Neutral"),
    ("F", "Friendly"),
)
CLASSES = (
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


class User(models.Model):
    id = models.BigAutoField(primary_key=True)
    first_name = models.TextField()
    last_name = models.TextField()
    username = models.TextField(unique=True)
    email = models.TextField(unique=True)
    password_hash = models.TextField()


class Campaign(models.Model):
    id = models.BigAutoField(primary_key=True)
    dm = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.TextField()
    description = models.TextField(null=True)
    is_public = models.BooleanField()
    approved_users = models.ManyToManyField(User, related_name='campaign_users')


class Note(models.Model):
    id = models.BigAutoField(primary_key=True)
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE)
    title = models.TextField()
    content = models.TextField(null=True)


class Location(models.Model):
    id = models.BigAutoField(primary_key=True)
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE)
    name = models.TextField()
    neighboring_locations = models.ManyToManyField('self', related_name='neighboring_locations')
    description = models.TextField(null=True)
    hostility = models.TextField(choices=HOSTILITY, default="N")


class Organization(models.Model):
    id = models.BigAutoField(primary_key=True)
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE)
    name = models.TextField()
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True)
    related_organizations = models.ManyToManyField('self', related_name='related_organizations')
    description = models.TextField(null=True)
    hostility = models.TextField(choices=HOSTILITY, default="N")


class Character(models.Model):
    id = models.BigAutoField(primary_key=True)
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE)
    name = models.TextField()
    race = models.TextField(default="Human")
    from_location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True)
    organizations = models.ManyToManyField(Organization, related_name='character_organizations')
    description = models.TextField(null=True)


class PlayerCharacter(Character):
    player = models.ForeignKey(User, on_delete=models.CASCADE)
    level = models.PositiveSmallIntegerField(default=1)
    clazz = models.TextField(choices=CLASSES)


class NonPlayerCharacter(Character):
    clazz = models.TextField(choices=CLASSES, null=True)
    hostility = models.TextField(choices=HOSTILITY, default="N")


class Event(models.Model):
    id = models.BigAutoField(primary_key=True)
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE)
    title = models.TextField()
    time_start = models.DateTimeField()
    time_end = models.DateTimeField(null=True)
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True)
    description = models.TextField(null=True)
    involved_organizations = models.ManyToManyField(Organization, related_name='event_organizations')
    involved_characters = models.ManyToManyField(Character, related_name='event_characters')
