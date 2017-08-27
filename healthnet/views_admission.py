import logging

from django.shortcuts import render
from django.http import HttpResponseRedirect

from healthnet.forms import AdmissionForm
from healthnet.models import Account, Admission, Action
from healthnet import logger
from healthnet import views


console_logger = logging.getLogger(__name__)  # Used for debug output.


def admit_view(request):
    # Authentication check.
    authentication_result = views.authentication_check(request, [Account.ACCOUNT_PATIENT, Account.ACCOUNT_NURSE,
                                                            Account.ACCOUNT_DOCTOR])
    if authentication_result is not None: return authentication_result
    # Get the template data from the session
    template_data = views.parse_session(request, {'form_button': "Admit"})
    # Proceed with the rest of the view
    default = {}

    request.POST._mutable = True
    request.POST.update(default)
    form = AdmissionForm(request.POST)
    if request.method == 'POST':
        if form.is_valid():
            admiss = Admission(
                patient=form.cleaned_data['patient'].user,
                reason=form.cleaned_data['reason'],
                hospital=form.cleaned_data['hospital'],
                time=form.cleaned_data['time'],
                date=form.cleaned_data['date'],
            )
            admiss.save()
            logger.log(Action.ACTION_ADMISSION, 'Admitted Patient', request.user)
            form = AdmissionForm(default)  # Clean the form when the page is redisplayed
            form._errors = {}
            template_data['alert_success'] = "Successfully admitted patient!"
    else:
        form._errors = {}
    template_data['form'] = form
    return render(request, 'healthnet/admission/admit.html', template_data)


def list_view(request):
    # Authentication check.
    authentication_result = views.authentication_check(request, [Account.ACCOUNT_PATIENT, Account.ACCOUNT_NURSE,
                                                            Account.ACCOUNT_DOCTOR])
    if authentication_result is not None: return authentication_result
    # Get the template data from the session
    template_data = views.parse_session(request)
    # Proceed with the rest of the view

    admissions = Admission.objects.all()
    # Page sorting.
    template_data['query'] = admissions.order_by('date', 'time')
    if 'sort' in request.GET:
        if request.GET['sort'] == 'patient':
            template_data['query'] = admissions.order_by('patient__username', 'date', 'time')
        if request.GET['sort'] == 'reason':
            template_data['query'] = admissions.order_by('reason', 'date', 'time')
        if request.GET['sort'] == 'hospital':
            template_data['query'] = admissions.order_by('hospital__name', 'date', 'time')
    return render(request, 'healthnet/admission/list.html', template_data)


def discharge_view(request):
    # Authentication check.
    authentication_result = views.authentication_check(request, [Account.ACCOUNT_DOCTOR], ['pk'])
    if authentication_result is not None: return authentication_result
    # Validation Check. Make sure an admission exists for the given pk.
    pk = request.GET['pk']
    try:
        admission = Admission.objects.get(pk=pk)
    except Exception:
        return HttpResponseRedirect('/error/denied/')
    # Get the template data from the session
    template_data = views.parse_session(request, {'admission': admission, 'form_action': "?pk=" + pk})
    # Proceed with the rest of the view
    if request.method == 'POST':
        if 'yes' in request.POST:
            admission.active = False
            admission.save()
            logger.log(Action.ACTION_ADMISSION, 'Discharged Patient', request.user)
            request.session[
                'alert_danger'] = "The patient has been discharged."  # Use session when passing data through a redirect
            return HttpResponseRedirect('/admission/list/')
        elif 'no' in request.POST:
            request.session[
                'alert_success'] = "The patient was not discharged."  # Use session when passing data through a redirect
            return HttpResponseRedirect('/admission/list/')
    return render(request, 'healthnet/admission/discharge.html', template_data)