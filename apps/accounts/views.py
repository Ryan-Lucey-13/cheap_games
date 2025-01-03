from django.shortcuts import render
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404

from apps.accounts.forms import UserEditForm, SignupForm
from apps.accounts.models import User
from apps.core.models import DashBoardPanel
from apps.core.models import FavoriteGame

def log_in(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, request.POST)
        if form.is_valid():
            # User has specified valid credentials, have user log-in, and then
            # redirect back home
            login(request, form.get_user())
            return redirect('home')
    else:
        form = AuthenticationForm()

    context = {
        'form': form,
    }
    return render(request, 'accounts/login.html', context)


def sign_up(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()

            # Log-in the user right away, then redirect home
            messages.success(request, 'Account created successfully. Welcome!')
            login(request, user)
            return redirect('home')
    else:
        form = SignupForm()

    context = {
        'form': form,
    }
    return render(request, 'accounts/signup.html', context)


def logout_view(request):
    logout(request)
    messages.success(request, 'Logged out.')
    return redirect('home')


def view_all_users(request):
    all_users = User.objects.all()
    context = {
        'users': all_users,
    }
    return render(request, 'accounts/view_all_users.html', context)


def view_profile(request, username):
    user = User.objects.get(username=username)

    if request.user == user:
        is_viewing_self = True
    else:
        is_viewing_self = False
    panels = DashBoardPanel.objects.filter(user=user)
    context = {
        'user': user,
        'is_viewing_self': is_viewing_self,
        'panels': panels,
    }
    return render(request, 'accounts/profile_page.html', context)


@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = UserEditForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = UserEditForm(instance=request.user)

    context = {
        'form': form,
    }
    return render(request, 'accounts/edit_profile.html', context)

@login_required
def favorites_list(request, username):
    user = User.objects.get(username=username)
    favorite_games = FavoriteGame.objects.filter(favorites=user)
    favorite_game_titles = request.user.favorite.all().values_list('title', flat=True)

    context = {
        'user': user,
        'favorite_games': favorite_games,
        'my_favorite_games': favorite_game_titles,

    }
    return render(request, 'accounts/favorite_games.html', context)


