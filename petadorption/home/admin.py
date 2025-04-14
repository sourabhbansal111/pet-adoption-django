from django.contrib import admin
from .models import Usert, Contact, Letter, Blog
from django.contrib.auth.admin import UserAdmin


# @admin.register(Profile)
# class UserAdmin(admin.ModelAdmin):
#     list_display = ('username', 'email', 'role')
#     search_fields = ('username', 'email')
#     list_filter = ('role',)
# admin.site.register(Usert)

@admin.register(Usert)
class CustomUserAdmin(admin.ModelAdmin):
    model = Usert
    
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_superuser', 'is_active', 'last_login', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    list_filter = ('is_staff', 'is_superuser', 'is_active')



@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'location', 'get_type_display', 'status']

    def get_type_display(self, obj):
        return obj.get_type_display()

    get_type_display.short_description = 'Type'

admin.site.register(Letter)
# class LetterAdmin(admin.ModelAdmin):
#     list_display = ('firstname', 'email', 'number', 'status')
#     search_fields = ('firstname', 'email')
#     list_filter = ('status',)

@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ('id', 'pet_name', 'photo')
    search_fields = ('pet_name',)
