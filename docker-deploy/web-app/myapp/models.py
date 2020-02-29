"""
Ying last modified on 02/02/2020
"""

from django.db import models
import uuid
from django.contrib.auth.models import User
from django.db.models import F

class MyUser(User):
    # uid = models.UUIDField(primary_key=True, default=uuid.uuid4, help_text='Unique ID for this user')
    # first_name = models.CharField(max_length=200)
    # last_name = models.CharField(max_length=200)
    # email = models.EmailField(max_length=200)
    # username = models.CharField(max_length=200, help_text='Enter a username (e.g. yingxu1995)')
    # password = models.CharField(max_length=200, help_text='Enter a password no less than 8 digits')
    # All above included in User
    is_driver = models.BooleanField(default=False)


class VehicleInfo(models.Model):
    plate_number = models.CharField(primary_key=True, max_length=200)
    driver = models.OneToOneField(MyUser, on_delete=models.CASCADE)
    license_num = models.CharField(max_length=200)
    v_type = models.CharField(max_length=200)
    num_of_passengers = models.PositiveIntegerField(default=1)
    special_info = models.TextField(null=True, blank=True, max_length=200)


class Ride(models.Model):
    ride_id = models.UUIDField(primary_key=True, default=uuid.uuid4,
                               help_text='Unique ID for this particular ride accross whole rides')
    dst_addr = models.CharField(max_length=200)
    arrive_time = models.DateTimeField()
    special_request = models.TextField(max_length=200, null=True, blank=True)
    """Ying added 02/02/2020"""
    # v_type should be specified by owner, should not be blank
    v_type = models.CharField(max_length=200)
    # plate_num and v_capacity should be copied here after a driver confirmed it
    plate_number = models.CharField(null=True, blank=True, max_length=200)
    vehicle_capacity = models.PositiveIntegerField(default=1, null=True, blank=True)
    """End"""
    owner = models.ForeignKey(MyUser, on_delete=models.CASCADE, related_name='ride_owner')
    owner_passengers = models.PositiveIntegerField(default=1)
    sharable = models.BooleanField(default=False)
    sharer = models.ForeignKey(MyUser, on_delete=models.CASCADE, null=True, blank=True, related_name='ride_sharer')
    sharer_passengers = models.PositiveIntegerField(default=0)
    driver = models.ForeignKey(MyUser, on_delete=models.CASCADE, null=True, blank=True, related_name='ride_driver')

    LOAN_STATUS = (
        ('Open', 'Open'),
        ('Confirmed', 'Confirmed'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    )
    status = models.CharField(
        max_length=10,
        choices=LOAN_STATUS,
        blank=True,
        default='Open',
        help_text='Ride status',
    )

    def __str__(self):
        return str(self.ride_id)

