import requests
import pygal
import datetime
from django.db import models

# Create your models here.
class DashBoardPanel(models.Model):
    game_title = models.CharField(max_length=127)
    max_game_price = models.FloatField()
    panel_type = models.CharField(max_length=127, choices=[
        ("table", "Table of Games Found in Search"),
        ("horizontal-bar chart", "Bar-Chart of Discounts"),
        ("vertical-bar chart", "Bar-Chart of Game Ratings")
        ])
    description = models.CharField(max_length=255, blank=True)
    panel_size = models.CharField(max_length=127, default="medium", choices=[
        ("small", "Small"),
        ("medium", "Medium"),
        ("large", "Large")
        ])
    user = models.ForeignKey(
       "accounts.User",
       on_delete=models.CASCADE, 
    )
    created = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)

    def get_table_data(self):
        search_game = self.game_title
        search_price = self.max_game_price
        response = requests.get(f'https://www.cheapshark.com/api/1.0/deals?storeID=1&upperPrice={search_price}&title={search_game}')

        games_data = response.json()
        for game in games_data:
            timestamp = game.get('releaseDate')
            if timestamp == 0:
                game['releaseDate'] = "N/A"
            elif timestamp:
                dt_object = datetime.datetime.utcfromtimestamp(timestamp)
                game['releaseDate'] = dt_object.strftime('%m-%d-%Y')

        return games_data

    def get_horizontal_bar_chart(self):
        search_game = self.game_title
        search_price = self.max_game_price
        response = requests.get(f'https://www.cheapshark.com/api/1.0/deals?storeID=1&pageSize=15&upperPrice={search_price}&title={search_game}')

        games_data = response.json()

        bar_chart = pygal.HorizontalBar()
        bar_chart.title = "Savings Breakdown Per Game"
        games_data = response.json()
        for game in games_data:
            value = game['salePrice']
            label = game['title']
            bar_chart.add(label, float(value))

        return bar_chart.render_data_uri()

    def get_vertical_bar_chart(self):
        search_game = self.game_title
        search_price = self.max_game_price
        response = requests.get(f'https://www.cheapshark.com/api/1.0/deals?storeID=1&upperPrice={search_price}&title={search_game}&exact=1')

        games_data = response.json()

        for game in games_data:
            if game['title'] == search_game:
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
        return bar_chart.render_data_uri()

class FavoriteGame(models.Model):
    favorites = models.ManyToManyField("accounts.User", related_name="favorite", blank=True)
    title = models.CharField(max_length=255)
    image = models.URLField()
    release_date = models.IntegerField()
    sale_price = models.DecimalField(max_digits=10, decimal_places=2)
    normal_price = models.DecimalField(max_digits=10, decimal_places=2)
    steam_rating = models.IntegerField()
    deal_rating = models.FloatField(default=0)
    user = models.ForeignKey(
       "accounts.User",
       on_delete=models.CASCADE, 
    )

    def get_table_data(self):
        search_game = self.game_title
        search_price = self.max_game_price
        response = requests.get(f'https://www.cheapshark.com/api/1.0/deals?storeID=1&upperPrice={search_price}&title={search_game}')

        games_data = response.json()
        for game in games_data:
            timestamp = game.get('releaseDate')
            if timestamp == 0:
                game['releaseDate'] = "N/A"
            elif timestamp:
                dt_object = datetime.datetime.utcfromtimestamp(timestamp)
                game['releaseDate'] = dt_object.strftime('%m-%d-%Y')

        return games_data

