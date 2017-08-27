from django.conf.urls import patterns, url

from healthnet import views
from healthnet import views_admin
from healthnet import views_admission
from healthnet import views_appointment
from healthnet import views_medtest
from healthnet import views_message
from healthnet import views_prescription
from healthnet import views_profile
from healthnet import views_medicalInfo


urlpatterns = patterns('',
                       url(r'^$', views.login_view, name='index'),
                       url(r'^logout/$', views.logout_view, name='logout'),
                       url(r'^register/$', views.register_view, name='register'),

                       #url(r'^message/list/$', views_message.message_view, name='message/list'),
                       #url(r'^message/read/$', views_message.read_view, name='message/read'),
                       #url(r'^message/new/$', views_message.new_view, name='message/new'),

                       url(r'^admin/users/$', views_admin.users_view, name='admin/users'),
                       url(r'^admin/activity/$', views_admin.activity_view, name='admin/activity'),
                       url(r'^admin/stats/$', views_admin.statistic_view, name='admin/stats'),
                       url(r'^admin/createemployee/$', views_admin.createemployee_view, name='admin/createemployee'),

                       url(r'^message/list/$', views_message.list_view, name='message/list'),
                       url(r'^message/new/$', views_message.new_view, name='message/new'),
                       url(r'^message/read/$', views_message.read_view, name='message/read'),

                       url(r'^appointment/list/$', views_appointment.list_view, name='appointment/list'),
                       url(r'^appointment/update/$', views_appointment.update_view, name='appointment/update'),
                       url(r'^appointment/create/$', views_appointment.create_view, name='appointment/create'),
                       url(r'^appointment/cancel/$', views_appointment.cancel_view, name='appointment/cancel'),

                       url(r'^profile/$', views_profile.profile_view, name='profile'),
                       url(r'^profile/update/$', views_profile.update_view, name='profile/update'),
                       url(r'^profile/password/$', views_profile.password_view, name='profile/password'),

                       url(r'^medtest/upload/$', views_medtest.create_view, name='medtest/upload'),
                       url(r'^medtest/list/$', views_medtest.list_view, name='medtest/list'),
                       url(r'^medtest/display/$', views_medtest.display_view, name='medtest/display'),
                       url(r'^medtest/update/$', views_medtest.update_view, name='medtest/update'),

                       url(r'^admission/admit/$', views_admission.admit_view, name='admission/admit'),
                       url(r'^admission/list/$', views_admission.list_view, name='admission/list'),
                       url(r'^admission/discharge/$', views_admission.discharge_view, name='admission/discharge'),

                       url(r'^error/denied/$', views.error_denied_view, name='error/denied'),

                       url(r'^prescription/create/$', views_prescription.create_view, name='prescription/create'),
                       url(r'^prescription/list/$', views_prescription.list_view, name='prescription/list'),
                       url(r'^prescription/delete/$', views_prescription.delete_view, name='prescription/delete'),

                       url(r'^medicalinfo/list/$', views_medicalInfo.list_view, name='medicalinfo/list'),
                       url(r'^medicalinfo/update/$', views_medicalInfo.update_view, name='medicalinfo/update'),
                       url(r'^medicalinfo/patient/$', views_medicalInfo.patient_view, name='medicalinfo/patient'),
)