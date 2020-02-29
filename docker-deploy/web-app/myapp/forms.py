"""
Griffin last modified on 02/6/2020
"""
from django import forms
from django.contrib.auth.forms import (
    UserCreationForm,
    UserChangeForm,
    PasswordChangeForm
)
from .models import MyUser, Ride, VehicleInfo
# from datetimewidget.widgets import DateTimeWidget
from django.contrib.auth import models
from django.utils import timezone
from django.forms import ModelForm
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from tempus_dominus.widgets import DateTimePicker



""" 
Ying last modified on 01/31/2020 
Functionality: Collect user registration information, email & username
"""
class MyUserRegisterForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = MyUser
        model.is_driver = False
        fields = ("username", "email", "first_name", "last_name")

    def save(self, commit=True):
        user = super(MyUserRegisterForm, self).save(commit=False)
        user.username = self.cleaned_data["username"]
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user


""" 
Ying last modified on 02/02/2020 
Functionality: To EDIT user profile, personal info
"""
class MyUserChangeForm(UserChangeForm):
    class Meta:
        model = MyUser
        fields = ("username", "email", "password", "first_name", "last_name", "is_driver")


""" 
Ying last modified on 02/01/2020 
Functionality: Collect driver and vehicle info
"""
class DriverRegisterForm(ModelForm):
    class Meta:
        model = VehicleInfo
        exclude = ('driver', )


""" 
Ying last modified on 02/02/2020 
Functionality: Edit vehicle info
"""
class DriverChangeForm(ModelForm):
    class Meta:
        model = VehicleInfo
        exclude = ('driver', )
    
    def clean(self):
        cleaned_data = super(DriverChangeForm, self).clean()
        plate_number = cleaned_data["plate_number"]
        
        if(VehicleInfo.objects.filter(plate_number__exact = plate_number)):
            raise forms.ValidationError("Plate number already taken.")

""" 
Griffin last modified on 02/02/2020 
Functionality: Collect ride info, for owner to make a new request
"""
class RideRequestForm(ModelForm):
    class Meta:
        model = Ride
        model.status = 'Open'
        exclude = ('owner', 'driver', 'sharer', 'sharer_passengers', 'ride_id', 'status',
                   'plate_number', 'vehicle_capacity',)
        widgets = {
            'arrive_time' : DateTimePicker(
                options={
                    'collapse':False,
                    'minDate': 'now',
                }
            )
        }

    # def clean_arrive_time(self):
    #     arrive_time = self.cleaned_data['arrive_time']
    #     if arrive_time < datetime.data.now():
    #         raise ValidationError(_('Invalid Arrive Time'))
    #     return arrive_time


"""
Griffin added on 02/06/2020
OwnRideEdit
"""
class OwnRideEditForm(ModelForm):

    class Meta:
        model = Ride
        exclude = ('owner', 'driver', 'sharer', 'sharer_passengers', 'ride_id', 'status',
                   'plate_number', 'vehicle_capacity',)
        widgets = {
            'arrive_time' : DateTimePicker(
                options={
                    'collapse':False,
                    'minDate': 'now',
                }
            )
        }


    # def clean_arrive_time(self):
    #     arrive_time = self.cleaned_data['arrive_time']
    #     if arrive_time < datetime.data.now():
    #         raise ValidationError(_('Invalid Arrive Time'))
    #     return arrive_time


""" 
Griffin last modified on 02/06/2020 
Functionality: Collect search info, for sharer to search available ride to join
"""


class RideShareForm(forms.Form):
    dst_addr = forms.CharField(label="Destination", required=True)
    earliest_arrival = forms.DateTimeField(label="Earlist Arrival", required=True,
        widget=DateTimePicker(options={'collapse':False,'minDate': 'now','defaultDate': 'now'}))
    latest_arrival = forms.DateTimeField(label="Latest Arrival", required=True,
        widget=DateTimePicker(options={'collapse':False,'minDate': 'now','defaultDate': 'now'}))
    passenger_num = forms.IntegerField(label="Passenger Number", required=True, min_value=1, initial=1)
