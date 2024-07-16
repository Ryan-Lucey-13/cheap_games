import requests
import pygal
import re
import datetime
from django.shortcuts import render
from django.shortcuts import redirect
from django.shortcuts import get_object_or_404
from django import forms
from django.views.decorators.http import require_POST

from .models import DashBoardPanel
from .models import FavoriteGame
# Two example views. Change or delete as necessary

class NewPanelForm(forms.ModelForm):
    class Meta:
        model = DashBoardPanel
        fields = [
            'game_title',
            'max_game_price',
            'panel_type',
            'description',
            'panel_size',
        ]
class EditPanelForm(forms.ModelForm):
    class Meta:
        model = DashBoardPanel
        fields = [
            'game_title',
            'max_game_price',
            'description',
            'panel_size',
        ]
class AddFavoriteForm(forms.ModelForm):
    class Meta:
        model = FavoriteGame
        fields = [
            'title',
            'image',
            'release_date',
            'sale_price',
            'normal_price',
            'steam_rating',
            'deal_rating',
        ]


def dashboard(request):
    panels = DashBoardPanel.objects.all()
    context = {
        "panels": panels,
    }
    return render(request, "pages/dashboard.html", context)

def game_info(request):
    if "searchterm" in request.GET: 
        search_query = request.GET['searchterm']
        search_price = request.GET['price']
        response = requests.get(f'https://www.cheapshark.com/api/1.0/deals?storeID=1&upperPrice={search_price}&title={search_query}')
    else:
        search_query = None
        response = requests.get('https://www.cheapshark.com/api/1.0/deals?storeID=1&upperPrice=25')
    
    games_data = response.json()
        
    results_list = games_data
    
    if request.user.is_authenticated:
        favorite_game_titles = request.user.favorite.all().values_list('title', flat=True)
    else:
        favorite_game_titles = []
    context = {
        'games_results': results_list,
        'search_term': search_query,
        'my_favorite_games': favorite_game_titles
    }

    return render(request,'pages/table.html', context)

def game_discount(request):
    if "searchterm" in request.GET:
        search_query = request.GET['searchterm']
        search_price = request.GET['price']
        response = requests.get(f'https://www.cheapshark.com/api/1.0/deals?storeID=1&pageSize=15&upperPrice={search_price}&title={search_query}')
    else:
        search_query = None
        response = requests.get('https://www.cheapshark.com/api/1.0/deals?storeID=1&pageSize=15&upperPrice=25')
    games_data = response.json()
    
    bar_chart = pygal.HorizontalBar()
    bar_chart.title = "Savings Breakdown Per Game"
    for game in games_data:
        value = game['salePrice']
        label = game['title']
        bar_chart.add(label, float(value))
   
    chart_svg = bar_chart.render_data_uri()
    
    context = {
        'rendered_chart_svg': chart_svg
    }

    return render(request,'pages/pricing.html', context)

def game_ratings(request):
    if "searchterm" in request.GET:
        search_query = request.GET['searchterm']
        response = requests.get(f'https://www.cheapshark.com/api/1.0/deals?storeID=1&upperPrice=25&title={search_query}&exact=1')
    else:
        search_query = None
        response = requests.get('https://www.cheapshark.com/api/1.0/deals?storeID=1&upperPrice=25')
    games_data = response.json()
    
    for game in games_data:
        if game['title'] == search_query:
            label = game['title']
            meta_rating = game['metacriticScore']
            steam_rating = game['steamRatingPercent']
            deal_rating = game['dealRating']
            adj_deal_rating = float(deal_rating) * 10
        else:
            label = None
            meta_rating = 0
            steam_rating = 0
            adj_deal_rating = 0
    
    bar_chart = pygal.Bar(range=(0, 100))
    bar_chart.title = 'Game Ratings (out of 100)'
    bar_chart.x_labels = 'MetaCritic Rating', 'Steam Rating', 'Deal Rating'
    bar_chart.add(label, [float(meta_rating), float(steam_rating), adj_deal_rating])
    chart_svg = bar_chart.render_data_uri()
    
    context = {
        'rendered_chart_svg': chart_svg
    }

    return render(request,'pages/ratings.html', context)

def create_panel(request):
    if request.method == 'POST':
        form = NewPanelForm(request.POST)
        
        if form.is_valid():
            panel = form.save(commit=False)
            panel.user = request.user
            panel.save()
            return redirect('/dashboard')
    else:
        form = NewPanelForm()
    
    context = {
        'form': form,
    }
    return render(request, 'pages/new_panel.html', context)

def delete_panel(request, panel_id):
    panel = DashBoardPanel.objects.get(id=panel_id)
    panel.delete()
    return redirect('/dashboard')

def update_panel(request, panel_id):
    panel_being_edited = DashBoardPanel.objects.get(id=panel_id)

    if request.method == 'POST':
        form = EditPanelForm(request.POST, instance=panel_being_edited)
        if form.is_valid():
            form.save()
            return redirect('/dashboard')

    else:
        initial_panel_data = {
            'game_title': panel_being_edited.game_title,
            'max_game_price': panel_being_edited.max_game_price,
            'description': panel_being_edited.description,
            'panel_size': panel_being_edited.panel_size,
        }
        form = EditPanelForm(initial=initial_panel_data)

    context = {
        'form': form,
    }

    return render(request, 'pages/update_panel.html', context)

@require_POST
def favorite_game_create(request):
    title = request.POST['title']
    sale_price = request.POST['sale_price']
    try:
        game = FavoriteGame.objects.get(title=title)
        if game.sale_price != sale_price:
            game.sale_price = sale_price
            game.save()
    except FavoriteGame.DoesNotExist:
        image = request.POST['image']
        release_date = request.POST['release_date']
        normal_price = request.POST['normal_price']
        steam_rating = request.POST['steam_rating']
        deal_rating = request.POST['deal_rating']
    
        game = FavoriteGame.objects.create(   
            title=title,
            image=image,
            release_date=release_date,
            sale_price=sale_price,
            normal_price=normal_price,
            steam_rating=steam_rating,
            deal_rating=deal_rating
            )
    if request.user.is_authenticated:
        game.favorites.add(request.user)

    return redirect(request.META.get('HTTP_REFERER', '/'))

def favorite_game_delete(request, favorite_game_title):
    favorite_game =  get_object_or_404(FavoriteGame, title=favorite_game_title)
    
    if request.user.is_authenticated:
        favorite_game.favorites.remove(request.user)

    if request.POST.get("redirect"):
            return redirect(request.POST.get('redirect'))

    return redirect('/')
