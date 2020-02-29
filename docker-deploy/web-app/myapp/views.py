"""
Ying last modified on 02/03/2020
"""
from django.contrib.auth.tokens import default_token_generator
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render, redirect, reverse, resolve_url, get_object_or_404
from django.template.response import TemplateResponse
from django.views import generic
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import permission_required, login_required
from .forms import MyUserRegisterForm, DriverRegisterForm, DriverChangeForm, MyUserChangeForm
from .forms import RideRequestForm, RideShareForm, OwnRideEditForm
from .models import MyUser, VehicleInfo, Ride
from django.contrib import auth
from django.utils import timezone
from django.contrib import messages
from django.db.models import Q, F
from django.contrib.auth.forms import (
    PasswordChangeForm,
    PasswordResetForm
)

from django.core.mail import send_mail
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.contrib import messages

def login(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            # login the user
            user = form.get_user()
            auth.login(request, user)
            return redirect('/myapp/home/')
        else:
          return render(request, 'login.html', {'form': form})
    else:
        form = AuthenticationForm()
        return render(request, 'login.html', {'form': form})


""" 
Ying last modified on 01/31/2020 
Functionality: logout
"""


def logout(request):
    if request.method == 'POST':
        auth.logout(request)
    return render(request, 'logout.html')


""" 
Ying last modified on 01/31/2020 
Functionality: user registration
"""


def user_register(request):
    if request.method == 'POST':
        form = MyUserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth.login(request, user)
            return redirect('/myapp/home/')
    else:
        form = MyUserRegisterForm()
    return render(request, 'profile/user_register.html', {'form': form})


""" 
Ying last modified on 02/01/2020 
Functionality: driver registration
"""


def view_profile(request):
    my_user = MyUser.objects.get(pk=request.user.pk)
    username = my_user.username
    first_name = my_user.first_name
    last_name = my_user.last_name
    email = my_user.email
    is_driver = my_user.is_driver
    if is_driver:
        my_car = VehicleInfo.objects.get(driver=my_user)
    else:
        my_car = None
    context = {
        'username': username,
        'first_name': first_name,
        'last_name': last_name,
        'email': email,
        'is_driver': is_driver,
        'my_car': my_car,
    }
    return render(request, 'profile/view_profile.html', context=context)


""" 
Ying last modified on 02/01/2020 
Functionality: driver registration
"""


def edit_profile(request):
    if request.method == 'POST':
        form = MyUserChangeForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('/myapp/profile/')
    else:
        form = MyUserChangeForm(instance=request.user)
    return render(request, 'profile/edit_profile.html', {"form": form})


"""
Ying modified on 02/03/2020
Functionality: for login user to change their password
"""
@login_required()
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated!')
            return redirect('/myapp/profile/')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'profile/change_password.html', {'form': form})


"""
Ying modified on 02/03/2020
password reset
Do not work, not a requirement, so stop here.
"""


def reset_password(request, is_admin_site=False,
                   template_name='registration/password_reset_form.html',
                   email_template_name='registration/password_reset_email.html',
                   subject_template_name='registration/password_reset_subject.txt',
                   password_reset_form=PasswordResetForm,
                   token_generator=default_token_generator,
                   post_reset_redirect=None,
                   from_email=None,
                   current_app=None,
                   extra_context=None):
    if post_reset_redirect is None:
        post_reset_redirect = 'registration/password_reset_done.html'
    else:
        post_reset_redirect = resolve_url(post_reset_redirect)
    if request.method == "POST":
        form = password_reset_form(request.POST)
        if form.is_valid():
            opts = {
                'use_https': request.is_secure(),
                'token_generator': token_generator,
                'from_email': from_email,
                'email_template_name': email_template_name,
                'subject_template_name': subject_template_name,
                'request': request,
            }
            if is_admin_site:
                opts = dict(opts, domain_override=request.get_host())
            form.save(**opts)
            return HttpResponseRedirect(post_reset_redirect)
    else:
        form = password_reset_form()
    context = {
        'form': form,
    }
    if extra_context is not None:
        context.update(extra_context)
    return TemplateResponse(request, template_name, context)


