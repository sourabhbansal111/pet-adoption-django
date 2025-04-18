from django.contrib import messages
from django.contrib.auth import authenticate,login,logout

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Usert, Contact, Letter, Blog
from django.core.files.storage import FileSystemStorage
from django.http import Http404
from django.db.models import Q

from django.http import HttpResponse

from django.core.mail import send_mail
import os
from django.http import JsonResponse
import json

import random
from .forms import UserUpdateForm
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash

from django.views.decorators.http import require_POST
from django.http import HttpResponseNotFound

# Create your views here.
def home(request):
    return render(request ,'home.html')

def aboutus(request):
    return render(request ,'about.html')

# === Role check decorators ===
def is_admin(user):
    return user.role == "admin"

def is_superadmin(user):
    return user.role == "superadmin"

# === Auth Views ===

def register_view(request):
    if request.method=="POST":
        name=request.POST.get('username')
        email=request.POST.get('email')
        password=request.POST.get('password')
        cpassword=request.POST.get('cpassword')
        if request.POST.get('role'): 
            if not name:
                messages.error(request,"please enter valid username")
            elif password!=cpassword:
                messages.error(request,"password not match")
            elif Usert.objects.filter(email=email).exists():
                messages.error(request, "Email already exists.")
            elif Usert.objects.filter(username=name).exists():
                messages.error(request, "Username already taken.")
            else:
                Usert.objects.create(
                username=name,
                email=email,
                password=password,
                is_staff=True
                )
                messages.success(request,"registered successfuly")
            return redirect('adminpage')
        if not name:
            messages.error(request,"please enter valid username")
        elif password!=cpassword:
            messages.error(request,"password not match")
        elif Usert.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
        elif Usert.objects.filter(username=name).exists():
            messages.error(request, "Username already taken.")
        else:
            Usert.objects.create_user(
                username=name,
                email=email,
                password=password,
            )
            messages.success(request,"registered successfuly")
    return render(request,'login.html')

def login_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = None

        # Try with username if given
        if username:
            user = authenticate(request, username=username, password=password)

        # If not authenticated and email is provided, try to find username by email
        if user is None and email:
            try:
                user_obj = Usert.objects.get(email=email)
                user = authenticate(request, username=user_obj.username, password=password)
            except Usert.DoesNotExist:
                user = None

        if user:
            login(request, user)
            messages.success(request, "User logged in successfully")
            return redirect('home')
        else:
            messages.error(request, "Invalid credentials. Please check your info.")

    return render(request, 'login.html')


def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def verifyemail_view(request,email):
    if request.user.email != email:
        raise Http404("You're not allowed to access this page.")

    if request.user.is_verified:
        return render(request,'success.html')
    
    if request.method == "POST":
        if 'send_otp' in request.POST:
            otp = ''.join([str(random.randint(0, 9)) for _ in range(6)])
            request.session['otp'] = otp
            request.session['otp_email'] = request.user.email

            send_mail(
                subject = "Your PetCare Email Verification Code",
                message = f"""
Hi { request.user.username},

We received a request to verify your email address for your PetCare account.

Your one-time verification code is: {otp}

Please enter this code on the PetCare website or app to complete your verification. This code will expire in 10 minutes. For your security, do not share this code with anyone.

If you didn’t request this, you can safely ignore this email.

Thanks,  
The PetCare Team  
https://www.petcare.com

PetCare Inc. | 123 Paw Street | New York, NY 10001  
""",

                from_email='parkspaws.petcare@gmail.com',
                recipient_list=[request.user.email],
                fail_silently=False,
            )

            messages.success(request, 'OTP sent to your email!')
            return render(request, 'verifyemail.html', {
                'user': request.user,
                'show_otp_form': True
            })

        elif 'verify_otp' in request.POST:
            entered_otp = ''.join([request.POST.get(f'digit{i}', '') for i in range(1, 7)])
            if entered_otp == request.session.get('otp'):
                request.user.is_verified = True
                request.user.save()
                
                send_mail(
                    subject = "Your PetCare Email Verification Code",
                    message = f"""
Hi {request.user.username },

🎉 Your email ({{ request.user.email }}) has been successfully verified.

You're now fully set to enjoy everything PetCare has to offer – from personalized features to secure access.

If this wasn't you or you believe your account was verified by mistake, please contact us immediately.

Thanks for verifying and being part of our community 🐾

Thanks,  
The PetCare Team  
https://www.petcare.com

PetCare Inc. | 123 Paw Street | New York, NY 10001  

""",

                    from_email='parkspaws.petcare@gmail.com',
                    recipient_list=[request.user.email],
                    fail_silently=False,
                )

                messages.success(request, 'Email verified successfully!')
                return redirect('success',email=request.user.email)
            else:
                messages.error(request, 'Invalid OTP. Please try again.')
                return render(request, 'verifyemail.html', {
                    'user': request.user,
                    'show_otp_form': True
                })

    return render(request, 'verifyemail.html', {'user': request.user})


