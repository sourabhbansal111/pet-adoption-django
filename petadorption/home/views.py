from django.contrib import messages
from django.contrib.auth import authenticate,login,logout

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Usert, Contact, Letter, Blog
from django.core.files.storage import FileSystemStorage
from django.http import Http404


from django.http import HttpResponse

from django.core.mail import send_mail

import random
from .forms import UserUpdateForm
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash

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
                password=password
            )
            messages.success(request,"registered successfuly")
    return render(request,'login.html')


def login_view(request):
    if request.method=="POST":
        email=request.POST.get('email')
        password=request.POST.get('password')
        user = Usert.objects.get(email=email)
        user=authenticate(request,username=user.username,email=email,password=password)
        #authenticate will check for username and password in your database
        if user:
            login(request,user)
            messages.success(request,"user loged in successfully")
            return redirect('blog')
        else:
            messages.error(request,"invalid credentials")

    return render(request,'login.html')

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
Hi {{ user.first_name|user.username|customer }},

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
Hi {{ user.first_name|user.username|customer }},

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
    return render(request, 'success.html')  # Or return HttpResponse("Email Verified Successfully!")

# === Dashboard ===
def blog(request):
    blogs = Blog.objects.all()
    return render(request, 'blog.html', {'blogs': blogs})


@login_required
def profile(request,email):
    if request.user.email != email:
        raise Http404("You're not allowed to access this page.")
    
    form = UserUpdateForm(instance=request.user)
    user_email = request.user.email
    contacts = Contact.objects.filter(email=user_email)
    letters = Letter.objects.filter(email=user_email)
    
    return render(request, 'profile.html', {'contacts': contacts, 'letters': letters, 'form': form})


@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile' , email=request.user.email)  # or wherever you want to go after saving
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
        if request.POST.get('email'):
            email = request.POST.get['email']
        else:
            email = request.user.email
        try:
            user = Usert.objects.get(email=email)
            otp = str(random.randint(100000, 999999))
            request.session['reset_email'] = email
            request.session['reset_otp'] = otp
            # send mail
            send_mail(
                subject = "Your PetCare Email Verification Code",
                message = f"""
Hi {user.email},

We received a request to Change password for your PetCare account.

Your one-time verification code is: {otp}

Please enter this code on the PetCare website or app to complete your verification. This code will expire in 10 minutes. For your security, do not share this code with anyone.

If you didn’t request this, you can safely ignore this email.

Thanks,  
The PetCare Team  
https://www.petcare.com

PetCare Inc. | 123 Paw Street | New York, NY 10001  
""",

                from_email='parkspaws.petcare@gmail.com',
                recipient_list=[email],
                fail_silently=False,
            )
            messages.success(request, 'OTP sent to your email.')
            request.session['otp_sent'] = True
            return redirect('verify_otp')
        except Usert.DoesNotExist:
            messages.error(request, 'Email not registered.')
    return render(request, 'forgot_password.html')


def verify_otp_view(request):
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
        return render(request, 'verify_otp.html')
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
Hi {{ user.first_name|user.username|customer }},

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
            firstname=request.POST['firstname'],
            lastname=request.POST['lastname'],
            number=request.POST['number'],
            email=request.POST['email'],
            location=request.POST['location'],
            message=request.POST['message'],
            petname=request.POST['petname'],
            petid=request.POST['petid']
        )
        messages.success(request, "Contact form submitted")
        return redirect
    return render(request, 'contact.html')

# === Letter Form ===
@login_required
def letter_view(request):
    if request.method == 'POST':
        Letter.objects.create(
            firstname=request.POST['firstname'],
            email=request.POST['email'],
            number=request.POST['number'],
            location=request.POST['location'],
            message=request.POST['message']
        )
        messages.success(request, "Letter submitted")
        return redirect('contact')
    return render(request, 'letter.html')


# === Blog Creation ===
@login_required
@user_passes_test(is_admin)
def create_blog(request):
    if request.method == 'POST':
        id = request.POST['id']
        photo = request.FILES['photo']
        pet_name = request.POST['pet_name']
        heading_explanation = request.POST['heading_explanation']
        subheadings = "**".join(request.POST.getlist('subheadings'))
        explanations = "**".join(request.POST.getlist('explanations'))

        Blog.objects.create(
            id=id,
            photo=photo,
            pet_name=pet_name,
            heading_explanation=heading_explanation,
            subheadings=subheadings,
            explanations=explanations
        )
        messages.success(request, "Blog added")
        return redirect('blog')
    return render(request, 'create_blog.html')

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

