from django.http import JsonResponse
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from .models import Artist, Song, UserSongRating, SongArtist
from .serializers import SongSerializer, ArtistSerializer
from .utilities import *
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.parsers import  MultiPartParser, FormParser

class Register(APIView):

    def post(self, request):

        name, email, password, isArtist = request.data["name"], request.data["email"], request.data["password"], request.data["isArtist"]

        if isArtist:

            dob, bio = request.data["dob"], request.data["bio"]
            # create user object
            try:
                user = User.objects.get(email=email) # check if user record exists already
            except:
                user = User.objects.create_user(first_name=name, username=email, email=email, password=password)
            return ArtistView.post(self, request, user, dob, bio) # create artist object

        else:

            try:

                user = User.objects.get(email=email)
                return Response("User with this email-id already exists", status=status.HTTP_409_CONFLICT)

            except:

                user = User.objects.create_user(first_name=name, username=email, email=email, password=password)
                user.save()

            return Response("User created successfully", status=status.HTTP_201_CREATED)

class Login(APIView):

    def post(self, request):

        email, password, isArtist  = request.data["email"], request.data["password"], request.data["isArtist"]

        if isArtist:

            try:
                user = authenticate(username=email, password=password)
                if user:

                    try:
                        artist = Artist.objects.get(user=user)
                        return Response("Artist login successful", status=status.HTTP_200_OK)

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


class ArtistView(APIView):

    def get(self, request):
        try:
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
        except:
            return Response(data="Something went wrong", status = status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request, user, dob, bio):

        try:
            artist = Artist.objects.get(user=user)
            return Response("Artist with this email-id already exists", status=status.HTTP_409_CONFLICT)

        except:
            artist = Artist.objects.create(user=user,name=user.first_name, dob=dob, bio=bio)

        return Response("Artist created successfully", status=status.HTTP_201_CREATED)


class ArtistAllSongs(APIView):

    def get(self, request):

        try:
            email = request.GET["email"]

            try:
                artist = Artist.objects.get(user=User.objects.get(email=email))
                songs_by_current_artist = SongArtist.objects.filter(artists__id=artist.id)
            except:
                songs_by_current_artist= []

            songs=[]
            for song in songs_by_current_artist:
                songs.append(song.song)
            serializer = SongSerializer(songs, many=True)
            return Response(data=serializer.data, status=status.HTTP_200_OK)

        except:
            return Response(data="Something went wrong", status = status.HTTP_500_INTERNAL_SERVER_ERROR)


class SongView(APIView):


    parser_classes = (MultiPartParser, FormParser)
    def post(self, request):
        try:
            song_serializer = SongSerializer(data=request.data)
            if song_serializer.is_valid():
                song_serializer.save()
                song_id = song_serializer.data["id"]
                email = request.headers["email"]

                current_artist = Artist.objects.get(user=User.objects.get(email=email))
                test_song_artist_object = SongArtist.objects.create(song=Song.objects.get(id=song_id))
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
        except:
            return Response(data="Something went wrong", status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class TopSongs(APIView):
    def get(self, request):
        try:
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

        except:
            return Response(data="Something went wrong", status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class TopArtists(APIView):

    def get(self, request):
        try:
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

        except:
                return Response(data="Something went wrong", status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UserSongRatingView(APIView):

    def post(self, request):
        try:
            try:
                user_song_obj = UserSongRating.objects.get(song=Song.objects.get(id=request.data["id"]),
                                                            user=User.objects.get(email=request.data["email"]))
                user_song_obj.rating = request.data["rating"]
                user_song_obj.save()

                return JsonResponse("User rating updated successfully", safe=False)
            except:
                try:
                    user_song_obj = UserSongRating.objects.create(song=Song.objects.get(id=request.data["id"]),
                                                            user=User.objects.get(email=request.data["email"]),
                                                            rating=request.data["rating"])
                    return JsonResponse("User rating created successfully", safe=False)

                except:
                    return Response("Record already exists", status=status.HTTP_409_CONFLICT)

        except:
            return Response(data="Something went wrong", status=status.HTTP_500_INTERNAL_SERVER_ERROR)
