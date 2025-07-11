from django.urls import path
from . import views

urlpatterns = [
    path('signup/caretaker/', views.caretaker_signup, name='signup_care'),
    path('signup/patient/', views.patient_signup, name='signup_user'),
    path('login/', views.login_view, name='login'),
    path('', views.home, name='home'),
    # path('browse/', views.browse, name='browse'),
    path('logout/', views.logout_view, name='logout'),
    path("profile_update/", views.profile_update, name="profile_update"),
    path('respond-booking/<int:booking_id>/', views.respond_booking, name='respond_booking'),
    path('browse/', views.caretaker_list_view, name='browse'),
    # path('book/', views.book, name='book'),
    path('book/<int:caretaker_id>/', views.book_caretaker, name='book'),
    # path('book/<int:caretaker_id>/', views.book_caretaker, name='book'),

    path('notification/', views.notifications_view, name='notifications'),
    path('cancel-booking/<int:booking_id>/', views.cancel_booking, name='cancel_booking'),

    path("notification/", views.notifications, name="notifications"),
    path('profile/', views.caretaker_profile, name='caretaker_profile'),
    path('profile/delete/', views.delete_caretaker, name='delete_caretaker'),
    path('profiles/', views.user_profile_view, name='user_profile'),
    path('profile/update/', views.update_user_profile, name='update_user_profile'),
    path('profile/delete/', views.delete_user_profile, name='delete_user_profile'),
    path('user_home/', views.user_home, name='user_home'),
    path('caretaker_home/', views.caretaker_home, name='caretaker_home'),
    path('api/caretakers/', views.available_caretakers, name='available_caretakers'),

]

# bookings/respond/<int:booking_id>/


    # path('dashboard/', views.dashboard, name='dashboard'),
    # path('logout/', views.logout_view, name='logout'),