""" 
Ying last modified on 02/01/2020 
Functionality: driver registration
"""


@login_required()
def driver_register(request):
    user = request.user
    my_driver = MyUser.objects.get(pk=user.pk)

    if my_driver.is_driver:
        return redirect('/myapp/profile/')

    if request.method == 'POST':
        form = DriverRegisterForm(data=request.POST)
        if form.is_valid():
            # save the car info
            vehicle = form.save(commit=False)
            vehicle.driver = my_driver
            vehicle.save()
            my_driver.is_driver = True
            my_driver.save()
            return redirect('/myapp/profile/')
    else:
        form = DriverRegisterForm()
    return render(request, 'profile/driver_register.html', {'form': form})


""" 
Ying last modified on 02/01/2020 
Functionality: edit a vehicle info as a driver
"""


@login_required()
def edit_vehicle(request):
    my_user = MyUser.objects.get(pk=request.user.pk)
    vehicle = VehicleInfo.objects.get(driver=my_user)

    form = DriverChangeForm(request.POST or None, instance=vehicle)
    if form.is_valid():
        VehicleInfo.objects.get(driver=my_user).delete()
        form.save(commit=False)
        form.my_driver = my_user
        form.save()
        return redirect('/myapp/profile/')
    return render(request, 'profile/edit_vehicle.html', {"form": form})


""" 
Ying last modified on 02/01/2020 
Functionality: Home page. Redirect to home page after login
"""


def home(request):
    my_name = MyUser.objects.get(pk=request.user.pk)
    my_car = VehicleInfo.objects.filter(driver=request.user).count()
    num_sharer = Ride.objects.filter(sharer=request.user).count()
    num_driver = Ride.objects.filter(driver=request.user).count()
    num_orders = Ride.objects.filter(owner=request.user).count()

    context = {
        'my_name': my_name,
        'my_car': my_car,
        'num_sharer': num_sharer,
        'num_driver': num_driver,
        'num_orders': num_orders,
    }
    return render(request, 'home.html', context=context)


""" 
Ying last modified on 02/01/2020 
Functionality: request a new ride as a owner
"""


@login_required()
def request_ride(request):
    my_user = MyUser.objects.get(pk=request.user.pk)
    if request.method == 'POST':
        form = RideRequestForm(data=request.POST)
        if form.is_valid():
            ride = form.save(commit=False)
            ride.owner = my_user
            ride.save()
            return redirect('/myapp/home/')
    else:
        form = RideRequestForm()
    return render(request, 'owner_ride/make_request_ride.html', {'form': form})


""" 
Ying last modified on 02/01/2020 
Functionality: show all rides in which I was a owner/sharer
"""


class MyRequestListView(LoginRequiredMixin, generic.ListView):
    model = Ride
    template_name = 'show_all_rides_list.html'
    # paginate_by = 10
    context_object_name = 'ride_lists'

    def get_queryset(self):
        query_set = {'own_list': Ride.objects.filter(owner=self.request.user).order_by('arrive_time'),
                     'share_list': Ride.objects.filter(sharer=self.request.user).order_by('arrive_time'),
                     'driver_list': Ride.objects.filter(driver=self.request.user).order_by('arrive_time')}

        return query_set


"""
Ying added on 02/04/2020
Show request details, history, not waiting page.
"""


class MyRideDetailView(LoginRequiredMixin, generic.DetailView):
    model = Ride
    template_name = 'ride_details.html'
    context_object_name = 'ride'

    def ride_detail_view(request, pk):
        try:
            my_ride = get_object_or_404(Ride, pk=pk)
        except Ride.DoesNotExist:
            raise Http404("Ride does not exist.")

        return render(request, 'ride_details.html', context={'ride': my_ride})


"""
Ying last modified on 02/07/2020
Edit view for owner
Allow user to edit the ride info.
if owner changed the sharable, arrivetime, destination, remove all sharer data
renew owner info
"""


