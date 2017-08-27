import logging

from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.core.exceptions import ObjectDoesNotExist

from healthnet.forms import LoginForm, AccountRegisterForm
from healthnet.models import Account, Profile, Action, MedicalInfo
from healthnet import logger
from healthnet.models import Statistics


console_logger = logging.getLogger(__name__)  # Used for debug output.


def authentication_check(request, required_roles=None, required_GET=None):
    """
    :param request: The page request
    :param required_roles: The role values of the users allowed to view the page
    :param required_GET: The GET values that the page needs to function properly
    :return: A redirect request if there's a problem, None otherwise
    """
    # Authentication check. Users not logged in cannot view this page.
    if not request.user.is_authenticated():
        request.session['alert_danger'] = "You must be logged into HealthNet to view that page."
        return HttpResponseRedirect('/')
    # Sanity check. Users without accounts cannot interact with HealthNet
    try:
        request.user.account
    except ObjectDoesNotExist:
        request.session['alert_danger'] = "Your account was not properly created, please try a different account."
        return HttpResponseRedirect('/logout/')
    # Permission Check.
    if required_roles and request.user.account.role not in required_roles:
        request.session['alert_danger'] = "You don't have permission to view that page."
        return HttpResponseRedirect('/error/denied/')
    # Validation Check. Make sure this page has any required GET keys.
    if required_GET:
        for key in required_GET:
            if key not in request.GET:
                request.session['alert_danger'] = "Looks like you tried to use a malformed URL."
                return HttpResponseRedirect('/error/denied/')


def parse_session(request, template_data=None):
    """
    Checks the session for any alert data. If there is alert data, it added to the given template data.
    :param request: The request to check session data for
    :param template_data: The dictionary to update
    :return: The updated dictionary
    """
    if template_data is None:
        template_data = {}
    if request.session.has_key('alert_success'):
        template_data['alert_success'] = request.session.get('alert_success')
        del request.session['alert_success']
    if request.session.has_key('alert_danger'):
        template_data['alert_danger'] = request.session.get('alert_danger')
        del request.session['alert_danger']
    return template_data


def logout_view(request):
    if request.user.is_authenticated():
        logger.log(Action.ACTION_ACCOUNT, "Account logout", request.user)
    # Django deletes the session on logout, so we need to preserve any alerts currently waiting to be displayed
    saved_data = {}
    if request.session.has_key('alert_success'):
        saved_data['alert_success'] = request.session['alert_success']
    else:
        saved_data['alert_success'] = "You have successfully logged out."
    if request.session.has_key('alert_danger'):
        saved_data['alert_danger'] = request.session['alert_danger']
    logout(request)
    if 'alert_success' in saved_data:
        request.session['alert_success'] = saved_data['alert_success']
    if 'alert_danger' in saved_data:
        request.session['alert_danger'] = saved_data['alert_danger']
    return HttpResponseRedirect('/')


def login_view(request):
    # Authentication check. Users currently logged in cannot view this page.
    if request.user.is_authenticated():
        return HttpResponseRedirect('/profile/')
    # Get the template data from the session
    template_data = parse_session(request, {'form_button': "Login"})
    # Proceed with the rest of the view
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                username=form.cleaned_data['email'].lower(),  # Make sure it's lowercase
                password=form.cleaned_data['password']
            )
            login(request, user)
            logger.log(Action.ACTION_ACCOUNT, "Account login", request.user)
            #logger.statlog("Account login")
            request.session['alert_success'] = "Successfully logged into HealthNet."
            return HttpResponseRedirect('/profile/')
    else:
        form = LoginForm()
    template_data['form'] = form
    return render(request, 'healthnet/login.html', template_data)


def register_view(request):
    # Authentication check. Users logged in cannot view this page.
    if request.user.is_authenticated():
        return HttpResponseRedirect('/profile/')
    # Get the template data from the session
    template_data = parse_session(request, {'form_button': "Register"})
    # Proceed with the rest of the view
    if request.method == 'POST':
        form = AccountRegisterForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                form.cleaned_data['email'].lower(),  # Username, make sure it's lowercase
                form.cleaned_data['email'],  # Email
                form.cleaned_data['password_first']  # Password
            )
            profile = Profile(
                firstname=form.cleaned_data['firstname'],
                lastname=form.cleaned_data['lastname'],
                insurance=form.cleaned_data['insurance'],
            )
            profile.save()
            account = Account(role=Account.ACCOUNT_PATIENT, profile=profile, user=user)
            account.save()
            medicalinfo = MedicalInfo(patient=account.user, alzheimer=False, asthma=False,
                                      diabetes=False, stroke=False)
            medicalinfo.save()
            user = authenticate(
                username=form.cleaned_data['email'].lower(),  # Make sure it's lowercase
                password=form.cleaned_data['password_first']
            )
            logger.log(Action.ACTION_ACCOUNT, "Account registered", user)
            logger.log(Action.ACTION_ACCOUNT, "Account login", user)
            login(request, user)
            request.session['alert_success'] = "Successfully registered with HealthNet."
            return HttpResponseRedirect('/profile/')
    else:
        form = AccountRegisterForm()
    template_data['form'] = form
    return render(request, 'healthnet/register.html', template_data)


def error_denied_view(request):
    # Authentication check.
    authentication_result = authentication_check(request)
    if authentication_result is not None: return authentication_result
    # Get the template data from the session
    template_data = parse_session(request)
    # Proceed with the rest of the view
    return render(request, 'healthnet/error/denied.html', template_data)