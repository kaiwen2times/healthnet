import logging

from django.shortcuts import render
from django.contrib.auth.models import User

from healthnet.forms import EmployeeRegisterForm
from healthnet.models import Account, Profile, Action
from healthnet.models import Statistics
from healthnet import logger
from healthnet import views


console_logger = logging.getLogger(__name__)  # Used for debug output.


def users_view(request):
    # Authentication check.
    authentication_result = views.authentication_check(request, [Account.ACCOUNT_ADMIN])
    if authentication_result is not None: return authentication_result
    # Get the template data from the session
    template_data = views.parse_session(request)
    # Proceed with the rest of the view
    if request.method == 'POST':
        pk = request.POST['pk']
        role = request.POST['role']
        account = Account.objects.get(pk=pk)
        if account is not None:
            account.role = role
            account.save()
            logger.log(Action.ACTION_ADMIN, 'Admin modified ' + account.user.username + "'s role", request.user)
            template_data['alert_success'] = "Updated " + account.user.username + "'s role!"
    if 'search' in request.GET:
        template_data['query'] = Account.objects.filer(profile__firstname__icontains=request.GET['search'])
    else:
        template_data['query'] = Account.objects.all().order_by('-role')
    if 'sort' in request.GET:
        if request.GET['sort'] == 'username':
            template_data['query'] = Account.objects.all().order_by('user__username')
        if request.GET['sort'] == 'firstname':
            template_data['query'] = Account.objects.all().order_by('profile__firstname')
        if request.GET['sort'] == 'lastname':
            template_data['query'] = Account.objects.all().order_by('profile__lastname')
    return render(request, 'healthnet/admin/users.html', template_data)


def activity_view(request):
    # Authentication check.
    authentication_result = views.authentication_check(request, [Account.ACCOUNT_ADMIN])
    if authentication_result is not None: return authentication_result
    # Get the template data from the session
    template_data = views.parse_session(request, {'query': Action.objects.all().order_by('-timePerformed')})
    # Proceed with the rest of the view
    if 'sort' in request.GET:
        if request.GET['sort'] == 'description':
            template_data['query'] = Action.objects.all().order_by('description', '-timePerformed')
        if request.GET['sort'] == 'user':
            template_data['query'] = Action.objects.all().order_by('user__username', '-timePerformed')
        if request.GET['sort'] == 'type':
            template_data['query'] = Action.objects.all().order_by('type', 'description', '-timePerformed')
    return render(request, 'healthnet/admin/activity.html', template_data)


def createemployee_view(request):
    # Authentication check.
    authentication_result = views.authentication_check(request, [Account.ACCOUNT_ADMIN])
    if authentication_result is not None: return authentication_result
    # Get the template data from the session
    template_data = views.parse_session(request, {'form_button': "Register"})
    # Proceed with the rest of the view
    if request.method == 'POST':
        form = EmployeeRegisterForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                form.cleaned_data['email'].lower(),  # Username, make sure it's lowercase
                form.cleaned_data['email'],  # Email
                form.cleaned_data['password_first']  # Password
            )
            profile = Profile(
                firstname=form.cleaned_data['firstname'],
                lastname=form.cleaned_data['lastname'],
            )
            profile.save()
            account = Account(role=form.cleaned_data['employee'], profile=profile, user=user)
            account.save()
            logger.log(Action.ACTION_ADMIN, 'Admin registered ' + user.username, request.user)
            form = EmployeeRegisterForm()  # Clean the form when the page is redisplayed
            template_data['alert_success'] = "Successfully created new employee account"
    else:
        form = EmployeeRegisterForm()
    template_data['form'] = form
    return render(request, 'healthnet/admin/createemployee.html', template_data)

def statistic_view(request):
   # Authentication check.
    authentication_result = views.authentication_check(request, [Account.ACCOUNT_ADMIN])
    if authentication_result is not None: return authentication_result
    # Get the template data from the session
    template_data = views.parse_session(request, {'query': Action.objects.all().order_by('-timePerformed')})
    # Proceed with the rest of the view
    if 'sort' in request.GET:
        if request.GET['sort'] == 'description':
            template_data['query'] = Action.objects.all().order_by('description', '-timePerformed')
        if request.GET['sort'] == 'user':
            template_data['query'] = Action.objects.all().order_by('user__username', '-timePerformed')
        if request.GET['sort'] == 'type':
            template_data['query'] = Action.objects.all().order_by('type', 'description', '-timePerformed')
    return render(request, 'healthnet/admin/stats.html', template_data)

    #template_data = views.parse_session(request, {'query': Statistics.objects.all().order_by('freq')})
    # Proceed with the rest of the view
   # if 'sort' in request.GET:
       # if request.GET['sort' == 'statistic':
         #   template_data['query'] = Statistics.objects.all().order_by('statistics','freq')