from django.urls import path
from . import views

urlpatterns = [
    # Authentication
    path('', views.homepage, name='homepage'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # User Profile Setup
    path('setup_profile/', views.setup_profile, name='setup_profile'),

    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),

    # Workout Management
    path('get_workouts/', views.get_workouts, name='get_workouts'),
    path('add_workout/', views.add_workout, name='add_workout'),
    path('delete_workout/<int:workout_id>/', views.delete_workout, name='delete_workout'),
    # path('get_calorie_deficit/', views.get_calorie_deficit, name='get_calorie_deficit'),

    # Step Tracking
    path('add_steps/', views.add_steps, name='add_steps'),
    path('get_steps/', views.get_steps, name='get_steps'),
    path('delete_steps/<int:step_id>/', views.delete_step, name='delete_step'),

    path('add_nutrition/', views.add_nutrition, name='add_nutrition'),
    path('delete_nutrition/<int:nutrition_id>/', views.delete_nutrition, name='delete_nutrition'),
    path('get_recent_activities/', views.get_recent_activities, name='get_recent_activities'),
    path('get_chart_data/', views.get_chart_data, name='get_chart_data'),
]

