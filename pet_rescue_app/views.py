from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import PetReport, Notification
from .serializers import PetReportSerializer, NotificationSerializer


# ======================= API VIEWSETS =======================

class PetReportViewSet(viewsets.ModelViewSet):
    serializer_class = PetReportSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return PetReport.objects.all()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'])
    def search(self, request):
        query = request.query_params.get('q')
        reports = PetReport.objects.all()
        if query:
            reports = reports.filter(
                Q(pet_name__icontains=query) | Q(pet_type__icontains=query) |
                Q(breed__icontains=query) | Q(color__icontains=query) |
                Q(location__icontains=query) | Q(description__icontains=query)
            )
        serializer = PetReportSerializer(reports, many=True)
        return Response(serializer.data)


class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)


# JSON endpoint for navbar badge polling
@login_required
def unread_count_api(request):
    count = Notification.objects.filter(user=request.user, is_read=False).count()
    # Return the latest unread message text (if any) for popup
    latest = Notification.objects.filter(user=request.user, is_read=False).order_by('-created_at').first()
    new_message = latest.message if latest else None
    return JsonResponse({'count': count, 'new_message': new_message})


# ======================= AUTH VIEWS =======================

def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'Registration successful! Please sign in with your new account, {user.username}.')
            return redirect('login')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserCreationForm()

    return render(request, 'register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            
            # Remember me logic
            if not request.POST.get('remember'):
                request.session.set_expiry(0) # Expire on browser close

            messages.success(request, f'Welcome back, {user.username}!')
            return redirect(request.GET.get('next', 'dashboard'))
        else:
            messages.error(request, 'Invalid username or password. Please try again.')
    else:
        form = AuthenticationForm()

    return render(request, 'login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, 'You have been successfully logged out.')
    return redirect('login')


# ======================= HOME =======================

def home_view(request):
    # Removed mandatory redirect to dashboard for logged-in users 
    # to allow them to browse the landing page.
    
    lost_pets = PetReport.objects.filter(report_type='Lost').order_by('-created_at')[:6]
    found_pets = PetReport.objects.filter(report_type='Found').order_by('-created_at')[:6]
    total_reports = PetReport.objects.count()
    # "Happy Reunions" now counts pets that are 'Closed' (Journey complete)
    reunited_count = PetReport.objects.filter(status='Closed').count()

    unread_count = 0
    if request.user.is_authenticated:
        unread_count = Notification.objects.filter(user=request.user, is_read=False).count()

    return render(request, 'home.html', {
        'lost_pets': lost_pets,
        'found_pets': found_pets,
        'total_reports': total_reports,
        'accepted_reports': reunited_count,
        'unread_count': unread_count,
    })


# ======================= DASHBOARD =======================

@login_required
def dashboard(request):
    # User's own reports
    my_reports = PetReport.objects.filter(user=request.user).order_by('-created_at')
    my_lost_reports = my_reports.filter(report_type='Lost')
    my_found_reports = my_reports.filter(report_type='Found')

    # Community reports (excluding user's own to avoid duplication or just all)
    # Let's show all latest reports to keep the user informed
    community_lost = PetReport.objects.filter(report_type='Lost').exclude(user=request.user).order_by('-created_at')[:10]
    community_found = PetReport.objects.filter(report_type='Found').exclude(user=request.user).order_by('-created_at')[:10]

    unread_notifications = Notification.objects.filter(user=request.user, is_read=False).count()

    context = {
        # My reports data
        'reports': my_reports,
        'lost_reports': my_lost_reports,
        'found_reports': my_found_reports,
        'total_reports': my_reports.count(),
        'pending_reports': my_reports.filter(status='Pending').count(),
        'accepted_reports': my_reports.filter(status='Accepted').count(),
        'rejected_reports': my_reports.filter(status='Rejected').count(),
        'closed_reports': my_reports.filter(status='Closed').count(),
        'lost_count': my_lost_reports.count(),
        'found_count': my_found_reports.count(),

        # Community reports data
        'community_lost': community_lost,
        'community_found': community_found,

        'unread_notifications': unread_notifications,
        'unread_count': unread_notifications,
    }
    return render(request, 'dashboard.html', context)


# ======================= PET REPORTS =======================

PET_TYPES = ['Dog', 'Cat', 'Bird', 'Rabbit', 'Hamster', 'Other']


@login_required
def add_report_page(request):
    # Determine type from query param or POST
    report_type_param = request.GET.get('type', 'lost').capitalize()
    if report_type_param not in ['Lost', 'Found']:
        report_type_param = 'Lost'

    if request.method == 'POST':
        pet_name = request.POST.get('pet_name', '').strip()
        pet_type = request.POST.get('pet_type', '').strip()
        breed = request.POST.get('breed', '').strip()
        color = request.POST.get('color', '').strip()
        location = request.POST.get('location', '').strip()
        description = request.POST.get('description', '').strip()
        report_type = request.POST.get('report_type', 'Lost')
        phone_number = request.POST.get('phone_number', '').strip()

        pet_image = request.FILES.get('pet_image')

        # Conditional checking: pet_name is mandatory ONLY for Lost pets
        required_fields = [pet_type, breed, color, location, phone_number]
        if report_type == 'Lost':
            required_fields.append(pet_name)

        if not all(required_fields):
            messages.error(request, 'Please fill in all required fields.')
            return render(request, 'add_report.html', {
                'report_type': report_type,
                'pet_types': PET_TYPES,
                'data': request.POST, # Send back data to pre-populate fields
            })

        new_report = PetReport.objects.create(
            user=request.user,
            pet_name=pet_name,
            pet_type=pet_type,
            breed=breed,
            color=color,
            location=location,
            description=description,
            report_type=report_type,
            phone_number=phone_number,
            pet_image=pet_image,
        )

        # Automated Matching Logic
        if new_report.report_type == 'Found':
            # Search for "Lost" pets that might match this "Found" pet
            potential_matches = PetReport.objects.filter(
                report_type='Lost',
                pet_type__iexact=new_report.pet_type,
                breed__iexact=new_report.breed
            ).exclude(user=request.user)

            # If the finder provided a name, refine the search for a specific name match
            if new_report.pet_name:
                potential_matches = potential_matches.filter(pet_name__iexact=new_report.pet_name)

            for lost_report in potential_matches:
                Notification.objects.create(
                    user=lost_report.user,
                    message=f"Exciting news! A {new_report.pet_type} matching your report for '{lost_report.pet_name}' has been found in {new_report.location}. Check the dashboard to contact the finder!"
                )

        return render(request, 'add_report.html', {
            'success': True,
            'report_type': report_type,
            'pet_types': PET_TYPES,
        })

    return render(request, 'add_report.html', {
        'report_type': report_type_param,
        'pet_types': PET_TYPES,
    })


@login_required
def edit_report(request, pk):
    report = get_object_or_404(PetReport, pk=pk, user=request.user)

    if request.method == 'POST':
        pet_name = request.POST.get('pet_name', '').strip()
        pet_type = request.POST.get('pet_type', '').strip()
        breed = request.POST.get('breed', '').strip()
        color = request.POST.get('color', '').strip()
        location = request.POST.get('location', '').strip()
        description = request.POST.get('description', '').strip()
        report_type = request.POST.get('report_type', 'Lost')
        phone_number = request.POST.get('phone_number', '').strip()

        # Conditional checking: pet_name is mandatory ONLY for Lost pets
        required_fields = [pet_type, breed, color, location, phone_number]
        if report_type == 'Lost':
            required_fields.append(pet_name)

        if not all(required_fields):
            messages.error(request, 'Please fill in all required fields.')
            return render(request, 'edit_report.html', {'report': report})

        # Update the report object
        report.pet_name = pet_name
        report.pet_type = pet_type
        report.breed = breed
        report.color = color
        report.location = location
        report.description = description
        report.report_type = report_type
        report.phone_number = phone_number

        if request.FILES.get('pet_image'):
            report.pet_image = request.FILES.get('pet_image')

        report.save()
        messages.success(request, f'Report for "{report.pet_name}" updated successfully.')
        return redirect('dashboard')

    return render(request, 'edit_report.html', {'report': report, 'pet_types': PET_TYPES})


@login_required
@require_POST
def delete_report(request, pk):
    report = get_object_or_404(PetReport, pk=pk, user=request.user)
    name = report.pet_name
    report.delete()
    messages.success(request, f'Report for "{name}" has been deleted.')
    return redirect('dashboard')


# ======================= SEARCH =======================

def search_pets(request):
    """
    Handles keyword searching and filtering for all lost and found pets.
    """
    query = request.GET.get('q', '').strip()
    filter_type = request.GET.get('type', '').strip() or None
    filter_pet_type = request.GET.get('pet_type', '').strip() or None
    filter_status = request.GET.get('status', '').strip() or None
    filter_breed = request.GET.get('breed', '').strip() or None
    filter_color = request.GET.get('color', '').strip() or None

    # Initial queryset
    results = PetReport.objects.all().order_by('-created_at')

    # Smart Keyword Search: Split query into words to match better
    if query:
        words = query.split()
        for word in words:
            results = results.filter(
                Q(pet_name__icontains=word) | 
                Q(pet_type__icontains=word) |
                Q(breed__icontains=word) | 
                Q(color__icontains=word) |
                Q(location__icontains=word) | 
                Q(description__icontains=word) |
                Q(phone_number__icontains=word)
            )

    # Selective property filters
    if filter_type:
        results = results.filter(report_type=filter_type)
    if filter_pet_type:
        results = results.filter(pet_type__iexact=filter_pet_type)
    if filter_status:
        results = results.filter(status=filter_status)
    if filter_breed:
        results = results.filter(breed__icontains=filter_breed)
    if filter_color:
        results = results.filter(color__icontains=filter_color)

    # Separated results for tabs in the search UI
    lost_results = results.filter(report_type='Lost')
    found_results = results.filter(report_type='Found')

    # Header count for notifications
    unread_count = 0
    if request.user.is_authenticated:
        unread_count = Notification.objects.filter(user=request.user, is_read=False).count()

    # Pass all variables directly into the template context
    context = {
        'results': results,
        'lost_results': lost_results,
        'found_results': found_results,
        'lost_count': lost_results.count(),
        'found_count': found_results.count(),
        'query': query,
        'filter_type': filter_type,
        'filter_pet_type': filter_pet_type,
        'filter_status': filter_status,
        'filter_breed': filter_breed,
        'filter_color': filter_color,
        'unread_count': unread_count,
    }
    return render(request, 'search.html', context)


# ======================= NOTIFICATIONS =======================

@login_required
def notifications_page(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    unread_count = notifications.filter(is_read=False).count()
    # Mark all as read after loading
    notifications.filter(is_read=False).update(is_read=True)

    return render(request, 'notifications.html', {
        'notifications': notifications,
        'unread_count': unread_count,
        'unread_notifications': unread_count,
    })


@login_required
@require_POST
def mark_all_read(request):
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    messages.success(request, 'All notifications marked as read.')
    return redirect('notifications_page')