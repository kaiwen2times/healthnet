import logging

from django.shortcuts import render
from django.contrib.auth import authenticate
from django.http import HttpResponseRedirect
from healthnet.forms import MedicalInfoForm
from healthnet.models import Action, Account, MedicalInfo
from healthnet import logger
from healthnet import views


console_logger = logging.getLogger(__name__)  # Used for debug output.


def list_view(request):
    # Authentication check.
    authentication_result = views.authentication_check(request, [Account.ACCOUNT_NURSE,Account.ACCOUNT_DOCTOR])
    if authentication_result is not None: return authentication_result
    # Get the template data from the session
    template_data = views.parse_session(request)
    # Proceed with the rest of the view
    medicalinfoes = MedicalInfo.objects.all()
    # Page sorting.
    template_data['query'] = medicalinfoes.order_by('patient')
    if 'sort' in request.GET:
        if request.GET['sort'] == 'patient':
            template_data['query'] = medicalinfoes.order_by('patient')
        if request.GET['sort'] == 'bloodType':
            template_data['query'] = medicalinfoes.order_by('bloodType')
        if request.GET['sort'] == 'allergy':
            template_data['query'] = medicalinfoes.order_by('allergy')
    return render(request, 'healthnet/medicalinfo/list.html', template_data)


def update_view(request):
    # Authentication check.
    authentication_result = views.authentication_check(request, [Account.ACCOUNT_DOCTOR,Account.ACCOUNT_NURSE])
    if authentication_result is not None: return authentication_result
    # Validation Check. Make sure an appointment exists for the given pk.
    pk = request.GET['pk']
    try:
        medicalinfo = MedicalInfo.objects.get(pk=pk)
    except Exception:
        request.session['alert_danger'] = "The requested medical info does not exist."
        return HttpResponseRedirect('/error/denied/')
    # Get the template data from the session
    template_data = views.parse_session(request, {'form_button': "Update Medical Info", 'form_action': "?pk=" + pk,
                                             'medicalinfo': medicalinfo})
    # Proceed with the rest of the view
    request.POST._mutable = True
    request.POST['patient'] = medicalinfo.patient.account.pk
    if request.method == 'POST':
        form = MedicalInfoForm(request.POST)
        if form.is_valid():
            form.assign(medicalinfo)
            medicalinfo.save()
            logger.log(Action.ACTION_MEDICALINFO, 'Medical info updated', request.user)
            template_data['alert_success'] = "The medical info has been updated!"
            template_data['form'] = form
    else:
        form = MedicalInfoForm(medicalinfo.get_populated_fields())
        form.disable_field('patient')
    template_data['form'] = form
    return render(request, 'healthnet/medicalinfo/update.html', template_data)


def patient_view(request):
    authentication_result = views.authentication_check(request, [Account.ACCOUNT_PATIENT])
    if authentication_result is not None: return authentication_result
    default = {}
    template_data = views.parse_session(request)
    if request.user.account.role == Account.ACCOUNT_PATIENT:
        default['patient'] = request.user.account.pk
    else:
        request.session['alert_danger'] = "The requested medical info does not exist."
        return HttpResponseRedirect('/error/denied/')
    request.POST._mutable = True
    request.POST.update(default)
    form = MedicalInfoForm(request.POST)
    form.disable_field('patient')
    template_data['form'] = form
    return render(request, 'healthnet/medicalinfo/patient.html',template_data)