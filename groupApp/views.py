from django.shortcuts import render, redirect
from django.contrib import messages
from .models import *
import bcrypt
from django.db.models import Count


# Create your views here.


def index(request):
    request.session.flush()
    return render(request, 'register.html')

def register(request):
    if request.method == "POST":
        errors = User.objects.reg_validator(request.POST)
        if len(errors) != 0:
            for key, value in errors.items():
                messages.error(request, value)
            return  redirect('/')
        hashed_pw = bcrypt.hashpw(request.POST['password'].encode(), bcrypt.gensalt()).decode()
        new_user = User.objects.create(
            first_name = request.POST['first_name'], 
            last_name = request.POST['last_name'],
            email = request.POST['email'],
            password = hashed_pw,
        )
        request.session['user_id'] = new_user.id
        return redirect('/main_page')
    return redirect('/')

def login(request):
    if request.method == "POST":
        errors = User.objects.login_validator(request.POST)
        if len(errors) > 0:
            for key, value in errors.items():
                messages.error(request, value)
                return  redirect('/')
    if request.method == 'POST':
        users_with_email = User.objects.filter(email=request.POST['email'])
        if users_with_email:
            user = users_with_email[0]
        if bcrypt.checkpw(request.POST['password'].encode(), user.password.encode()):
            request.session['user_id'] = user.id
            request.session['greeting'] = user.first_name
            return redirect('/main_page')
        messages.error(request, "Email or Password incorrect")
    return redirect('/')

def logout(request):
    request.session.flush()
    return redirect('/')

def main_page(request):
    if 'user_id' not in request.session:
        return redirect('/')
    context = {
        'current_user': User.objects.get(id=request.session['user_id']),
        'all_groups': Group.objects.annotate(members=Count('users_that_joined')).order_by('-members'),
    }
    return render(request, 'main_page.html', context)

def create_group(request):
    if 'user_id' not in request.session:
        return redirect('/')
    if request.method == "POST":
        errors = Group.objects.group_validator(request.POST)
        if len(errors) > 0:
            for key, value in errors.items():
                messages.error(request, value)
            return redirect('/main_page')
        else:
            user = User.objects.get(id=request.session['user_id'])
            organization = Group.objects.create(
                name=request.POST['org_name'],
                description=request.POST['description'],
                owner=User.objects.get(id=request.session['user_id'])
            )
            messages.success(request, "Organization created")
            user.users_joined_for.add(organization)
            return redirect('/main_page')
    return redirect('/main_page')

def show_group(request, group_id):
    orgs_with_id = Group.objects.filter(id=group_id)
    if len(orgs_with_id) == 0:
        return redirect('/main_page')
    context = {
        'one_group': Group.objects.get(id=group_id),
        'current_user': User.objects.get(id=request.session['user_id']),
        'all_groups': Group.objects.all(),
    }
    return render(request, 'viewpage.html', context)

def joined_groups(request, group_id):
    if 'user_id' not in request.session:
        return redirect('/')
    if request.method == "POST":
        one_group = Group.objects.get(id=group_id)
        current_user = User.objects.get(id=request.session['user_id'])
        one_group.users_that_joined.add(current_user)
        current_user.users_joined_for.add(one_group)
        return redirect(f'/group/{group_id}')

def leave_group(request, group_id):
    if 'user_id' not in request.session:
        return redirect('/')
    if request.method == "POST":
        one_group = Group.objects.get(id=group_id)
        current_user = User.objects.get(id=request.session['user_id'])
        one_group.users_that_joined.remove(current_user)
        current_user.users_joined_for.remove(one_group)
        return redirect(f'/group/{group_id}')

def delete_group(request, group_id):
    if 'user_id' not in request.session:
        return redirect('/')
    group_to_delete = Group.objects.get(id=group_id)
    group_to_delete.delete()
    return redirect('/main_page')
