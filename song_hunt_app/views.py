from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.files.storage import default_storage

from .models import Artist, Song, UserSongRating, TestSongArtist
from .serializers import SongSerializer
from .utilities import *
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import JSONParser,  MultiPartParser, FormParser

class Register(APIView):
    def post(self, request):
        name = request.data["name"]
        email = request.data["email"]
        password = request.data["password"]
        isArtist = request.data["isArtist"]
        if isArtist:
            dob = request.data["dob"]
            bio = request.data["bio"]
            try:
                user = User.objects.get(email=email)
                artist = Artist.objects.filter(user=user)
                return Response("User already exists", status=status.HTTP_409_CONFLICT)
            except:
                try:
                    user = User.objects.get(email=email)
                    artist = Artist.objects.create(user=user,name=name, dob=dob, bio=bio)
                    artist.save()
                    return Response("User created successfully", status=status.HTTP_201_CREATED)
                except:
                    user = User.objects.create_user(first_name=name, username=email, email=email, password=password)
                    user.save()
                    artist = Artist.objects.create(user=user,name=name, dob=dob, bio=bio)
                    artist.save()
            return Response("User created successfully", status=status.HTTP_201_CREATED)
        else:
            try:
                user = User.objects.get(email=email)
                return Response("User already exists", status=status.HTTP_409_CONFLICT)
            except:
                user = User.objects.create_user(first_name=name, username=email, email=email, password=password)
                user.save()
            return Response("User created successfully", status=status.HTTP_201_CREATED)

class Login(APIView):
    def post(self, request):
        email = request.data["email"]
        password = request.data["password"]
        isArtist = request.data["isArtist"]
        if isArtist:
            try:
                user = authenticate(username=email, password=password)
                if user:
                    login(request, user)
                    try:
                        user_obj = User.objects.get(email=email)
                        artist = Artist.objects.get(user=user_obj)
                        return Response("User Logged in successfully", status=status.HTTP_200_OK)
                    except:
                        return Response("You haven't created an artist account", status=status.HTTP_401_UNAUTHORIZED)

                else:
                    return Response("Wrong password", status=status.HTTP_401_UNAUTHORIZED)
            except:
                return Response("User doesn't exist", status=status.HTTP_404_NOT_FOUND)
        else:
            try:
                user = authenticate(username=email, password=password)
                if user:
                    login(request, user)
                    return Response("User Logged in successfully", status=status.HTTP_200_OK)
                else:
                    return Response("Wrong password", status=status.HTTP_401_UNAUTHORIZED)
            except:
                return Response("User doesn't exist", status=status.HTTP_404_NOT_FOUND)

class Test(APIView):
    def get(self, request):
        try:
            return JsonResponse(request.headers["id"], safe=False)
        except:
            return JsonResponse("Can't fetch", safe=False)

class ArtistView(APIView):
    def get(self, request):
        if request.GET["bulk"] == True or request.GET["bulk"] == "true":
            # return list of all artists, used in dropdown.
            email = request.GET["email"]

            artists = Artist.objects.all()
            response = []
            for artist in artists:
                artist_obj = {
                    'id': artist.id,
                    'name': artist.name,
                    'dob': artist.dob,
                    'bio':artist.bio
                }
                response.append(artist_obj)


            return JsonResponse(response, safe=False)
        else:
            email = request.GET["email"]
            user = User.objects.get(email=email)
            artist = Artist.objects.get(user=user)
            response = {
                'name': artist.name,
                'dob': artist.dob,
                'bio':artist.bio
            }

            return JsonResponse(response)

class ArtistAllSongs(APIView):
    def get(self, request):
        email = request.GET["email"]
        try:
            artist = Artist.objects.get(user=User.objects.get(email=email))
            songs_by_current_artist = TestSongArtist.objects.filter(artists__id=artist.id)
        except:
            songs_by_current_artist= []
        songs=[]
        for song in songs_by_current_artist:
            songs.append(song.song)
        serializer = SongSerializer(songs, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

class SongView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    def post(self, request):
        song_serializer = SongSerializer(data=request.data)
        if song_serializer.is_valid():
            song_serializer.save()
            song_id = song_serializer.data["id"]
            email = request.headers["email"]

            current_artist = Artist.objects.get(user=User.objects.get(email=email))
            test_song_artist_object = TestSongArtist.objects.create(song=Song.objects.get(id=song_id))
            test_song_artist_object.save()

            test_song_artist_object.artists.add(current_artist)
            try:
                artists = [int(i) for i in request.data["selectedArtists"].split(",")]
            except:
                artists = []
            for id in artists:
                if id != current_artist.id:
                    test_song_artist_object.artists.add(Artist.objects.get(id=id))
            test_song_artist_object.save()
            return Response(song_serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(song_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TopSongs(APIView):
    def get(self, request): # get will always return songs ordered_by average_rating, it can be filtered to top 10 in frontend
        response = []
        email = request.GET["email"]
        songs = Song.objects.all()
        for song in songs:
            current_obj = {
                'song': getSongObj(song),
                'artists': getArtists(song),
                'rating': getRatingDetails(song),
                'user_rating': getUserRating(song, email)
            }
            response.append(current_obj)
        response = sorted(response, key=lambda x: x["rating"]["rating__avg"], reverse=True)

        return Response(data=response, status=status.HTTP_200_OK)

class TopArtists(APIView):
    def get(self, request):
        artists = Artist.objects.all()
        response = []
        for artist in artists:
            current_obj = {
                'artist': getArtistObj(artist),
                'songDetails': getSongDetails(artist)
            }
            response.append(current_obj)

        response = sorted(response, key=lambda x:x["songDetails"]["rating"], reverse=True)
        return Response(data=response, status=status.HTTP_200_OK)


class UserSongRatingView(APIView):
    def post(self, request):
        try:
            user_song_obj = UserSongRating.objects.get(song=Song.objects.get(id=request.data["id"]),
                                                        user=User.objects.get(email=request.data["email"]))

            user_song_obj.rating = request.data["rating"]
            user_song_obj.save()
        except:
            try:
                user_song_obj = UserSongRating.objects.create(song=Song.objects.get(id=request.data["id"]),
                                                        user=User.objects.get(email=request.data["email"]),
                                                        rating=request.data["rating"])
            except:
                return Response("Record already exists", status=status.HTTP_409_CONFLICT)

        return JsonResponse("Done", safe=False)