@login_required
def success_view(request,email):
    if email==request.user.email:
        return render(request, 'success.html')  
    else:
        raise Http404("You're not allowed to access this page.")

# === Dashboard ===
def blog(request, blog=""):
    if blog == "adopt":
        blogs = Blog.objects.filter(type='adopt')
    elif blog == "service":
        blogs = Blog.objects.filter(type='service')
    else:
        blogs = Blog.objects.all()

    return render(request, 'blog.html', {'blogs': blogs,'key':blog})



@login_required
def profile(request,email):
    if request.user.email != email:
        raise Http404("You're not allowed to access this page.")
    
    form = UserUpdateForm(instance=request.user)
    user_email = request.user.email
    contacts = Contact.objects.filter(email=user_email)
    letters = Letter.objects.filter(email=user_email)
    conditions = [
        any(contact.status=="accepted" for contact in Contact.objects.all()),  # Condition 1
        any(contact.status=="declined" for contact in Contact.objects.all()),  # Condition 2
        any(contact.status=="pending" for contact in Contact.objects.all()),   # Condition 3
        any(letter.status=="Viewed" for letter in Letter.objects.all()),       # Condition 4
        any(letter.status=="Not Viewed" for letter in Letter.objects.all())    # Condition 5
    ]
    return render(request, 'profile.html', {'contacts': contacts, 'letters': letters, 'form': form, 'co' : conditions})


@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, request.FILES, instance=request.user)
        user = Usert.objects.get(email=request.user.email)
        if form.is_valid():
            email_changed = form.cleaned_data['email'] != user.email
            user = form.save(commit=False)  # Don't save yet

            if email_changed:
                user.is_verified = False
                messages.warning(request, "Email has been changed. You need to verify your new email address.")
            else:
                messages.success(request, "Changes saved.")

            user.save()  # Now save including is_verified
            return redirect('profile', email=user.email)



    else:   
        form = UserUpdateForm(instance=request.user)
    user_email = request.user.email
    contacts = Contact.objects.filter(email=user_email)
    letters = Letter.objects.filter(email=user_email)
    
    return render(request, 'profile.html', {'contacts': contacts, 'letters': letters, 'form': form})



def custom_404_view(request, exception):
    return render(request, '404.html', {
        'exception': exception
    }, status=404)

@login_required
def change_password_view(request):
    if request.method == 'POST':
        old_password = request.POST.get('old_password')
        new_password1 = request.POST.get('new_password1')
        new_password2 = request.POST.get('new_password2')

        user = request.user

        if not user.check_password(old_password):
            messages.error(request, '❌ Old password is incorrect.')
            return redirect(request.META.get('HTTP_REFERER'))
        if new_password1 != new_password2:
            messages.error(request, '❌ New passwords do not match.')
            return redirect(request.META.get('HTTP_REFERER'))

        if len(new_password1) < 6:
            messages.error(request, '❌ Password must be at least 6 characters.')
            return redirect(request.META.get('HTTP_REFERER'))

        # Change password
        user.set_password(new_password1)
        user.save()
        update_session_auth_hash(request, user) 
        messages.success(request, '✅ Password changed successfully.')
        return redirect('profile',email=request.user.email)  
     
    return redirect('profile',email=request.user.email) 

