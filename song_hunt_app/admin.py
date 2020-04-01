from django.contrib import admin
from .models import Artist, Song, UserSongRating, SongArtist

admin.site.register(Artist)
admin.site.register(Song)
admin.site.register(SongArtist)
admin.site.register(UserSongRating)
