from django.contrib import admin
from .models import Artist, Song, UserSongRating, TestSongArtist

admin.site.register(Artist)
admin.site.register(Song)
admin.site.register(TestSongArtist)
admin.site.register(UserSongRating)