def forgot_password_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        if not email:
            if request.user.is_authenticated:
                email = request.user.email
            else:
                messages.error(request, 'Please enter your email.')
                return redirect(request.META.get('HTTP_REFERER', 'login'))

        try:
            user = Usert.objects.get(email=email)
            otp = str(random.randint(100000, 999999))
            request.session['reset_email'] = email
            request.session['reset_otp'] = otp

            # send mail
            send_mail(
                subject="Your PetCare Email Verification Code",
                message=f"""
Hi {user.username},

We received a request to change the password for your PetCare account.

Your one-time verification code is: {otp}

Please enter this code on the PetCare website or app to complete your verification. This code will expire in 10 minutes. For your security, do not share this code with anyone.

If you didn’t request this, you can safely ignore this email.

Thanks,  
The PetCare Team  
https://www.petcare.com

PetCare Inc. | 123 Paw Street | New York, NY 10001
""",  # plain text fallback

                from_email='parkspaws.petcare@gmail.com',
                recipient_list=[email],
                html_message=f"""
<html>
  <body style="font-family: Arial, sans-serif; color: #333;">
    <p>Hi {user.username},</p>
    <p>We received a request to change the password for your PetCare account.</p>
    <p>Your one-time verification code is:</p>
    <p style="font-size: 24px; font-weight: bold; color: #2c7be5;">{otp}</p>
    <p>Please enter this code on the PetCare website or app to complete your verification. This code will expire in 10 minutes. For your security, do not share this code with anyone.</p>
    <p>If you didn’t request this, you can safely ignore this email.</p>
    <br>
    <p>Thanks,<br>The PetCare Team</p>
    <p><a href="https://www.petcare.com">https://www.petcare.com</a></p>
    <footer style="font-size: 12px; color: #888;">
      <p>PetCare Inc. | 123 Paw Street | New York, NY 10001</p>
    </footer>
  </body>
</html>
""",
                fail_silently=False,
            )

            messages.success(request, 'OTP sent to your email.')
            request.session['otp_sent'] = True
            return redirect('verify_otp')

        except Usert.DoesNotExist:
            messages.error(request, 'Email not registered.')

    return render(request, 'forgot_password.html')
def forgot_password_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        if not email:
            if request.user.is_authenticated:
                email = request.user.email
            else:
                messages.error(request, 'Please enter your email.')
                return redirect(request.META.get('HTTP_REFERER', 'forgot_password'))

        try:
            user = Usert.objects.get(email=email)
            otp = str(random.randint(100000, 999999))
            request.session['reset_email'] = email
            request.session['reset_otp'] = otp

            # send mail
            send_mail(
                subject="Your PetCare Email Verification Code",
                message=f"""
Hi {user.username},

We received a request to change the password for your PetCare account.

Your one-time verification code is: {otp}

Please enter this code on the PetCare website or app to complete your verification. This code will expire in 10 minutes. For your security, do not share this code with anyone.

If you didn’t request this, you can safely ignore this email.

Thanks,  
The PetCare Team  
https://www.petcare.com

PetCare Inc. | 123 Paw Street | New York, NY 10001
""",  # plain text fallback

                from_email='parkspaws.petcare@gmail.com',
                recipient_list=[email],
                html_message=f"""
<html>
  <body style="font-family: Arial, sans-serif; color: #333;">
    <p>Hi {user.username},</p>
    <p>We received a request to change the password for your PetCare account.</p>
    <p>Your one-time verification code is:</p>
    <p style="font-size: 24px; font-weight: bold; color: #2c7be5;">{otp}</p>
    <p>Please enter this code on the PetCare website or app to complete your verification. This code will expire in 10 minutes. For your security, do not share this code with anyone.</p>
    <p>If you didn’t request this, you can safely ignore this email.</p>
    <br>
    <p>Thanks,<br>The PetCare Team</p>
    <p><a href="https://www.petcare.com">https://www.petcare.com</a></p>
    <footer style="font-size: 12px; color: #888;">
      <p>PetCare Inc. | 123 Paw Street | New York, NY 10001</p>
    </footer>
  </body>
</html>
""",
                fail_silently=False,
            )

            messages.success(request, 'OTP sent to your email.')
            request.session['otp_sent'] = True
            return redirect('verify_otp',email=email)

        except Usert.DoesNotExist:
            messages.error(request, 'Email not registered.')

    return render(request, 'forgot_password.html')

