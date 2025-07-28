from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth import login, logout  # Add 'logout' to the imports
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.forms import AuthenticationForm
from django.utils import timezone
from datetime import date
from .models import DailyRecord, Ride
from .forms import SignUpForm, RideForm, PetrolExpenseForm
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from datetime import date, datetime


@login_required
def home(request):
    selected_date = request.GET.get('date', str(timezone.now().date()))
    
    try:
        selected_date = date.fromisoformat(selected_date)
    except (ValueError, TypeError):
        selected_date = timezone.now().date()
    
    return render(request, 'rides/home.html', {'selected_date': selected_date})
@login_required
def dashboard(request):
    """Main dashboard view showing rides and summary for selected date"""
    selected_date = request.GET.get('date', str(timezone.now().date()))
    
    try:
        selected_date = date.fromisoformat(selected_date)
    except (ValueError, TypeError):
        selected_date = timezone.now().date()
    
    # Get or create daily record for the selected date
    daily_record, created = DailyRecord.objects.get_or_create(
        user=request.user,
        date=selected_date,
        defaults={'petrol_expense': 0.00}
    )
    
    # Get rides ordered by timestamp (oldest first)
    rides = daily_record.rides.all().order_by('timestamp')
    
    context = {
        'daily_record': daily_record,
        'rides': rides,
        'selected_date': selected_date,
        'current_date': timezone.now().date()
    }
    return render(request, 'rides/dashboard.html', context)

@csrf_protect
@login_required
def add_ride(request):
    """Handle adding new rides while preserving the selected date"""
    selected_date = request.GET.get('date', str(timezone.now().date()))
    
    try:
        selected_date = date.fromisoformat(selected_date)
    except (ValueError, TypeError):
        selected_date = timezone.now().date()
    
    if request.method == 'POST':
        # Get or create daily record
        daily_record, created = DailyRecord.objects.get_or_create(
            user=request.user,
            date=selected_date,
            defaults={'petrol_expense': 0.00}
        )
        
        # Get device time from form or use current time
        device_time_str = request.POST.get('device_time', '')
        try:
            device_time = datetime.fromisoformat(device_time_str) if device_time_str else timezone.now()
        except ValueError:
            device_time = timezone.now()
        
        # Create new ride
        Ride.objects.create(
            daily_record=daily_record,
            earning=request.POST['earning'],
            commission=request.POST['commission'],
            device_time=device_time
        )
        messages.success(request, 'Ride added successfully!')
        return redirect(f"{reverse('home')}?date={selected_date}")
    
    return redirect(f"{reverse('home')}?date={selected_date}")

@csrf_protect
@login_required
def update_petrol(request):
    """Handle petrol expense updates while preserving the selected date"""
    selected_date = request.GET.get('date', str(timezone.now().date()))
    
    try:
        selected_date = date.fromisoformat(selected_date)
    except (ValueError, TypeError):
        selected_date = timezone.now().date()
    
    if request.method == 'POST':
        # Get or create daily record
        daily_record, created = DailyRecord.objects.get_or_create(
            user=request.user,
            date=selected_date,
            defaults={'petrol_expense': 0.00}
        )
        
        # Update petrol expense
        daily_record.petrol_expense = request.POST['petrol_expense']
        daily_record.save()
        messages.success(request, 'Petrol expense updated successfully!')
        return redirect(f"{reverse('home')}?date={selected_date}")
    
    return redirect(f"{reverse('home')}?date={selected_date}")

@login_required
def edit_ride(request, ride_id):
    """Handle editing existing rides while preserving the selected date"""
    selected_date = request.GET.get('date', str(timezone.now().date()))
    
    try:
        selected_date = date.fromisoformat(selected_date)
    except (ValueError, TypeError):
        selected_date = timezone.now().date()
    
    ride = get_object_or_404(Ride, id=ride_id, daily_record__user=request.user)
    
    if request.method == 'POST':
        form = RideForm(request.POST, instance=ride)
        if form.is_valid():
            form.save()
            messages.success(request, 'Ride updated successfully!')
            return redirect(f"{reverse('home')}?date={selected_date}")
    else:
        form = RideForm(instance=ride)
    
    return render(request, 'rides/edit_ride.html', {
        'form': form,
        'ride': ride,
        'selected_date': selected_date
    })

@login_required
def delete_ride(request, ride_id):
    """Handle ride deletion while preserving the selected date"""
    selected_date = request.GET.get('date', str(timezone.now().date()))
    
    try:
        selected_date = date.fromisoformat(selected_date)
    except (ValueError, TypeError):
        selected_date = timezone.now().date()
    
    ride = get_object_or_404(Ride, id=ride_id, daily_record__user=request.user)
    
    if request.method == 'POST':
        ride.delete()
        messages.success(request, 'Ride deleted successfully!')
        return redirect(f"{reverse('home')}?date={selected_date}")
    
    return render(request, 'rides/confirm_delete.html', {
        'ride': ride,
        'selected_date': selected_date
    })


def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')  # Changed from 'dashboard' to 'home'
    else:
        form = AuthenticationForm()
    return render(request, 'rides/login.html', {'form': form})

def user_signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = SignUpForm()
    
    return render(request, 'rides/signup.html', {'form': form})

def user_logout(request):
    logout(request)
    return redirect('login')
