from django.shortcuts import render, redirect
from .forms import CaretakerSignupForm, PatientSignupForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from care.models import Caretaker, Patient
from django.contrib.auth.decorators import login_required


from django.contrib import messages

def caretaker_signup(request):
    if request.method == 'POST':
        form = CaretakerSignupForm(request.POST, request.FILES)

        if form.is_valid():


            email = form.cleaned_data['emails']
            if User.objects.filter(username=email).exists():
                messages.error(request, "Email already exists. Please use a different email.")
                # return redirect('/login/')
            raw_password = form.cleaned_data['passwords']
                
            user = User.objects.create_user(
                    username=email,
                    password=raw_password  # Automatically hashed
                )

                # Create Caretaker instance linked to User
            caretaker = form.save(commit=False)
            caretaker.availability = True 
            caretaker.user = user
            caretaker.save()
            return redirect('/') 
        else:
            print(form.errors) # redirect to login page
    else:
        form = CaretakerSignupForm()
    return render(request, 'login.html', {'form': form})

def patient_signup(request):
    if request.method == 'POST':
        form = PatientSignupForm(request.POST)
        if form.is_valid():


            email = form.cleaned_data['email']
            raw_password = form.cleaned_data['password']
                
            user = User.objects.create_user(
                    username=email,
                    password=raw_password  # Automatically hashed
                )

                # Create Caretaker instance linked to User
            patient = form.save(commit=False)
            patient.user = user
            patient.save()
            return redirect('/')
    
        else:
            print(form.errors)
    else:
        form = PatientSignupForm()
    return render(request, 'login.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        if not User.objects.filter(username = email).exists():
            messages.info(request, "Username doesn't exists.")
            return redirect('/login/')
        
        user = authenticate(request, username=email, password=password)  # We used email as username
        if user is not None:
            login(request, user)
            messages.success(request, 'You have successfully logged in.')
        else:
            messages.error(request, 'Invalid email or password')
    
        if hasattr(user, 'patient'):
            return redirect('/user_home')
        elif hasattr(user, 'caretaker'):
            return redirect('/caretaker_home')
        else:
            return redirect('/')

      
    return render(request, 'login.html')

def profile_update(request):
    if request.method == 'POST':
        form = CaretakerSignupForm(request.POST, instance=request.user.caretaker)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect('/profile_update/')
    else:
        form = CaretakerSignupForm(instance=request.user.caretaker)
    return render(request, 'profile_update.html', {'form': form})

def user_home(request):
    caretakers = Caretaker.objects.all().order_by('-availability')  # Sort by availability
    if request.user.is_authenticated:
        return render(request, 'user_home.html', {'caretakers': caretakers})
    else:
        messages.error(request, "You need to log in to access this page.")
        return redirect('/login/')
    

from django.http import JsonResponse
from .models import Caretaker

def available_caretakers(request):
    caretakers = Caretaker.objects.filter(availability=True)
    data = [
        {
            "id": c.id,
            "full_names": c.full_names,
            "role": c.role,
            "experiences": c.experiences,
            "location": c.locations,
            "rate": float(c.rate),
            "availability": c.availability,
            "image_url": c.image_url.url if c.image_url else ""
        }
        for c in caretakers
    ]
    return JsonResponse(data, safe=False)

    
def caretaker_home(request):
    caretaker = get_object_or_404(Caretaker, user=request.user)
    pending_bookings = Booking.objects.filter(caretaker=caretaker, status="Pending")
    history_bookings = Booking.objects.filter(caretaker=caretaker, status__in=['Accepted', 'Completed'])


    if request.user.is_authenticated:
        return render(request, 'caretaker_home.html', {'caretakers': caretaker, 'bookings': pending_bookings, 'history_bookings': history_bookings})
    else:
        messages.error(request, "You need to log in to access this page.")
        return redirect('/login/')
    
def caretaker_list_view(request):
    caretakers = Caretaker.objects.all().order_by('-availability')  # Sort by availability
    return render(request, 'Browse_caregiver.html', {'caretakers': caretakers})



def home(request):
    return render(request, 'Home.html')


from django.contrib.auth import logout
from django.shortcuts import redirect

def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect('/')

def notification(request):
    return render(request, 'notification.html')

# def book(request):
#     return render(request, 'book.html')

from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .models import Caretaker, Booking
from django.utils import timezone

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Caretaker, Patient, Booking


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Caretaker, Booking, Patient

@login_required
def book_caretaker(request, caretaker_id):
    caretaker = get_object_or_404(Caretaker, id=caretaker_id)

    if not caretaker.availability:
        messages.error(request, "This caretaker is currently unavailable.")
        return redirect('home')

    if request.method == 'POST':
        full_name = request.POST.get('full_names')
        phone_number = request.POST.get('phone_number')
        location = request.POST.get('location')
        book_date = request.POST.get('book_date')  # should be in yyyy-mm-dd format
        time = request.POST.get('time')  # should be in HH:MM format
        duration = request.POST.get('duration')  # in hours
        description = request.POST.get('desc')

        if not all([full_name, phone_number, location, book_date]):
            messages.error(request, "Please fill in all required fields.")
            return render(request, 'book.html', {'caretaker': caretaker})
        
        patient = Patient.objects.get(user=request.user)


        Booking.objects.create(
            caretaker=caretaker,
            patient=patient,
            patient_full_name=full_name,
            phone_number=phone_number,
            patient_location=location,
            book_date=book_date,
            requested_at=time,
            duration=duration,
            Description=description
        )

        messages.success(request, "Booking request sent successfully!")
        return redirect('user_home')  # or a confirmation page

    return render(request, 'book.html', {'caretaker': caretaker})


from django.views.decorators.http import require_POST
from django.http import HttpResponseForbidden
from django.core.mail import send_mail
from django.conf import settings



from django.core.mail import send_mail
from django.contrib import messages
from django.shortcuts import redirect

@login_required
def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)

    # Ensure the logged-in user owns the booking (security check)
    if hasattr(request.user, 'patient') and booking.patient.user == request.user:
        if booking.status == 'Pending':  # Only allow cancellation if it's still pending
            booking.status = 'Cancelled'
            booking.save()
            messages.success(request, "Your booking has been cancelled.")
        else:
            messages.warning(request, "You can only cancel bookings that are still pending.")
    else:
        messages.error(request, "You are not authorized to cancel this booking.")

    return redirect('notifications')  # redirect back to the notifications page