def verify_otp_view(request,email):
    if request.method == 'POST':
        entered_otp = ''.join([request.POST.get(f'digit{i}', '') for i in range(1, 7)])

        session_otp = request.session.get('reset_otp')
        if entered_otp == session_otp:
            request.session['otp_verified'] = True
            messages.success(request, 'OTP verified. Set a new password.')
            return redirect('set_new_password')
        else:
            messages.error(request, 'Incorrect OTP.')
    if request.session.get('otp_sent'):
        return render(request, 'verify_otp.html',{"email":email})
    else:
        raise Http404("You're not allowed to access this page.")
     

def set_new_password_view(request):
    if request.session.get('otp_verified'):
        request.session['otp_sent'] = False

        email = request.session.get('reset_email')
        if request.method == 'POST':
            pass1 = request.POST['new_password1']
            pass2 = request.POST['new_password2']

            if pass1 == pass2:
                try:
                    if request.user.is_authenticated :
                        user = Usert.objects.get(email=email)
                        user.set_password(pass1)
                        user.is_verified = True
                        user.save()
                        send_mail(
                            subject = "Your PetCare Email Verification Code",
                            message =f"""
Hi {user.username },

We’re letting you know that your password was successfully changed.

If you made this change, no further action is needed.

If you did **not** change your password, please reset your password immediately by clicking the link below or contact support:

🔗 Reset Password through our site.

Keeping your account safe is our top priority.

Thanks,  
The PetCare Team  
https://www.petcare.com

PetCare Inc. | 123 Paw Street | New York, NY 10001  
""",

                            from_email='parkspaws.petcare@gmail.com',
                            recipient_list=[email],
                            fail_silently=False,
                        )
                        # 💡 Try updating session (if user is logged in)
                        if request.user.is_authenticated and request.user == user:
                            update_session_auth_hash(request, user)
                        else:
                            # 👇 Re-authenticate and log them in if coming from OTP link or not logged in
                            user = authenticate(request, username=user.username, password=pass1)
                            if user is not None:
                                login(request, user)

                        messages.success(request, 'Password changed successfully.')
                        request.session['otp_verified'] = False
                        #so that user cant change password after change once
                        return redirect('profile' , email=request.user.email)  
                    else:
                        user = Usert.objects.get(email=email)
                        user.set_password(pass1)
                        # user.is_verified = True
                        user.save()

                        messages.success(request, 'Password changed successfully.')
                        request.session['otp_verified'] = False
                        #so that user cant change password after change once
                        return redirect('login')  
                except Usert.DoesNotExist:
                    messages.error(request, 'User not found.')
                except Exception as e:
                    messages.error(request, f'Something went wrong: {str(e)}')
            else:
                messages.error(request, 'Passwords do not match.')


        return render(request, 'set_new_password.html')
    raise Http404("You're not allowed to access this page.")


# === Contact Form ===
@login_required
def contact_view(request):
    if request.method == 'POST':
        Contact.objects.create(
            username=request.POST['username'],
            number=request.POST['phone'],
            email=request.POST['email'],
            type=request.POST['type'],
            location=request.POST['location'],
            message=request.POST['message'],
            pname=request.POST['pet-name'],
            pid=request.POST['pet-id']
        )
        messages.success(request, "Contact form submitted")
    return render(request, 'contact.html')


def delete_contact(request, id):
    if request.method=='POST':
        try:
            contact = get_object_or_404(Contact, id=id)
            contact.delete()
        except 404:
            messages.error(request,"request not found")
        return redirect(request.META.get('HTTP_REFERER', 'home')) 
    else:
        raise Http404("You're not allowed to access this page.")

