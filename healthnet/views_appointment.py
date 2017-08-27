import logging

from django.shortcuts import render
from django.http import HttpResponseRedirect

from healthnet.forms import AppointmentForm
from healthnet.models import Account, Appointment, Action
from healthnet import logger
from healthnet import views


console_logger = logging.getLogger(__name__)  # Used for debug output.


def cancel_view(request):
    # Authentication check.
    authentication_result = views.authentication_check(request, [Account.ACCOUNT_PATIENT, Account.ACCOUNT_DOCTOR,
                                                            Account.ACCOUNT_ADMIN], ['pk'])
    if authentication_result is not None: return authentication_result
    # Validation Check. Make sure an appointment exists for the given pk.
    pk = request.GET['pk']
    try:
        appointment = Appointment.objects.get(pk=pk)
    except Exception:
        return HttpResponseRedirect('/error/denied/')
    # Get the template data from the session
    template_data = views.parse_session(request, {'appointment': appointment, 'form_action': "?pk=" + pk})
    # Proceed with the rest of the view
    if request.method == 'POST':
        if 'yes' in request.POST:
            appointment.active = False
            appointment.save()
            logger.log(Action.ACTION_APPOINTMENT, 'Appointment cancelled', request.user)
            request.session[
                'alert_danger'] = "The appointment has been cancelled."  # Use session when passing data through a redirect
            return HttpResponseRedirect('/appointment/list/')
        elif 'no' in request.POST:
            request.session[
                'alert_success'] = "The appointment was not cancelled."  # Use session when passing data through a redirect
            return HttpResponseRedirect('/appointment/list/')
    return render(request, 'healthnet/appointment/cancel.html', template_data)


def list_view(request):
    # Authentication check.
    authentication_result = views.authentication_check(request, [Account.ACCOUNT_PATIENT, Account.ACCOUNT_NURSE,
                                                            Account.ACCOUNT_DOCTOR])
    if authentication_result is not None: return authentication_result
    # Get the template data from the session
    template_data = views.parse_session(request)
    # Proceed with the rest of the view
    if request.user.account.role == Account.ACCOUNT_PATIENT:
        appointments = Appointment.objects.filter(patient=request.user)
    elif request.user.account.role == Account.ACCOUNT_DOCTOR:
        appointments = Appointment.objects.filter(doctor=request.user)
    else:
        appointments = Appointment.objects.all()
    # Page sorting.
    template_data['query'] = appointments.order_by('date', 'startTime')
    if 'sort' in request.GET:
        if request.GET['sort'] == 'doctor':
            template_data['query'] = appointments.order_by('doctor__username', 'date', 'startTime')
        if request.GET['sort'] == 'patient':
            template_data['query'] = appointments.order_by('patient__username', 'date', 'startTime')
        if request.GET['sort'] == 'description':
            template_data['query'] = appointments.order_by('description', 'date', 'startTime')
        if request.GET['sort'] == 'hospital':
            template_data['query'] = appointments.order_by('hospital__name', 'date', 'startTime')
        if request.GET['sort'] == 'status':
            template_data['query'] = appointments.order_by('active', 'date', 'startTime')
    return render(request, 'healthnet/appointment/list.html', template_data)


def update_view(request):
    # Authentication check.
    authentication_result = views.authentication_check(request, None, ['pk'])
    if authentication_result is not None: return authentication_result
    # Validation Check. Make sure an appointment exists for the given pk.
    pk = request.GET['pk']
    try:
        appointment = Appointment.objects.get(pk=pk)
    except Exception:
        request.session['alert_danger'] = "The requested appointment does not exist."
        return HttpResponseRedirect('/error/denied/')
    # Get the template data from the session
    template_data = views.parse_session(request, {'form_button': "Update Appointment", 'form_action': "?pk=" + pk,
                                             'appointment': appointment})
    # Proceed with the rest of the view
    request.POST._mutable = True
    if request.user.account.role == Account.ACCOUNT_PATIENT:
        request.POST['patient'] = request.user.account.pk
    elif request.user.account.role == Account.ACCOUNT_DOCTOR:
        request.POST['doctor'] = request.user.account.pk
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            form.assign(appointment)
            appointment.save()
            logger.log(Action.ACTION_APPOINTMENT, 'Appointment updated', request.user)
            template_data['alert_success'] = "The appointment has been updated!"
            template_data['form'] = form
    else:
        form = AppointmentForm(appointment.get_populated_fields())
    if request.user.account.role == Account.ACCOUNT_PATIENT:
        form.disable_field('patient')
    elif request.user.account.role == Account.ACCOUNT_DOCTOR:
        form.disable_field('doctor')
    template_data['form'] = form
    return render(request, 'healthnet/appointment/update.html', template_data)


def create_view(request):
    # Authentication check.
    authentication_result = views.authentication_check(request, [Account.ACCOUNT_PATIENT, Account.ACCOUNT_NURSE,
                                                            Account.ACCOUNT_DOCTOR])
    if authentication_result is not None: return authentication_result
    # Get the template data from the session
    template_data = views.parse_session(request, {'form_button': "Create"})
    # Proceed with the rest of the view
    default = {}
    if request.user.account.role == Account.ACCOUNT_PATIENT:
        default['patient'] = request.user.account.pk
    elif request.user.account.role == Account.ACCOUNT_DOCTOR:
        default['doctor'] = request.user.account.pk
    request.POST._mutable = True
    request.POST.update(default)
    form = AppointmentForm(request.POST)
    if request.method == 'POST':
        if form.is_valid():
            appt = Appointment(
                doctor=form.cleaned_data['doctor'].user,
                patient=form.cleaned_data['patient'].user,
                description=form.cleaned_data['description'],
                hospital=form.cleaned_data['hospital'],
                startTime=form.cleaned_data['startTime'],
                endTime=form.cleaned_data['endTime'],
                date=form.cleaned_data['date'],
            )
            appt.save()
            logger.log(Action.ACTION_APPOINTMENT, 'Appointment created', request.user)
            form = AppointmentForm(default)  # Clean the form when the page is redisplayed
            form._errors = {}
            template_data['alert_success'] = "Successfully created your appointment!"
    else:
        form._errors = {}
    if request.user.account.role == Account.ACCOUNT_PATIENT:
        form.disable_field('patient')
    elif request.user.account.role == Account.ACCOUNT_DOCTOR:
        form.disable_field('doctor')
    template_data['form'] = form
    return render(request, 'healthnet/appointment/create.html', template_data)