class OwnRideEditView(LoginRequiredMixin, generic.DetailView):
    model = Ride

    def own_ride_edit(request, pk):
        my_ride = get_object_or_404(Ride, pk=pk)
        old_dst = my_ride.dst_addr
        old_arrive_time = my_ride.arrive_time

        if request.method == 'POST':
            form = OwnRideEditForm(data=request.POST, instance=my_ride)
            if form.is_valid():
                if(my_ride.status == 'Open'):
                    #new_ride = Ride(dst_addr=form.cleaned_data['dst_addr'], arrive_time=form.cleaned_data['arrive_time'], \
                    #                special_request=form.cleaned_data['special_request'], v_type=form.cleaned_data['v_type'],\
                    #                owner=my_ride.owner, owner_passengers=form.cleaned_data['owner_passengers'])
                    #new_ride.save()
                    #my_ride.status = 'Cancelled'

                    if(my_ride.sharer != None):
                        message = "Hello user!\n" \
                        "The following ride has changed. As such you have been removed.\n" \
                        "ID : {}\n" \
                        "Destination : {}\n" \
                        "Arrival Time : {}\n" \
                        "Owner : {} {}\n" \
                        "Owner passengers : {}\n" \
                        .format(my_ride.ride_id, my_ride.dst_addr, my_ride.arrive_time, my_ride.owner.first_name, my_ride.owner.last_name, my_ride.owner_passengers)

                        message += "Sharer : {} {}\nSharer passengers : {}\n" \
                        .format(my_ride.sharer.first_name, my_ride.sharer.last_name, my_ride.sharer_passengers)
                        				        
                        message += "Vehicle type : {}\n" \
                        "Special Vehicle Info : {}\n".format(my_ride.v_type, my_ride.special_request)
                        send_mail('Ride cancelled!', message.format(my_ride.ride_id), settings.EMAIL_HOST_USER, [my_ride.sharer.email], fail_silently=False)

                    form.save()
                    my_ride.sharer_passengers = 0
                    my_ride.sharer = None
                    my_ride.save()

                    return render(request, 'ride_details.html', context={'ride': my_ride}) # Ying changed from new_ride to my_ride
                else:
                    messages.error(request, 'Ride cannot be edited (either confirmed or cancelled).')
                    raise PermissionDenied
            else:
                raise Http404('invalid form')

        else:
            form = OwnRideEditForm(instance=my_ride)
            return render(request, 'owner_ride/edit_own_ride.html', context={'form': form, 'ride': my_ride})


"""
Ying added on 02/04/2020
Cancel the ride
"""

@login_required()
def cancel_ride(request, pk):
    try:
        my_ride = get_object_or_404(Ride, pk=pk)
    except Ride.DoesNotExist:
        raise Http404("Ride does not exist.")

    if(my_ride.status == 'Open'):
        my_ride.status = 'Cancelled'
        my_ride.save()
        
        if(my_ride.sharer != None):
            message = "Hello user!\n" \
            "The following ride has been cancelled.\n" \
            "ID : {}\n" \
            "Destination : {}\n" \
            "Arrival Time : {}\n" \
            "Owner : {} {}\n" \
            "Owner passengers : {}\n" \
            .format(my_ride.ride_id, my_ride.dst_addr, my_ride.arrive_time, my_ride.owner.first_name, my_ride.owner.last_name, my_ride.owner_passengers)

            message += "Sharer : {} {}\nSharer passengers : {}\n" \
            .format(my_ride.sharer.first_name, my_ride.sharer.last_name, my_ride.sharer_passengers)

            message += "Vehicle type : {}\n" \
            "Special Vehicle Info : {}\n".format(my_ride.v_type, my_ride.special_request)
            send_mail('Ride cancelled!', message.format(my_ride.ride_id), settings.EMAIL_HOST_USER, [my_ride.sharer.email], fail_silently=False)

        return render(request, 'owner_ride/cancel_ride.html')
    else:
        messages.error('Ride cannot be cancelled (either confirmed or cancelled).')
        return PermissionDenied


""" 
Ying added on 02/05/2020 

Function Name: sharer_searh_ride
Functionality: display the RideShareForm to collect sharer's destination, arrival window, passenger number
"""


@login_required()
def share_search_ride(request):
    form = RideShareForm()
    return render(request, 'sharer_ride/make_share_ride.html', {'form': form})