def delete_letter(request, id):
    if request.method=='POST':
        try:
            letter = get_object_or_404(Letter, id=id)
            letter.delete()
        except 404:
            messages.error(request,"letter not found")
        return redirect(request.META.get('HTTP_REFERER', 'home')) 
    else:
        raise Http404("You're not allowed to access this page.")


# === Letter Form ===
@login_required
def letter_view(request):
    if request.method == 'POST':
        Letter.objects.create(
            username=request.POST['username'],
            email=request.POST['email'],
            number=request.POST['phone'],
            location=request.POST['location'],
            message=request.POST['message']
        )
        messages.success(request, "Letter submitted")
        return redirect('contact')
    return render(request, 'contact.html')


# === Blog Creation ===
@login_required
def create_blog(request):
    if request.method == 'POST':
        id = request.POST['id']

        # Check if the ID already exists
        if Blog.objects.filter(id=id).exists():
            messages.error(request, "ID already exists! Please use a unique ID.")
            return redirect('blog')

        photo = request.FILES['photo']
        if not photo:
            messages.error(request, "No photo selected.")
            return redirect(request.META.get('HTTP_REFERER', 'blog'))

        type = request.POST['type']
        pet_name = request.POST['pname']
        heading_explanation = request.POST['heading_explanation']
        subheadings = "**".join(request.POST.getlist('subheading[]'))
        explanations = "**".join(request.POST.getlist('explanation[]'))

        # Custom file path
        upload_folder = os.path.join('home','static', 'images', 'uploads', 'pets')
        os.makedirs(upload_folder, exist_ok=True)

        filename = photo.name
        filepath = os.path.join(upload_folder, filename)

        with open(filepath, 'wb+') as destination:
            for chunk in photo.chunks():
                destination.write(chunk)

        Blog.objects.create(
            id=id,
            photo=photo,  # Save the relative path if you plan to render it
            type=type,
            pet_name=pet_name,
            heading_explanation=heading_explanation,
            subheadings=subheadings,
            explanations=explanations
        )
        messages.success(request, "Blog added successfully!")
        return redirect('blog')

    return render(request, 'create_blog.html')

@login_required
def staff_view(request):
    if request.user.is_staff or request.user.is_superuser:
        users = Usert.objects.filter(is_staff=False)
        admins = Usert.objects.filter(Q(is_staff=True) | Q(is_superuser=True))

        contacts = Contact.objects.all()
        letters = Letter.objects.all()
        cards = Blog.objects.all()
        existing_ids = [card.id for card in cards]
        conditions = [
        any(contact.status=="accepted" for contact in Contact.objects.all()),  # Condition 1
        any(contact.status=="declined" for contact in Contact.objects.all()),  # Condition 2
        any(contact.status=="pending" for contact in Contact.objects.all()),   # Condition 3
        any(letter.status=="Viewed" for letter in Letter.objects.all()),       # Condition 4
        any(letter.status=="Not Viewed" for letter in Letter.objects.all())    # Condition 5
        ]
        orders={
            "total":Order.objects.all(),
            "completed": Order.objects.filter(status="Completed"),
            "pending":Order.objects.filter(status="Pending")
        }
       

        return render(request, "staff.html", {
            "admins": admins,
            "users": users,
            "contacts": contacts,
            "letters": letters,
            "cards": cards,
            "existing_ids": existing_ids,
            "co":conditions,
            "orders": orders,
        })
    else:
        return redirect('lofin')


