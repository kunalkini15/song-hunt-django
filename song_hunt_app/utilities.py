from .models import Song, Artist, UserSongRating, SongArtist
from django.contrib.auth.models import User
from django.db.models import Avg, Count
from .serializers import SongSerializer, ArtistSerializer
def getArtists(song):


    test_song_artist_object = SongArtist.objects.filter(song=song)
    artists = []
    for i in test_song_artist_object:
        artist_objects = i.artists.all()
        for artist in artist_objects:
            current_obj={
                "id": artist.id,
                "name": artist.name
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
    songs_by_current_artist = SongArtist.objects.filter(artists__id=artist.id)
    songs = []
    ratings =[]
    for song in songs_by_current_artist:
        songs.append(getSongObj(song.song))
        ratings.append(getRatingDetails(song.song)["rating__avg"])
    if len(ratings) == 0:
        rating = 0
    else:
        rating = sum(ratings) / len(ratings)
    return {
        'songs': songs,
        'rating': rating
    }
