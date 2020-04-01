from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator

class Artist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=50)
    dob = models.DateField()
    bio = models.TextField(null=True)

    def __str__(self):
        return self.name

class Song(models.Model):
    name = models.CharField(max_length=50)
    release_date = models.DateField()
    image = models.ImageField(null=True, upload_to='song_artworks', blank=True)

    def __str__(self):
        return self.name


class SongArtist(models.Model):
    song = models.ForeignKey('Song', on_delete=models.CASCADE)
    artists = models.ManyToManyField('Artist')

    def __str__(self):
        return self.song.name +  " - " + str(self.id)

class UserSongRating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    song = models.ForeignKey('Song', on_delete=models.CASCADE)
    rating = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(5)], default=0)

    class Meta:
        unique_together = ('user','song','rating')
    def __str__(self):
        return self.user.first_name + " - " + self.song.name
