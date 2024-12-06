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

from ..models import *
from .utils import *


# Load manifest when server launches
MANIFEST = {}
if not settings.DEBUG:
    f = open(f"{settings.BASE_DIR}/core/static/manifest.json")
    MANIFEST = json.load(f)


def field_index(req: HttpRequest, campaign_id: int, field_id: int) -> HttpResponse:
    campaign_opt = get_campaign_opt(campaign_id, req.user)
