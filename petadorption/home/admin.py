from django.contrib import admin,messages
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
    list_display = ['id','username', 'email', 'location', 'type', 'status','last_updated_by']
    search_fields = ('username', 'email','location')
    list_filter = ('status','type')
    readonly_fields = ['last_updated_by']

    def save_model(self, request, obj, form, change):
        obj.last_updated_by = request.user  # store who made the last change
        super().save_model(request, obj, form, change)

@admin.register(Letter)
class LetterAdmin(admin.ModelAdmin):
    list_display = ('id','username', 'email', 'number', 'status', 'last_updated_by')
    readonly_fields = ['last_updated_by']
    search_fields = ('username', 'email')
    list_filter = ('status',)

    def save_model(self, request, obj, form, change):
        if change:
            original = Letter.objects.get(pk=obj.pk)
            if original.status == 'Viewed':
                messages.error(request, "This letter has already been viewed and cannot be changed.")
                return  # stop save

        obj.last_updated_by = request.user
        super().save_model(request, obj, form, change)

@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ('id', 'pet_name', 'photo','type')
    search_fields = ('pet_name',)
    list_filter = ('type',)

