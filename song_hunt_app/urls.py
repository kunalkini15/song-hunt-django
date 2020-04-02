from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings
urlpatterns = [
    path('register/', views.Register.as_view(), name="register"),
    path('login/', views.Login.as_view(), name="login"),
    path('deleteAccount/', views.DeleteAccount.as_view(), name="deleteAccount"),
    path('artist/', views.ArtistView.as_view(), name="artist"),
    path('artistAllSongs/', views.ArtistAllSongs.as_view(), name="ArtistAllSongs"),
    path('song/', views.SongView.as_view(), name="song"),
    path('topSongs/', views.TopSongs.as_view(), name="topSongs"),
    path('userRating/', views.UserSongRatingView.as_view(), name="userRating"),
    path('topArtists/', views.TopArtists.as_view(), name="topArtists")
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
