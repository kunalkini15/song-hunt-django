from django.contrib import admin
from .models import Artist, Song, SongArtist, UserSongRating

admin.site.register(Artist)
admin.site.register(Song)
admin.site.register(SongArtist)
admin.site.register(UserSongRating)