@login_required
def admin_view(request):
    if request.user.is_superuser:
        users = Usert.objects.filter(is_staff=False)
        admins = Usert.objects.filter(Q(is_staff=True) | Q(is_superuser=True))
        contacts = Contact.objects.all()
        letters = Letter.objects.all()
        cards = Blog.objects.all()
        existing_ids = [card.id for card in cards]
        conditions = [
        any(contact.status=="accepted" for contact in Contact.objects.all()),  # Condition 1
        any(contact.status=="declined" for contact in Contact.objects.all()),  # Condition 2
        any(contact.status=="pending" for contact in Contact.objects.all()),   # Condition 3
        any(letter.status=="Viewed" for letter in Letter.objects.all()),       # Condition 4
        any(letter.status=="Not Viewed" for letter in Letter.objects.all())    # Condition 5
        ]
    
        orders=[
            Order.objects.all(),
            Order.objects.filter(status="Completed"),
            Order.objects.filter(status="Pending")
        ]
   

        return render(request, "superuser.html", {
            "admins": admins,
            "users": users,
            "contacts": contacts,
            "letters": letters,
            "cards": cards,
            "existing_ids": existing_ids,
            "co":conditions,
            "orders": orders,
        })
    else:
        return redirect('login')




@login_required
def delete_user(request, username):
    referer_url = request.META.get('HTTP_REFERER', None)
    if request.method == 'POST':
        user_to_delete = get_object_or_404(Usert, username=username)
        
        if request.user != user_to_delete:  # Optional: prevent deleting yourself
            user_to_delete.delete()
            messages.success(request, f"User '{username}' has been deleted successfully.")  # Success message
        else:
            messages.warning(request, "You cannot delete your own account.")  # Warning message if user tries to delete themselves
        if referer_url:
            return redirect(referer_url)  # Redirect to the referer (previous page)
        else:
            return redirect('staff')
    
    messages.error(request, "Invalid request method.")  # Error message if not POST
    return redirect('home') # Fallback to 'staff' if no referer is found



# ✅ Update status for Contacts
@login_required
@require_POST
def update_status(request):
    con_ids = request.POST.getlist('con_ids')
    status = request.POST.get('status')

    if con_ids:
        if status == "del":
            for contact_id in con_ids:
                entry = Contact.objects.filter(id=contact_id).first()
                if entry:
                    entry.delete()
        else:
            for contact_id in con_ids:
                cont = Contact.objects.filter(id=contact_id)
                Contact.objects.filter(id=contact_id).update(status=status)
                if status=="acepted":
                    send_mail(
                            subject = "Your PetCare Email Verification Code",
                            message = f"""
Hi {cont.username},

Great news! Your recent request has been **accepted** ✅

We’re happy to inform you that everything has been reviewed and approved successfully. If you have any questions or need further assistance, feel free to reach out.

Thanks for being a part of PetCare 🐾

Warm regards,  
The PetCare Team  
https://www.petcare.com

PetCare Inc. | 123 Paw Street | New York, NY 10001
""",
                    

                            from_email='parkspaws.petcare@gmail.com',
                            recipient_list=[cont.email],
                            fail_silently=False,
                        )
                else:
                    send_mail(
                            subject = "Your PetCare Email Verification Code",
                            message = f"""
Hi {cont.username},

We wanted to let you know that your recent request has been **declined** ❌

This could be due to missing information or something not meeting our current requirements. You’re welcome to reach out for more details or reapply with the necessary changes.

Thanks for understanding and being a valued part of PetCare 🐾

Warm regards,
{cont.last_updated_by}  
The PetCare Team  
https://www.petcare.com

PetCare Inc. | 123 Paw Street | New York, NY 10001
""",
                    

                            from_email='parkspaws.petcare@gmail.com',
                            recipient_list=[cont.email],
                            fail_silently=False,
                        )

    return redirect(request.META.get('HTTP_REFERER', 'fallback_url'))


# ✅ Update status for Letters
@login_required
@require_POST
def update_status_letter(request):
    lett_ids = request.POST.getlist('lett_ids')
    status = request.POST.get('status')

    if lett_ids:
        if status == "del":
            for letter_id in lett_ids:
                entry = Letter.objects.filter(id=letter_id).first()
                if entry:
                    entry.delete()
        else:
            Letter.objects.filter(id__in=lett_ids).update(status=status)

    return redirect(request.META.get('HTTP_REFERER', 'fallback_url'))



