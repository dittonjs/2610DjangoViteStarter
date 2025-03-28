from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.shortcuts import redirect, render

from .utils import LOGIN_PAGE, HOME_PAGE, CURRENT_USER, ASSET, ASSET_URL, CSS, CSS_FILE


# /users/ (redirecting)
def users(req: HttpRequest) -> HttpResponse:
    if req.user.is_authenticated:
        return redirect(f"/users/{req.user.id}/")
    return redirect(LOGIN_PAGE)


# /users/new/
def users_new(req: HttpRequest) -> HttpResponse:
    if req.user.is_authenticated:
        return redirect(f"/users/{req.user.id}/")
    if req.method == "GET":
        return render(req, "users/new.html", {ASSET: ASSET_URL, CSS: CSS_FILE})

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


# /users/login/
def users_login(req: HttpRequest) -> HttpResponse:
    if req.user.is_authenticated:
        return redirect(f"/users/{req.user.id}/")
    if req.method == "GET":
        return render(req, "users/login.html", {ASSET: ASSET_URL, CSS: CSS_FILE})

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


# /users/logout/
@login_required
def users_logout(req: HttpRequest) -> HttpResponse:
    logout(req)
    return redirect(HOME_PAGE)


# /users/<int:user_id>/
@login_required
def users_id(req: HttpRequest, user_id: int) -> HttpResponse:
    if req.user.id != user_id or not User.objects.filter(id=user_id).exists():
        return HttpResponseForbidden("You do not have access to this page")
    return render(req, "users/user.html", {ASSET: ASSET_URL, CSS: CSS_FILE, CURRENT_USER: req.user})


# /users/<int:user_id>/delete/
@login_required
def users_delete(req: HttpRequest, user_id: int) -> HttpResponse:
    if req.user.id != user_id or not User.objects.filter(id=user_id).exists():
        return HttpResponseForbidden("You do not have access delete someone else's account")
    req.user.delete()
    return redirect(HOME_PAGE)
