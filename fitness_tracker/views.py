import json
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Workout, Profile, Step,Nutrition
from django.utils.timezone import now

# Home Page (Login & Signup)
def homepage(request):
    if request.user.is_authenticated:
        print("User:", request.user, "Authenticated:", request.user.is_authenticated)
        return redirect('dashboard') 
    return render(request, 'homepage.html')

# Signup View
def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('setup_profile')
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})

# Login View
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

# Logout View
def logout_view(request):
    logout(request)
    return redirect('homepage')

# Profile Setup (Age, Weight, Height, Gender, DOB)
@login_required
def setup_profile(request):
    if request.method == 'POST':
        age = request.POST.get('age')
        weight = request.POST.get('weight')
        height = request.POST.get('height')
        gender = request.POST.get('gender')
        dob = request.POST.get('dob')


        Profile.objects.update_or_create(
            user=request.user,
            defaults={'age': age, 'weight': weight, 'height': height, 'gender': gender, 'dob': dob,}
        )
        return redirect('dashboard')
    
    return render(request, 'setup_profile.html')

# Dashboard
@login_required
def dashboard(request):
    user = request.user
    workouts = Workout.objects.filter(user=user).order_by('-date')[:10]
    steps = Step.objects.filter(user=user).order_by('-date')[:10]
    nutrition = Nutrition.objects.filter(user=user).order_by('-date')[:10]
    
    # Get last 7 days for chart
    date_list = [timezone.now().date() - timedelta(days=i) for i in range(7)]
    date_list.reverse()
    
    chart_data = {
        'labels': [date.strftime('%Y-%m-%d') for date in date_list],
        'workout': [],
        'steps': [],
        'nutrition': []
    }
    
    for date in date_list:
        chart_data['workout'].append(
            sum(w.calories for w in Workout.objects.filter(user=user, date=date)))
        chart_data['steps'].append(
            sum(s.calories_burned() for s in Step.objects.filter(user=user, date=date)))
        chart_data['nutrition'].append(
            sum(n.calories for n in Nutrition.objects.filter(user=user, date=date)))
        
    return render(request, 'dashboard.html', {
        'workouts': workouts,
        'steps': steps,
        'nutrition': nutrition,
        'chart_data': json.dumps(chart_data),
        'calorie_deficit': calculate_deficit(user),
    })



