from django.contrib.auth.models import User
from django.db import models

# Create your models here.

class HotelStatus(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name

class Hotel(models.Model):
    name = models.CharField(max_length=200)
    stars = models.IntegerField()
    location = models.CharField(max_length=200)
    phone = models.CharField(max_length=30)
    email = models.CharField(max_length=200)
    city = models.CharField(max_length=200)
    to_center = models.FloatField()
    about = models.TextField()
    status = models.ForeignKey(HotelStatus,on_delete=models.CASCADE)
    user = models.ForeignKey(User,on_delete=models.CASCADE)

    @property
    def primary_photo(self):
        return self.files_set.filter(is_primary=True).first()
    def not_primary_photo(self):
        return self.files_set.filter(is_primary=False).first()

    def __str__(self):
        return self.name


class Comfort(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name

class Hotel_Comfort(models.Model):
    hotel = models.ForeignKey(Hotel,on_delete=models.CASCADE)
    comfort = models.ForeignKey(Comfort,on_delete=models.CASCADE)

    def __str__(self):
        return self.hotel.name

class Hotel_Room(models.Model):
    hotel = models.ForeignKey(Hotel,on_delete=models.CASCADE)
    description = models.TextField()
    name = models.CharField(max_length=200)
    max_people = models.IntegerField()
    rooms= models.IntegerField()
    price = models.IntegerField()
    free_count = models.IntegerField()

    @property
    def primary_photo(self):
        return self.files_set.filter(is_primary=True).first()
    def not_primary_photo(self):
        return self.files_set.filter(is_primary=False).first()

    def __str__(self):
        return self.name

class Review(models.Model):
    text = models.TextField()
    hotel = models.ForeignKey(Hotel,on_delete=models.CASCADE)
    room = models.ForeignKey(Hotel_Room,on_delete=models.CASCADE)
    stars = models.IntegerField()

    def __str__(self):
        return self.text

class BookingHistory(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    hotel = models.ForeignKey(Hotel,on_delete=models.CASCADE)
    room = models.ForeignKey(Hotel_Room,on_delete=models.CASCADE)
    datefrom = models.DateField()
    dateto = models.DateField()
    price = models.IntegerField()
    people = models.IntegerField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.hotel.name


class BookingFavorites(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    hotel = models.ForeignKey(Hotel,on_delete=models.CASCADE)
    room = models.ForeignKey(Hotel_Room,on_delete=models.CASCADE)

    def __str__(self):
        return self.hotel.name

class Files(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    hotel = models.ForeignKey(Hotel,on_delete=models.CASCADE)
    room = models.ForeignKey(Hotel_Room,on_delete=models.CASCADE, null=True)
    file = models.FileField(upload_to='files')
    is_primary = models.BooleanField(default=False)  # Для установки основного фото
    description = models.CharField(max_length=255, blank=True, null=True)

class Bookings(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    surname = models.CharField(max_length=200)
    idoc_series = models.IntegerField()
    idoc_number = models.IntegerField()
    people = models.IntegerField()
    hotel = models.ForeignKey(Hotel,on_delete=models.CASCADE)
    room = models.ForeignKey(Hotel_Room,on_delete=models.CASCADE)
    datefrom = models.DateField()
    dateto = models.DateField()