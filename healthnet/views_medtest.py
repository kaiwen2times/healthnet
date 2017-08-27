import logging

from django.shortcuts import render
from django.http import HttpResponseRedirect

from healthnet.forms import MedTestForm
from healthnet.models import Account, Action, MedicalTest
from healthnet import logger
from healthnet import views


console_logger = logging.getLogger(__name__)  # Used for debug output.


def create_view(request):
    # Authentication check.
    authentication_result = views.authentication_check(request, [Account.ACCOUNT_DOCTOR])
    if authentication_result is not None: return authentication_result
    # Get the template data from the session
    template_data = views.parse_session(request, {'form_button': "Upload"})
    # Proceed with the rest of the view
    default = {}
    if request.user.account.role == Account.ACCOUNT_DOCTOR:
        default['doctor'] = request.user.account.pk
    request.POST._mutable = True
    request.POST.update(default)
    form = MedTestForm(request.POST)
    if request.method == 'POST':
        if form.is_valid():
            medtest = MedicalTest(
                name=form.cleaned_data['name'],
                date=form.cleaned_data['date'],
                hospital=form.cleaned_data['hospital'],
                description=form.cleaned_data['description'],
                doctor=form.cleaned_data['doctor'].user,
                patient=form.cleaned_data['patient'].user,
                private=form.cleaned_data['private'],
                completed=form.cleaned_data['completed'],
            )
            medtest.save()
            logger.log(Action.ACTION_MEDTEST, 'Medical Test created', request.user)
            form = MedTestForm(default)  # Clean the form when the page is redisplayed
            form.disable_field('doctor')
            form._errors = {}
            template_data['alert_success'] = "Successfully uploaded the medical test!"
    else:
        form._errors = {}
    form.disable_field('doctor')
    # if request.user.account.role == Account.ACCOUNT_DOCTOR:
    # form.disable_field('performedBy')
    template_data['form'] = form
    return render(request, 'healthnet/medtest/upload.html', template_data)


# def medtest_addimage_view(request):
# # Authentication check.
# authentication_result = _authentication_check(request, [Account.ACCOUNT_DOCTOR], ['pk'])
# if authentication_result is not None: return authentication_result
#     # Get the template data from the session
#     template_data = _parse_session(request, {'form_button': "Attach & Submit"})
#     # Proceed with the rest of the view
#     default = {}
#     form = MedTestImageForm(request.POST, request.FILES)
#     if request.method == 'POST' and request.FILES:
#         if form.is_valid():
#             # for key in request.FILES.keys:
#             #     img = TestImage(
#             #         picture=request.FILES[key],
#             #         test=template_data['medtest'].pk
#             #     )
#             #     img.save()
#             img1 = TestImage(
#                 picture=request.FILES['image1'],
#                 test=template_data['medtest'].pk
#             )
#             img1.save()
#
#
#             form = MedTestImageForm(default)
#             form._errors = {}
#             template_data['alert_success'] = "Successfully attached and submitted the test images!"
#     else:
#         form._errors = {}
#     template_data['form'] = form
#     return render(request, 'healthnet/medtest/imgupload.html', template_data)

def list_view(request):
    # Authentication check.
    authentication_result = views.authentication_check(request, [Account.ACCOUNT_DOCTOR, Account.ACCOUNT_NURSE,
                                                            Account.ACCOUNT_PATIENT])
    if authentication_result is not None: return authentication_result
    # Get the template data from the session
    template_data = views.parse_session(request)
    # Proceed with the rest of the view
    if request.user.account.role == Account.ACCOUNT_DOCTOR:
        medtests = MedicalTest.objects.all()
    elif request.user.account.role == Account.ACCOUNT_NURSE:
        medtests = MedicalTest.objects.filter(hospital=request.user.account.profile.prefHospital)
    else:
        medtests = MedicalTest.objects.filter(patient=request.user, private=False)
    # Page sorting
    template_data['query'] = medtests.order_by('date')
    if 'sort' in request.GET:
        if request.GET['sort'] == 'doctor':
            template_data['query'] = medtests.order_by('doctor__username', 'date')
        if request.GET['sort'] == 'patient':
            template_data['query'] = medtests.order_by('patient__username', 'date')
        if request.GET['sort'] == 'description':
            template_data['query'] = medtests.order_by('description', 'date')
        if request.GET['sort'] == 'hospital':
            template_data['query'] = medtests.order_by('hospital__name', 'date')
        if request.GET['sort'] == 'name':
            template_data['query'] == medtests.order_by('name', 'date')
    return render(request, 'healthnet/medtest/list.html', template_data)


def display_view(request):
    # Authentication check.
    authentication_result = views.authentication_check(request, None, ['pk'])
    if authentication_result is not None: return authentication_result
    # Validation Check. Make sure a medical test exists for the given pk.
    pk = request.GET['pk']
    try:
        medtest = MedicalTest.objects.get(pk=pk)
    except Exception:
        request.session['alert_danger'] = "The requested medical test does not exist"
        return HttpResponseRedirect('/error/denied/')
    template_data = views.parse_session(request,
                                   {'form_button': "Return to list of Medical Tests", 'form_action': "?pk=" + pk,
                                    'medtest': medtest})
    if request.method == 'GET':
        form = MedTestForm(medtest.get_populated_fields())

        form.disable_field('name')
        form.disable_field('date')
        form.disable_field('hospital')
        form.disable_field('description')
        form.disable_field('doctor')
        form.disable_field('patient')
        form.disable_field('private')
        form.disable_field('completed')

        template_data['form'] = form
    else:
        return HttpResponseRedirect('/medtest/list')
    return render(request, 'healthnet/medtest/display.html', template_data)


def update_view(request):
    # Authentication check.
    authentication_result = views.authentication_check(request, None, ['pk'])
    if authentication_result is not None: return authentication_result
    # Validation Check. Make sure a medical test exists for the given pk.
    pk = request.GET['pk']
    try:
        medtest = MedicalTest.objects.get(pk=pk)
    except Exception:
        request.session['alert_danger'] = "The requested medical test does not exist"
        return HttpResponseRedirect('/error/denied/')
    # Get the template data from the session
    template_data = views.parse_session(request, {'form_button': "Update Medical Test", 'form_action': "?pk=" + pk,
                                             'medtest': medtest})
    # Proceed with the rest of the view
    request.POST._mutable = True
    if request.user.account.role == Account.ACCOUNT_DOCTOR:
        request.POST['doctor'] = request.user.account.pk
    if request.method == 'POST':
        form = MedTestForm(request.POST)
        if form.is_valid():
            form.assign(medtest)
            medtest.save()
            logger.log(Action.ACTION_MEDTEST, 'Medical Test updated', request.user)
            template_data['alert_success'] = "The medical test has been updated!"
            template_data['form'] = form
    else:
        form = MedTestForm(medtest.get_populated_fields())
    if request.user.account.role == Account.ACCOUNT_DOCTOR:
        form.disable_field('doctor')
    template_data['form'] = form
    return render(request, 'healthnet/medtest/update.html', template_data)