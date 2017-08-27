import logging

from django import template
from django import forms

from healthnet.models import Action, Account

console_logger = logging.getLogger(__name__)  # Used for debug output.
register = template.Library()


@register.filter(name='isDateable')
def isDateable(field):
    return isinstance(field.field, forms.DateField) or isinstance(field.field, forms.DateTimeField) or isinstance(
        field.field, forms.TimeField)


@register.filter(name='isDateField')
def isDateField(field):
    return isinstance(field.field, forms.DateField)


@register.filter(name='isDateTimeField')
def isDateTimeField(field):
    return isinstance(field.field, forms.DateTimeField)


@register.filter(name='isTimeField')
def isTimeField(field):
    return isinstance(field.field, forms.TimeField)


@register.filter(name='isAuthenticated')
def isAuthenticated(user):
    return user.is_authenticated()


@register.filter(name='getAccountRole')
def getAccountRole(user):
    """
    :param user: The user model
    :return: The string representation of the name for the role
    """
    return Account.toAccount(user.account.role).lower()


@register.filter(name='getActivityAction')
def getActivityAction(key):
    """
    :param key: The action number
    :return: The string representation of the name for action
    """
    return Action.toAction(key)