from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate, logout
from django.http import JsonResponse
from core.models import Campaign

# Create your views here.
def sign_up(req):
    if req.method == "POST":
        user = User.objects.create_user(
            username=req.POST.get("email"),
            password=req.POST.get("password"),
            email=req.POST.get("email"),
            first_name=req.POST.get("first_name"),
            last_name=req.POST.get("last_name")
        )
        login(req, user)
        return redirect("/")
    else:
        return render(req, "registration/sign_up.html")

def sign_in(req):
    if req.method == "POST":
        user = authenticate(req, username=req.POST.get("email"), password=req.POST.get("password"))
        if user is not None:
            login(req, user)
            return redirect("/")

        return render(req, "registration/sign_in.html")
    else:
        return render(req, "registration/sign_in.html")

def logout_view(request):
    logout(request)
    return JsonResponse({"success": True })

def campaigns_new(request):
    if request.method == 'POST':
        # Get the form data
        name = request.POST.get('name')
        description = request.POST.get('description')
        is_public = request.POST.get('is_public') == 'on'
        approved_users = request.POST.getlist('approved_users')  # Replace with actual field handling logic

        # Debugging line
        print(f"Name: {name}, Description: {description}, Is Public: {is_public}, Approved Users: {approved_users}")

        # Creating the campaign
        campaign = Campaign.objects.create(
            name=name,
            description=description,
            is_public=is_public,
        )

        # Update the Many-to-Many field, the issue is you were trying to directly update it but we need this to do it for us
        if approved_users:  # Ensure you have a valid list, if publice we can default to all
            campaign.approved_users.set(approved_users)

        return redirect('/campaigns/')  # Redirect to the desired page after saving

    # In the future we should add a played with or friends feature, this is a safety risk if it wasn't just a small project for friends
    return render(request, 'campaigns/new_campaign.html', {'all_users': all_users})