""" 
Ying added on 02/05/2020 

Function Name: show_share_search_result
Functionality: 
1. get the form coming from make_share_ride.html and query available ride in db
2. Display the result of query
"""

@login_required()
def show_share_search_result(request):
    my_user = get_object_or_404(MyUser, pk=request.user.pk)
    if request.method == 'POST':
        form = RideShareForm(data=request.POST)
        if form.is_valid():
            dst_addr = form.cleaned_data['dst_addr']
            earliest_arvl = form.cleaned_data['earliest_arrival']
            latest_arvl = form.cleaned_data['latest_arrival']
            share_pass_num = form.cleaned_data['passenger_num']

            if latest_arvl < timezone.now() or earliest_arvl > latest_arvl:
                return render(request, 'sharer_ride/make_share_ride.html', {'form': form, 'is_valid': False})

            else:
                # for confirmed ride, have to check whether there's enough seats on the vehicle
                query = Q(status__exact="Open")
                query.add(Q(sharable__exact=True, dst_addr__exact=dst_addr, arrive_time__range=[earliest_arvl,latest_arvl]), Q.AND)
                ride_list = Ride.objects.filter(query).exclude(owner__exact=my_user).exclude(
                    driver__exact=my_user).exclude(sharer__exact=my_user).all()
                return render(request, 'sharer_ride/show_joinable_ride_list.html',
                              {'ride_list': ride_list, 'share_passengers': share_pass_num})

    return redirect('/myapp/profile/')


"""
Ying added on 02/06/2020
Allow sharer to join a ride
put sharer to ride.sharer,
set ride.sharer_passenger to sharer_passenger_num
"""

@login_required
def sharer_join_the_ride(request, pk, share_passengers):
    my_ride = get_object_or_404(Ride, pk=pk)
    if(my_ride.status == 'Open' and my_ride.sharer == None):
        my_user = MyUser.objects.get(pk=request.user.pk)
        my_ride.sharer = my_user
        my_ride.sharer_passengers = share_passengers
        my_ride.save()
        return render(request, 'sharer_ride/sharer_search_ride_details.html', {'ride': my_ride})
    else:
        messages.error(request, 'Ride cannot be joined (either confirmed or cancelled).')
        raise PermissionDenied


"""
Griffin added on 02/07/2020
"""

@login_required()
def sharer_ride_edit(request, pk):
    my_ride = get_object_or_404(Ride, pk=pk)
    if(my_ride.status == 'Open'):
        cur_dst = my_ride.dst_addr
        cur_arrive_time = my_ride.arrive_time
        cur_sharer_passengers = my_ride.sharer_passengers

        form = RideShareForm(initial={'dst_addr' : cur_dst, 'earliest_arrival' : cur_arrive_time,\
                                      'latest_arrival' : cur_arrive_time, 'passenger_num' : cur_sharer_passengers})
        my_ride.sharer = None
        my_ride.sharer_passengers = 0
        my_ride.save()
        return render(request, 'sharer_ride/make_share_ride.html', {'form' : form})
    else:
        messages.error('Ride cannot be edited (either confirmed or cancelled).')
        return PermissionDenied

@login_required()
def sharer_ride_cancel(request, pk):
    my_ride = get_object_or_404(Ride, pk=pk)
    if(my_ride.status == 'Open'):
        my_ride.sharer = None
        my_ride.sharer_passengers = 0
        my_ride.save()
        return HttpResponseRedirect(reverse('my_user_request'))
    else:
        messages.error('Ride  cannot be cancelled (either confirmed or cancelled).')
        return PermissionDenied

"""
Ying added on 02/05/2020
Allow sharer to see details of a joinable order
At this point, we show all details in the list and do not implement a link for sharer to check details separately
But in My Rides, sharer can step into sharer view if click link
"""

@login_required
class SharerRideDetailView(LoginRequiredMixin, generic.DetailView):
    model = Ride
    template_name = 'sharer_ride/sharer_search_ride_details.html'
    context_object_name = 'ride'

    def sharer_ride_detail_view(request, pk):
        try:
            my_ride = get_object_or_404(Ride, pk=pk)
        except Ride.DoesNotExist:
            raise Http404("Ride does not exist.")

        return render(request, 'sharer_ride/sharer_search_ride_details.html', context={'ride': my_ride})


