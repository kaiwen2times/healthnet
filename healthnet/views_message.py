from itertools import chain
import logging
from datetime import datetime

from django.shortcuts import render
from django.http import HttpResponseRedirect

from healthnet.models import Message
from healthnet import logger
from healthnet.forms import MessageForm
from healthnet.models import Account, Prescription, Action
from healthnet import views
from django.db.models import Q


console_logger = logging.getLogger(__name__)  # Used for debug output.


def list_view(request):
    # Authentication check.
    authentication_result = views.authentication_check(request)
    if authentication_result is not None: return authentication_result
    # Get the template data from the session
    template_data = views.parse_session(request)
    # Proceed with the rest of the view
    messages = Message.objects.filter(Q(sender=request.user.account) | Q(target=request.user.account))
    # Page sorting.
    template_data['query'] = messages.order_by('timestamp')
    if 'sort' in request.GET:
        if request.GET['sort'] == 'to':
            template_data['query'] = messages.order_by('target__profile', 'timestamp')
        if request.GET['sort'] == 'from':
            template_data['query'] = messages.order_by('sender__profile', 'timestamp')
        if request.GET['sort'] == 'subject':
            template_data['query'] = messages.order_by('header', 'timestamp')
        if request.GET['sort'] == 'time':
            template_data['query'] = messages.order_by('timestamp')
        if request.GET['sort'] == 'read':
            template_data['query'] = messages.order_by('read', 'timestamp')
    return render(request, 'healthnet/message/list.html', template_data)


def new_view(request):
    # Authentication check.
    authentication_result = views.authentication_check(request)
    if authentication_result is not None: return authentication_result
    # Get the template data from the session
    template_data = views.parse_session(request, {'form_button': "Send Message"})
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = Message(
                target=form.cleaned_data['target'],
                sender=request.user.account,
                header=form.cleaned_data['header'],
                body=form.cleaned_data['body'],
            )
            message.save()
            logger.log(Action.ACTION_MESSAGE, 'Message sent', request.user)
            form = MessageForm()  # Clean the form when the page is redisplayed
            template_data['alert_success'] = "Successfully sent your message!"
    else:
        form = MessageForm()
    template_data['form'] = form
    return render(request, 'healthnet/message/new.html', template_data)


def read_view(request):
    # Authentication check.
    authentication_result = views.authentication_check(request, None, ['pk'])
    if authentication_result is not None: return authentication_result
    # Validation Check. Make sure an appointment exists for the given pk.
    pk = request.GET['pk']
    try:
        message = Message.objects.get(pk=pk)
    except Exception:
        request.session['alert_danger'] = "The requested message does not exist."
        return HttpResponseRedirect('/error/denied/')
    # Get the template data from the session
    if request.user.account == message.target and not message.read:
        message.read = True
        message.save()
        logger.log(Action.ACTION_MESSAGE, 'Message read', request.user)
    template_data = views.parse_session(request,
                                        {'to': message.target.profile,
                                         'from': message.sender.profile,
                                         'header': message.header,
                                         'body': message.body})
    # Proceed with the rest of the view
    return render(request, 'healthnet/message/read.html', template_data)