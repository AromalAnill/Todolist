from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.utils import timezone
from calendar import monthcalendar
from datetime import datetime, timedelta
import json

from .forms import CustomUserCreationForm, CustomAuthenticationForm, TaskForm
from .models import Task, CustomUser


def register(request):
    """Handle user registration."""
    if request.user.is_authenticated:
        return redirect('calendar')
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            context = {
                'success': True,
                'message': 'Registration successful! Please log in.'
            }
            return render(request, 'tasks/register.html', {'form': form, **context})
        else:
            context = {
                'success': False,
                'errors': form.errors
            }
    else:
        form = CustomUserCreationForm()
        context = {}
    
    return render(request, 'tasks/register.html', {'form': form, **context})


def login_view(request):
    """Handle user login using phone number."""
    if request.user.is_authenticated:
        return redirect('calendar')
    
    context = {}
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            context = {
                'success': True,
                'message': 'Login Successful'
            }
            # Return success response for AJAX
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'redirect': '/calendar/'})
            return redirect('calendar')
        else:
            # Extract error message
            error_msg = 'Password Incorrect / User Not Found'
            context = {
                'success': False,
                'message': error_msg,
                'errors': form.errors
            }
    else:
        form = CustomAuthenticationForm()
    
    context['form'] = form
    return render(request, 'tasks/login.html', context)


def logout_view(request):
    """Handle user logout."""
    logout(request)
    return redirect('login')


@login_required(login_url='login')
def calendar_view(request):
    """Display interactive calendar with tasks."""
    today = timezone.now().date()
    
    # Get current month and year from request or use today
    if 'year' in request.GET and 'month' in request.GET:
        year = int(request.GET['year'])
        month = int(request.GET['month'])
        current_date = datetime(year, month, 1).date()
    else:
        current_date = today
    
    # Get all tasks for the user in this month
    tasks = Task.objects.filter(
        user=request.user,
        due_date__month=current_date.month,
        due_date__year=current_date.year
    )
    
    # Build task dictionary for easy lookup
    task_dict = {}
    for task in tasks:
        day = task.due_date.day
        if day not in task_dict:
            task_dict[day] = []
        task_dict[day].append(task)
    
    # Generate calendar
    calendar_data = monthcalendar(current_date.year, current_date.month)
    
    # Calculate previous and next month
    if current_date.month == 1:
        prev_month = datetime(current_date.year - 1, 12, 1).date()
        next_month = datetime(current_date.year, 2, 1).date()
    elif current_date.month == 12:
        prev_month = datetime(current_date.year, 11, 1).date()
        next_month = datetime(current_date.year + 1, 1, 1).date()
    else:
        prev_month = datetime(current_date.year, current_date.month - 1, 1).date()
        next_month = datetime(current_date.year, current_date.month + 1, 1).date()
    
    context = {
        'today': today,
        'current_date': current_date,
        'calendar': calendar_data,
        'task_dict': task_dict,
        'prev_month': prev_month,
        'next_month': next_month,
        'month_year': current_date.strftime('%B %Y'),
    }
    
    return render(request, 'tasks/calendar.html', context)


@login_required(login_url='login')
@require_http_methods(["POST"])
def add_task(request):
    """Handle adding a new task via AJAX."""
    try:
        data = json.loads(request.body)
        title = data.get('title')
        description = data.get('description', '')
        due_date_str = data.get('due_date')
        
        if not title or not due_date_str:
            return JsonResponse({
                'success': False,
                'error': 'Title and due date are required.'
            }, status=400)
        
        # Parse and validate date
        try:
            due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date()
        except ValueError:
            return JsonResponse({
                'success': False,
                'error': 'Invalid date format.'
            }, status=400)
        
        # Check if date is not in the past
        if due_date < timezone.now().date():
            return JsonResponse({
                'success': False,
                'error': 'Cannot add tasks to dates in the past.'
            }, status=400)
        
        # Create task
        task = Task.objects.create(
            user=request.user,
            title=title,
            description=description,
            due_date=due_date
        )
        
        return JsonResponse({
            'success': True,
            'task_id': task.id,
            'message': 'Task added successfully!'
        })
    
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid request data.'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required(login_url='login')
@require_http_methods(["DELETE"])
def delete_task(request, task_id):
    """Handle deleting a task."""
    try:
        task = Task.objects.get(id=task_id, user=request.user)
        task.delete()
        return JsonResponse({
            'success': True,
            'message': 'Task deleted successfully!'
        })
    except Task.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Task not found.'
        }, status=404)


@login_required(login_url='login')
@require_http_methods(["PATCH"])
def toggle_task(request, task_id):
    """Handle toggling task completion status."""
    try:
        task = Task.objects.get(id=task_id, user=request.user)
        task.is_completed = not task.is_completed
        task.save()
        return JsonResponse({
            'success': True,
            'is_completed': task.is_completed,
            'message': 'Task updated successfully!'
        })
    except Task.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Task not found.'
        }, status=404)


@login_required(login_url='login')
def get_tasks_for_date(request):
    """Get tasks for a specific date via AJAX."""
    date_str = request.GET.get('date')
    
    if not date_str:
        return JsonResponse({
            'success': False,
            'error': 'Date is required.'
        }, status=400)
    
    try:
        due_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        tasks = Task.objects.filter(user=request.user, due_date=due_date)
        
        tasks_data = [
            {
                'id': task.id,
                'title': task.title,
                'description': task.description,
                'is_completed': task.is_completed
            }
            for task in tasks
        ]
        
        return JsonResponse({
            'success': True,
            'tasks': tasks_data,
            'date': date_str
        })
    except ValueError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid date format.'
        }, status=400)