"""
Ying added on 02/06/2020
Driver search function

[NOTICE] Need to modify the template in render
"""

@login_required
def driver_search_and_result(request):
    my_user = get_object_or_404(MyUser, pk=request.user.pk)
    try:
        my_car = get_object_or_404(VehicleInfo, driver=my_user)
    except VehicleInfo.DoesNotExist:
        raise Http404("Car does not exist.")

    ride_list = Ride.objects.annotate(total_pass=F('owner_passengers')+F('sharer_passengers'))
    query = Q(status__exact="Open")
    query.add(Q(total_pass__lte=my_car.num_of_passengers, v_type__exact=my_car.v_type), Q.AND)
    ride_list = ride_list.filter(query).exclude(owner__exact=my_user).exclude(
                    driver__exact=my_user).exclude(sharer__exact=my_user).all()
    return render(request, 'driver_ride/show_driveable_ride_list.html', {'ride_list': ride_list})

"""
Griffin added on 02/06/2020
Allow driver  to join a ride
"""

@login_required
def driver_join_ride(request, pk):
    my_ride = get_object_or_404(Ride, pk=pk)

    if(my_ride.status == 'Open'):
        my_user = MyUser.objects.get(pk=request.user.pk)
        my_ride.driver = my_user
        my_ride.plate_number = VehicleInfo.objects.get(driver=my_user).plate_number
        my_ride.vehicle_capacity = VehicleInfo.objects.get(driver=my_user).num_of_passengers
        my_ride.status = 'Confirmed'
        my_ride.save()
        
        toaddrs = [my_ride.owner.email]#, my_ride.driver.email]
        if(my_ride.sharer):
          toaddrs.append(my_ride.sharer.email)
        message = "Hello user!\n"\
        "The following ride has been confirmed.\n"\
        "ID : {}\n" \
        "Destination : {}\n" \
        "Arrival Time : {}\n" \
        "Owner : {} {}\n" \
        "Owner passengers : {}\n" \
        .format(my_ride.ride_id, my_ride.dst_addr, my_ride.arrive_time, my_ride.owner.first_name, my_ride.owner.last_name, my_ride.owner_passengers)
        
        if(my_ride.sharer):
          message += "Sharer : {} {}\nSharer passengers : {}\n"\
          .format(my_ride.sharer.first_name, my_ride.sharer.last_name, my_ride.sharer_passengers)
        
        message += "Driver : {} {}\n"\
        "Vehicle capacity : {}\n"\
        .format(my_ride.driver.first_name, my_ride.driver.last_name, my_ride.vehicle_capacity)
        
        message += "Plate Number : {}\n" \
        "Vehicle type : {}\n" \
        "Special Vehicle Info : {}\n".format(my_ride.plate_number, my_ride.v_type, my_ride.special_request)
        
        for addr in toaddrs:
          send_mail('Ride confirmed!', message.format(my_ride.ride_id), settings.EMAIL_HOST_USER, [addr], fail_silently=False)
        
        return render(request, 'driver_ride/driver_ride_details.html', context={'ride': my_ride})
        # Ying modified to driver_view
    else:
        messages.error('Ride not valid (cancelled or already taken).')
        return PermissionDenied

"""
Griffin added on 02/06/2020
Allow driver to complete ride
"""

@login_required
def complete_ride(request, pk):
    my_ride = get_object_or_404(Ride, pk=pk)
    my_ride.status = 'Completed'
    my_ride.save()
    return render(request, 'ride_details.html', context={'ride': my_ride})


"""
Ying modified on 02/07/2020
Driver detail view
"""
@login_required
class DriverRideDetailView(LoginRequiredMixin, generic.DetailView):
    model = Ride
    template_name = 'driver_ride/driver_ride_details.html'
    context_object_name = 'ride'

    def driver_ride_detail_view(request, pk):
        try:
            my_ride = get_object_or_404(Ride, pk=pk)
        except Ride.DoesNotExist:
            raise Http404("Ride does not exist.")

        return render(request, 'driver_ride/driver_ride_details.html', context={'ride': my_ride})