def blog_delete(request):
    if request.method == 'POST':
        blog_id = request.POST.get("blog_id")

        if not blog_id:
            messages.error(request, "Blog ID is required!")
            return redirect(request.META.get('HTTP_REFERER', 'fallback_url'))

        blog = Blog.objects.filter(id=blog_id).first()
        if blog:
            blog.delete()
            messages.success(request, "Blog deleted successfully!")
        else:
            messages.error(request, "Blog ID not found!")

        return redirect(request.META.get('HTTP_REFERER', 'fallback_url'))

    # If it's not a POST request
    messages.error(request, "Invalid request method.")
    return redirect('blog')


def get_pet_data(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        value = data.get('value')
        field = data.get('field')

        if field == 'id':
            pet = Blog.objects.filter(id=value).first()
            if pet:
                return JsonResponse({'pet_name': pet.pet_name})
        elif field == 'name':
            pet = Blog.objects.filter(pet_name=value).first()
            if pet:
                return JsonResponse({'pet_id': pet.id})

    return JsonResponse({})

def doggydaycamp(request):
    return render(request ,'doggydaycamp.html')

def see_pricing(request):
    return render(request ,'boarding.html')

def grooming(request):
    return render(request ,'grooming.html')

def doggycamp(request):
    return render(request , 'doggycamp.html')

def puppyplay(request):
    return render(request ,'PuppyPlayGroup.html')

def faq(request):
    return render(request , 'faq.html')


from django.shortcuts import render, redirect
from django.contrib import messages
from store.models import Order

def order_dashboard(request):
    tab = request.GET.get('tab', 'all')
    
    if tab == 'completed':
        orders = Order.objects.filter(status="Completed")
    elif tab == 'pending':
        orders = Order.objects.filter(status="Pending")
    else:
        orders = Order.objects.all()

    count = {
        "total": Order.objects.count(),
        "completed": Order.objects.filter(status="Completed").count(),
        "pending": Order.objects.filter(status="Pending").count(),
    }

    return render(request, 'staff', {
        "orders": orders,
        "count": count,
        "active_tab": tab
    })

def update_status_order(request):
    if request.method == 'POST':
        ids = request.POST.getlist('ord_ids')
        status = request.POST.get('status')
        referer_url = request.META.get('HTTP_REFERER', None)
        if status == 'Completed':
            Order.objects.filter(id__in=ids).update(status='Completed')
            messages.success(request, "Selected orders marked as Completed.")
        elif status == 'del':
            Order.objects.filter(id__in=ids).delete()
            messages.success(request, "Selected orders deleted.")
        if referer_url:
            return redirect(referer_url)  # Redirect to the referer (previous page)
        else:
            return redirect('staff')



# === Contact Admin Views ===
@login_required
@user_passes_test(is_admin)
def view_contacts(request):
    contacts = Contact.objects.all()
    return render(request, 'view_contacts.html', {'contacts': contacts})

@login_required
@user_passes_test(is_admin)
def approve_contact(request, id):
    contact = get_object_or_404(Contact, id=id)
    contact.status = "V"
    contact.save()
    return redirect('view_contacts')

@login_required
@user_passes_test(is_admin)
def reject_contact(request, id):
    contact = get_object_or_404(Contact, id=id)
    contact.status = "R"
    contact.save()
    return redirect('view_contacts')

# === Letter Admin Views ===
@login_required
@user_passes_test(is_admin)
def view_letters(request):
    letters = Letter.objects.all()
    return render(request, 'view_letters.html', {'letters': letters})

@login_required
@user_passes_test(is_admin)
def approve_letter(request, id):
    letter = get_object_or_404(Letter, id=id)
    letter.status = "R"
    letter.save()
    return redirect('view_letters')

@login_required
@user_passes_test(is_admin)
def reject_letter(request, id):
    letter = get_object_or_404(Letter, id=id)
    letter.status = "NR"
    letter.save()
    return redirect('view_letters')

# === Superadmin View ===
@login_required
@user_passes_test(is_superadmin)
def admin_list(request):
    admins = Usert.objects.filter(role="admin")
    return render(request, 'admin_list.html', {'admins': admins})