@login_required
def notifications_view(request):
    patient = get_object_or_404(Patient, user=request.user)
    pending_bookings = Booking.objects.filter(patient=patient, status='Pending')

    return render(request, 'notifications.html', {
        'pending_bookings': pending_bookings
    })

@login_required
def respond_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, caretaker__user=request.user)
    caretaker = booking.caretaker

    if request.method == 'POST':
        action = request.POST.get('response')

        if action == 'Accept':
            booking.status = 'Accepted'
            caretaker.availability = False
            messages.success(request, 'Booking accepted.')
            send_mail(
                subject="Your booking has been accepted",
                message=f"Dear {booking.patient_full_name},\n\nYour booking on {booking.book_date} has been accepted!",
                from_email="no-reply@careconnect.com",
                recipient_list=[booking.patient.user.email],
                fail_silently=True)

        elif action == 'Decline':
            booking.status = 'Declined'
            messages.info(request, 'Booking declined.')
            send_mail(
                subject="Your booking has been declined",
                message=f"Dear {booking.patient_full_name},\n\nSorry, your booking was declined.",
                from_email="no-reply@careconnect.com",
                recipient_list=[booking.patient.user.email],
                fail_silently=True
            )


        elif action == 'Cancel':
            booking.status = 'Cancelled'
            caretaker.availability = True
            messages.warning(request, 'Booking cancelled.')

        elif action == 'Complete':
            booking.status = 'Completed'
            caretaker.availability = True
            messages.success(request, 'Booking marked as completed.')

        booking.save()
        caretaker.save()

    return redirect('caretaker_home')




@login_required
def notifications(request):
    # Assuming request.user is the caretaker or linked to caretaker
    caretaker = get_object_or_404(Caretaker, user=request.user)
    bookings = Booking.objects.filter(caretaker=caretaker, status="Pending").order_by('-requested_at')

    return render(request, 'notification.html', {'bookings': bookings})

from django.shortcuts import render, redirect, get_object_or_404
from .models import Caretaker
from django.contrib.auth.decorators import login_required

@login_required
def caretaker_profile(request):
    caretaker = get_object_or_404(Caretaker, user=request.user)

    if request.method == "POST":
        caretaker.full_names = request.POST['full_names']
        caretaker.emails = request.POST['emails']
        caretaker.phone_numbers = request.POST['phone_numbers']
        caretaker.role = request.POST['role']
        caretaker.experiences = request.POST['experiences']
        caretaker.locations = request.POST['location']
        caretaker.rate = request.POST['rate']

        if 'image_url' in request.FILES:
            caretaker.image = request.FILES['image']

        caretaker.save()
        return redirect('caretaker_profile')

    edit_mode = request.GET.get("edit") == "true"

    return render(request, "profile.html", {
        "caretaker": caretaker,
        "edit": edit_mode
    })

@login_required
def delete_caretaker(request):
    caretaker = get_object_or_404(Caretaker, user=request.user)
    if request.method == "POST":
        caretaker.delete()
        return redirect("home")  # Redirect to home or login page


from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .models import Patient  # or your User Profile model
from django.contrib.auth.models import User

@login_required
def user_profile_view(request):
    profile = get_object_or_404(Patient, user=request.user)
    return render(request, 'user_profile.html', {'user_profile': profile})

@login_required
def update_user_profile(request):
    if request.method == 'POST':
        profile = get_object_or_404(Patient, user=request.user)
        profile.full_name = request.POST['full_name']
        profile.email = request.POST['email']
        profile.phone_number = request.POST['phone_number']
        profile.city = request.POST['city']
        if request.POST['password']:
            request.user.set_password(request.POST['password'])
            request.user.save()
        profile.save()
        return redirect('user_profile')
    return redirect('user_profile')

@login_required
def delete_user_profile(request):
    if request.method == 'POST':
        request.user.delete()
        return redirect('home')
    return redirect('user_profile')


