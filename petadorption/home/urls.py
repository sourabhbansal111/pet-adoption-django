from django.urls import path
from . import views
from django.conf.urls import handler404

handler404 = 'home.views.custom_404_view',
urlpatterns = [
    path('', views.home,name='home'),
    path('about_us/', views.aboutus,name='aboutus'),



    # Authentication
    path('login/', views.login_view, name='login'),
    path('verify_email/<str:email>/', views.verifyemail_view, name='verifyemail'),
    path('email_verified/<str:email>/', views.success_view, name='success'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('change_password/', views.change_password_view, name='change_password'),
    path('forgot-password/', views.forgot_password_view, name='forgot_password'),
    path('verify-otp/<str:email>', views.verify_otp_view, name='verify_otp'),
    path('set-new-password/', views.set_new_password_view, name='set_new_password'),


    # Dashboard
    path('blog/', views.blog, name='blog'),
    path('blog/<str:blog>/', views.blog, name='blog'),
    path('profile/<str:email>/', views.profile, name='profile'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),

    # Contact and Letter Forms
    path('contact/', views.contact_view, name='contact'),
    path('letter/', views.letter_view, name='letter'),
    path('deletecont/<int:id>/', views.delete_contact, name='delete_contact'),
    path('deleteletter/<int:id>/', views.delete_letter, name='delete_letter'),

    path('staff/', views.staff_view, name='staff'),
    path('adminpage/', views.admin_view, name='adminpage'),
    path('delete-user/<str:username>/', views.delete_user, name='delete_user'),

    path('update_status/', views.update_status, name='update_status'),
    path('update_status_letter/', views.update_status_letter, name='update_status_letter'),



    # Blog
    path('create-blog/', views.create_blog, name='create_blog'),
    path('delete-blog/', views.blog_delete, name='delete_blog'),
    path('get_pet_data/', views.get_pet_data, name='get_pet_data'),





    path('services_doggy_day_camp/', views.doggydaycamp,name='doggydaycamp'),
    path('boarding/', views.see_pricing,name='boarding'),
    path('grooming/', views.grooming,name='grooming'),
    path('doggy_day_camp/', views.doggycamp,name='doggycamp'),
    path('puppy_play_group/', views.puppyplay,name='puppyplay'),
    path('faq/', views.faq,name='faq'),



    path('orders/update/', views.update_status_order, name='update_status_order'),
    # # Admin Contact Management
    # path('view-contacts/', views.view_contacts, name='view_contacts'),
    # path('approve-contact/<int:id>/', views.approve_contact, name='approve_contact'),
    # path('reject-contact/<int:id>/', views.reject_contact, name='reject_contact'),

    # # Admin Letter Management
    # path('view-letters/', views.view_letters, name='view_letters'),
    # path('approve-letter/<int:id>/', views.approve_letter, name='approve_letter'),
    # path('reject-letter/<int:id>/', views.reject_letter, name='reject_letter'),

    # # Superadmin - Manage Admins
    # path('admin-list/', views.admin_list, name='admin_list'),

]