@login_required
def add_workout(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        calories = int(request.POST.get('calories'))

        if not name or calories <= 0:
            return JsonResponse({'success': False, 'message': 'Invalid input'})

        Workout.objects.create(user=request.user, name=name, calories=calories, date=now())
        return JsonResponse({'success': True, 'message': 'Workout added successfully'})

    return JsonResponse({'success': False, 'message': 'Invalid request method'})

# Delete Workout
@login_required
def delete_workout(request, workout_id):
    try:
        workout = Workout.objects.get(id=workout_id, user=request.user)
        workout.delete()
        return JsonResponse({'success': True, 'message': 'Workout deleted successfully'})
    except Workout.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Workout not found'})

# Get Workouts for Logged-in User
@login_required
def get_workouts(request):
    workouts = Workout.objects.filter(user=request.user).order_by('-date')
    workout_list = [{'id': w.id, 'name': w.name, 'calories': w.calories, 'date': w.date.strftime('%Y-%m-%d')} for w in workouts]
    return JsonResponse({'workouts': workout_list})

# Steps Input (Convert Steps to Calories)
@login_required
@login_required
def add_steps(request):
    if request.method == 'POST':
        steps = request.POST.get('steps')
        if steps and steps.isdigit():
            steps = int(steps)
            if steps > 0:
                step_object = Step.objects.create(user=request.user, steps_taken=steps, date=now())
                return JsonResponse({
                    'success': True,
                    'step': {
                        'id': step_object.id,
                        'steps_taken': step_object.steps_taken,
                        'calories_burned': step_object.calories_burned(),
                        'date': step_object.date.strftime('%Y-%m-%d')
                    }
                })
            else:
                return JsonResponse({'success': False, 'error': 'Step count must be greater than zero.'}, status=400)
        else:
            return JsonResponse({'success': False, 'error': 'Invalid step count.'}, status=400)
    return JsonResponse({'success': False, 'error': 'Invalid request method.'}, status=405)

# Get Steps Data
@login_required
def get_steps(request):
    steps = Step.objects.filter(user=request.user).order_by('-date')
    step_list = [{'id': s.id, 'steps': s.steps, 'calories_burned': s.calories_burned, 'date': s.date.strftime('%Y-%m-%d')} for s in steps]
    return JsonResponse({'steps': step_list})

# @login_required
# def get_calorie_deficit(request):
#     user = request.user

#     try:
#         user_profile = Profile.objects.get(user=user)
#     except Profile.DoesNotExist:
#         return JsonResponse({'error': 'User profile not found'}, status=400)

#     # Calculate BMR
#     if user_profile.gender == 'Male':
#         bmr = 88.36 + (13.4 * float(user_profile.weight)) + (4.8 * float(user_profile.height)) - (5.7 * float(user_profile.age))
#     else:
#         bmr = 447.6 + (9.2 * float(user_profile.weight)) + (3.1 * float(user_profile.height)) - (4.3 * float(user_profile.age))

#     # Total Calories Burned (Workouts + Steps)
#     workouts = Workout.objects.filter(user=user)
#     steps = Step.objects.filter(user=user)
#     total_calories_burned = (
#     sum(workout.calories for workout in workouts) +
#     sum(step.calories_burned() for step in steps)
#     )

#     # Calculate calorie deficit
#     calorie_deficit = round(bmr - total_calories_burned, 2)

#     return JsonResponse({'deficit': calorie_deficit})

@login_required
def delete_step(request, step_id):
    try:
        step = Step.objects.get(id=step_id, user=request.user)
        step.delete()
        return JsonResponse({'success': True, 'message': 'Step entry deleted successfully'})
    except Step.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Step entry not found'})
   
def calculate_deficit(user):
    try:
        profile = Profile.objects.get(user=user)
        if profile.gender == 'Male':
            bmr = 88.36 + (13.4 * float(profile.weight)) + (4.8 * float(profile.height)) - (5.7 * float(profile.age))
        else:
            bmr = 447.6 + (9.2 * float(profile.weight)) + (3.1 * float(profile.height)) - (4.3 * float(profile.age))
        
        today = timezone.now().date()
        burned = sum(w.calories for w in Workout.objects.filter(user=user, date=today)) + \
                 sum(s.calories_burned() for s in Step.objects.filter(user=user, date=today))
        consumed = sum(n.calories for n in Nutrition.objects.filter(user=user, date=today))
        
        return round(bmr + consumed - burned, 2)
    except Profile.DoesNotExist:
        return 0
    
@login_required
def add_nutrition(request):
    if request.method == 'POST':
        food_name = request.POST.get('food_name')
        calories = request.POST.get('calories')
        date = request.POST.get('date') or timezone.now().date()
        
        if food_name and calories:
            Nutrition.objects.create(
                user=request.user,
                food_name=food_name,
                calories=calories,
                date=date
            )
            return JsonResponse({'success': True})
    
    return JsonResponse({'success': False, 'error': 'Invalid data'}, status=400)

@login_required
def delete_nutrition(request, nutrition_id):
    try:
        nutrition = Nutrition.objects.get(id=nutrition_id, user=request.user)
        nutrition.delete()
        return JsonResponse({'success': True})
    except Nutrition.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Entry not found'}, status=404)
    
@login_required
def get_recent_activities(request):
    # Combine workouts, steps, and nutrition into a single activity feed
    workouts = Workout.objects.filter(user=request.user).order_by('-date')[:5]
    steps = Step.objects.filter(user=request.user).order_by('-date')[:5]
    nutrition = Nutrition.objects.filter(user=request.user).order_by('-date')[:5]
    
    activities = []
    for workout in workouts:
        activities.append({
            'type': 'workout',
            'date': workout.date,
            'name': workout.name,
            'calories': workout.calories,
            'id': workout.id
        })
    
    for step in steps:
        activities.append({
            'type': 'steps',
            'date': step.date,
            'name': f"{step.steps_taken} steps",
            'calories': step.calories_burned(),
            'id': step.id
        })
        
    for item in nutrition:
        activities.append({
            'type': 'nutrition',
            'date': item.date,
            'name': item.food_name,
            'calories': item.calories,
            'id': item.id
        })
    
    # Sort by date (newest first)
    activities.sort(key=lambda x: x['date'], reverse=True)
    
    return render(request, 'activity_feed.html', {'activities': activities[:10]})

@login_required
def get_chart_data(request):
    # Same logic as your current dashboard view for chart data
    date_range = 7
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=date_range-1)
    date_list = [start_date + timedelta(days=x) for x in range(date_range)]
    
    chart_data = []
    for date in date_list:
        chart_data.append({
            'date': date.strftime('%Y-%m-%d'),
            'workout': sum(w.calories for w in Workout.objects.filter(user=request.user, date=date)),
            'steps': sum(s.calories_burned() for s in Step.objects.filter(user=request.user, date=date)),
            'nutrition': sum(n.calories for n in Nutrition.objects.filter(user=request.user, date=date))
        })
    
    return JsonResponse({
        'labels': [item['date'] for item in chart_data],
        'workout': [item['workout'] for item in chart_data],
        'steps': [item['steps'] for item in chart_data],
        'nutrition': [item['nutrition'] for item in chart_data]
    })