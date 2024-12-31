from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("register/", views.register, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("add-expense/", views.add_expense, name="add_expense"),
    path("view-expenses/", views.view_expenses, name="view_expenses"),
    path("financial-report/", views.financial_report, name="financial_report"),
    path("profile/", views.profile, name="profile"),
    path("update-profile/", views.profile, name="update_profile"),  
    path("change-password/", views.change_password, name="change_password"),  
    path("track-expenses/", views.view_expenses, name="track_expenses"), 
    path("financial-reports/", views.financial_report, name="financial_reports"), 
    path("settings/", views.settings, name="settings"), 
    path("view-balances", views.view_balances, name="view_balances"), 
    path('dashboard/<int:account_id>/', views.dashboard, name='account_dashboard'),
    path("expenses/", views.expenses, name="expenses"),
]