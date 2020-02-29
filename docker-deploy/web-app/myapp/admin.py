from django.contrib import admin

# Register your models here.
from .models import MyUser, Ride, VehicleInfo

#admin.site.register(User)
#admin.site.register(Ride)
#admin.site.register(Owner)
#admin.site.register(Driver)
#admin.site.register(Sharer)
#admin.site.register(Vehicle)
@admin.register(VehicleInfo)

class VehicleInfoAdmin(admin.ModelAdmin):
    list_display = ('plate_number', 'driver', 'v_type', 'num_of_passengers')

@admin.register(MyUser)

class MyUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'first_name', 'last_name', 'email', 'password', 'is_driver')


@admin.register(Ride)

class RideAdmin(admin.ModelAdmin):
    list_display = ('ride_id', 'dst_addr', 'status')
    list_filter = ('status', 'dst_addr')

