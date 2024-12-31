from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from .models import UserProfile, BankAccount, Expense
from .forms import UserRegistrationForm, UserProfileForm, CustomPasswordChangeForm, ExpenseForm


def index(request):
    if not request.user.is_authenticated:
        return redirect('register')
    return render(request, 'tracker/index.html')


def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        return render(request, "tracker/login.html", {"message": "Invalid username and/or password."})
    return render(request, "tracker/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.user.is_authenticated:
        return redirect('index')
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            login(request, user)
            return redirect('index')
    else:
        form = UserRegistrationForm()
    return render(request, "tracker/register.html", {'form': form})


@login_required
def dashboard(request, account_id=None):
    account = None
    if account_id:
        try:
            account = BankAccount.objects.get(id=account_id, user=request.user)
        except BankAccount.DoesNotExist:
            return redirect('view_balances')  

    expenses = Expense.objects.filter(user=request.user)
    if account:
        expenses = expenses.filter(account=account)

    total_expenses = sum(expense.amount for expense in expenses)
    total_balance = account.balance if account else None

    context = {
        'account': account,
        'expenses': expenses,
        'total_expenses': total_expenses,
        'total_balance': total_balance,
    }
    return render(request, 'tracker/dashboard.html', context)


@login_required
def add_expense(request):
    if request.method == "POST":
        form = ExpenseForm(request.POST)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.user = request.user
            expense.save()
            return redirect('dashboard')
    else:
        form = ExpenseForm()
    return render(request, 'tracker/add_expense.html', {'form': form})


@login_required
def view_expenses(request):
    expenses = Expense.objects.filter(user=request.user)
    return render(request, 'tracker/view_expenses.html', {'expenses': expenses})


@login_required
def financial_report(request):
    expenses = Expense.objects.filter(user=request.user)
    total_expenses = sum(expense.amount for expense in expenses)
    return render(request, 'tracker/financial_report.html', {'total_expenses': total_expenses, 'expenses': expenses})


@login_required
def profile(request):
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    if request.method == "POST":
        form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = UserProfileForm(instance=user_profile)
    return render(request, 'tracker/profile.html', {'form': form})


@login_required
def change_password(request):
    if request.method == 'POST':
        form = CustomPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            return redirect('dashboard')
    else:
        form = CustomPasswordChangeForm(request.user)
    return render(request, 'tracker/change_password.html', {'form': form})


@login_required
def settings(request):
    return render(request, 'tracker/settings.html')


@login_required
def view_balances(request):
    bank_accounts = BankAccount.objects.filter(user=request.user)
    total_balance = sum(account.balance for account in bank_accounts)

    if request.method == 'POST':
        account_name = request.POST.get('account_name')
        account_balance = request.POST.get('account_balance')
        if account_name and account_balance:
            BankAccount.objects.create(
                user=request.user,
                name=account_name,
                balance=float(account_balance)
            )
            return redirect('dashboard')

    context = {
        'bank_accounts': bank_accounts,
        'total_balance': total_balance,
    }
    return render(request, 'tracker/view_balances.html', context)

from .models import Expense  # Make sure to import your Expense model
from .forms import ExpenseForm  # Import the form you create

@login_required
def expenses(request):
    if request.method == 'POST':
        # Create a new expense from the submitted form data
        form = ExpenseForm(request.POST)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.user = request.user  # Associate the expense with the logged-in user
            expense.save()
            return redirect('expenses')  # Redirect to the same page after saving

    else:
        form = ExpenseForm()  # Create an empty form for GET requests

    expenses = Expense.objects.filter(user=request.user)  # Fetch user's expenses
    return render(request, 'tracker/expenses.html', {'expenses': expenses, 'form': form})