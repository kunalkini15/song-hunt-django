from .models import Song, Artist, SongArtist, UserSongRating
from django.contrib.auth.models import User
from django.db.models import Avg, Count
from .serializers import SongSerializer, ArtistSerializer
def getArtists(song):
    song_artist_objects = SongArtist.objects.filter(song=song)
    artists = []
    for song_artist in song_artist_objects:
        current_obj = {
            "id": song_artist.artist.id,
            "name": song_artist.artist.name
        }
        artists.append(current_obj)
    return artists

def getRatingDetails(song):
    rating_details = UserSongRating.objects.filter(song=song).aggregate(Avg('rating'), Count('rating'))
    if rating_details['rating__avg'] == None:
        rating_details['rating__avg'] = 0

    return rating_details



def getSongObj(song):
    serializer = SongSerializer(song, many= False)
    return serializer.data

def getUserRating(song, email):
    try:
        user_rating_obj = UserSongRating.objects.filter(song=song, user=User.objects.get(email=email))[0]
        return user_rating_obj.rating
    except:
        return -1


def getArtistObj(artist):
    serializer = ArtistSerializer(artist, many=False)
    return serializer.data

def getSongDetails(artist):
    song_artists = SongArtist.objects.filter(artist=artist)
    songs = []
    ratings =[]
    for song_artist in song_artists:
        songs.append(getSongObj(song_artist.song))
        ratings.append(getRatingDetails(song_artist.song)["rating__avg"])
    return {
        'songs': songs,
        'rating': sum(ratings)/len(ratings)
    }
