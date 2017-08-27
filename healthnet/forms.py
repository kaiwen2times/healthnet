from datetime import date

from django import forms
from django.contrib.auth.models import User
from django.contrib.auth import authenticate

from healthnet.models import Account, Profile, Hospital, Admission, MedicalInfo


def validate_username_available(username):
    """
    This is a validator that throws an error if the given username already exists.
    """
    if User.objects.filter(username=username).count():
        raise forms.ValidationError("That email is already registered")


def validate_username_exists(username):
    """
    This is a validator that throws an error if the given username doesn't exist.
    """
    if not User.objects.filter(username=username).count():
        raise forms.ValidationError("That email does not exist")


def validate_not_admitted(patient):
    """
    This is a validator that throws an error if the patient is already admitted.
    """
    queryset = Admission.objects.filter(patient=patient.user);
    if queryset.count():
        for admission in queryset:
            if admission.active:
                raise forms.ValidationError("Patient already admitted")


def validate_birthday(birthday):
    """
    This is a validator that checks if the date is realistic.
    """
    if birthday.year < (date.today().year - 200):
        raise forms.ValidationError("Please choose a later date")
    elif birthday > date.today():
        raise forms.ValidationError("Please choose an earlier date")


def setup_field(field, placeholder=None):
    """
    This configures the given field to play nice with the bootstrap theme. Additionally, you can add
    an additional argument to set a placeholder text on the field.
    """
    field.widget.attrs['class'] = 'form-control'
    if placeholder is not None:
        field.widget.attrs['placeholder'] = placeholder


class BasicForm(forms.Form):
    def disable_field(self, field):
        """
        Marks the field as disabled.
        :param field: The name of the field
        """
        self.fields[field].widget.attrs['disabled'] = ""

    def mark_error(self, field, description):
        """
        Marks the given field as errous. The given description is displayed when the form it generated
        :param field: The name of the field
        :param description: The error description
        """
        self._errors[field] = self.error_class([description])
        del self.cleaned_data[field]


class LoginForm(BasicForm):
    email = forms.EmailField(max_length=50, validators=[validate_username_exists])
    setup_field(email, 'Enter email here')
    password = forms.CharField(max_length=50, widget=forms.PasswordInput())
    setup_field(password, "Enter password here")

    def clean(self):
        """
        This is to make sure the password is valid for the given email. We don't have to worry about
        the email being invalid because the field specific validators run before this clean function.
        """
        cleaned_data = super(LoginForm, self).clean()
        username = cleaned_data.get('email')
        password = cleaned_data.get('password')
        if username and password:
            user = authenticate(username=username, password=password)
            if user is None:
                self.mark_error('password', 'Incorrect password')
        return cleaned_data


class AccountRegisterForm(BasicForm):
    insurance = forms.CharField(max_length=50)
    setup_field(insurance, 'Enter your insurance information')
    firstname = forms.CharField(max_length=50)
    setup_field(firstname, 'Enter first name here')
    lastname = forms.CharField(max_length=50)
    setup_field(lastname, 'Enter a last name here')
    email = forms.EmailField(max_length=50, validators=[validate_username_available])
    setup_field(email, 'Enter email here')
    password_first = forms.CharField(label='Password', min_length=1, max_length=50, widget=forms.PasswordInput())
    setup_field(password_first, "Enter password here")
    password_second = forms.CharField(label='', min_length=1, max_length=50, widget=forms.PasswordInput())
    setup_field(password_second, "Enter password again")

    """
    This is to make sure both passwords fields have the same values in them. If they don't mark
    them as errous.
    """

    def clean(self):
        cleaned_data = super(AccountRegisterForm, self).clean()
        password_first = cleaned_data.get('password_first')
        password_second = cleaned_data.get('password_second')
        if password_first and password_second and password_first != password_second:
            self.mark_error('password_second', 'Passwords do not match')
        return cleaned_data


class PasswordForm(BasicForm):
    password_current = forms.CharField(label='Current', max_length=50, widget=forms.PasswordInput())
    setup_field(password_current, 'Enter your current password here')
    password_first = forms.CharField(label='New', max_length=50, widget=forms.PasswordInput())
    setup_field(password_first, "Enter new password here")
    password_second = forms.CharField(label='', max_length=50, widget=forms.PasswordInput())
    setup_field(password_second, "Enter new password again")

    """
    This is to make sure both passwords fields have the same values in them. If they don't, mark
    them as errous. Also check if the current and new passwords are they same. If they are, then
    mark them as errous (we want different passwords).
    """

    def clean(self):
        cleaned_data = super(PasswordForm, self).clean()
        password_current = cleaned_data.get('password_current')
        password_first = cleaned_data.get('password_first')
        password_second = cleaned_data.get('password_second')
        if password_first and password_second:
            if password_first != password_second:
                self.mark_error('password_second', 'Passwords do not match')
            if password_current and password_current == password_first:
                self.mark_error('password_current', 'Your current and new passwords must be different')
        return cleaned_data


class ProfileForm(BasicForm):
    firstname = forms.CharField(max_length=50)
    setup_field(firstname, 'Enter first name here')
    lastname = forms.CharField(max_length=50)
    setup_field(lastname, 'Enter a last name here')
    insurance = forms.CharField(max_length=50)
    setup_field(insurance, "Enter your insurance information")
    sex = forms.ChoiceField(required=False, choices=Profile.GENDER)
    setup_field(sex)
    birthday = forms.DateField(required=False, validators=[validate_birthday])
    setup_field(birthday, 'Enter birthday as YYYY-MM-DD')
    phone = forms.CharField(required=False, max_length=20)
    setup_field(phone, 'Enter phone number here')
    allergies = forms.CharField(required=False, max_length=250)
    setup_field(allergies, 'Enter any allergies here')
    emergencyContactName = forms.CharField(label="Emergency Contact", required=False, max_length=50)
    setup_field(emergencyContactName, "Enter your emergency contact's name here")
    emergencyContactNumber = forms.CharField(label="Emergency Contact #", required=False, max_length=20)
    setup_field(emergencyContactNumber, "Enter your emergency contact's number here")
    prefHospital = forms.ModelChoiceField(label="Preferred Hospital", required=False, queryset=Hospital.objects.all())
    setup_field(prefHospital)
    # ecLinkedPatient = forms.ModelChoiceField(required=False, queryset=Account.objects.filter(role=10))
    # setup_field(ecLinkedPatient)

    def assign(self, profile):
        profile.firstname = self.cleaned_data['firstname']
        profile.lastname = self.cleaned_data['lastname']
        profile.sex = self.cleaned_data['sex']
        if self.cleaned_data['birthday'] is not None:
            profile.birthday = self.cleaned_data['birthday']
        profile.phone = self.cleaned_data['phone']
        profile.allergies = self.cleaned_data['allergies']
        profile.insurance = self.cleaned_data['insurance']
        profile.emergencyContactName = self.cleaned_data['emergencyContactName']
        profile.emergencyContactNumber = self.cleaned_data['emergencyContactNumber']
        profile.prefHospital = self.cleaned_data['prefHospital']


class AppointmentForm(BasicForm):
    description = forms.CharField(required=True, max_length=50)
    setup_field(description, 'Enter description here')
    hospital = forms.ModelChoiceField(queryset=Hospital.objects.all())
    setup_field(hospital)
    doctor = forms.ModelChoiceField(queryset=Account.objects.filter(role=30))
    setup_field(doctor)
    patient = forms.ModelChoiceField(queryset=Account.objects.filter(role=10))
    setup_field(patient)
    startTime = forms.TimeField()
    setup_field(startTime)
    endTime = forms.TimeField()
    setup_field(endTime)
    date = forms.DateField()
    setup_field(date)

    def assign(self, appointment):
        """
        """
        appointment.description = self.cleaned_data['description']
        appointment.hospital = self.cleaned_data['hospital']
        appointment.doctor = self.cleaned_data['doctor'].user
        appointment.patient = self.cleaned_data['patient'].user
        appointment.startTime = self.cleaned_data['startTime']
        appointment.endTime = self.cleaned_data['endTime']
        appointment.date = self.cleaned_data['date']

    """
    This is a validator that checks if the appointment is conflicting with any other already
    made appointments.
    """
    # def clean(self):
    # cleaned_data = super(PasswordForm, self).clean()
    # startTime = cleaned_data.get('startTime')
    #     endTime = cleaned_data.get('endTime')
    #     date = cleaned_data.get('date')
    #     doctor = cleaned_data.get('doctor')
    #     if startTime and endTime and date:
    #         appointments = Appointment.objects.filter(doctor=doctor)
    #         time = another.startTime
    #         if time >= self.startTime and time <= self.endTime:
    #             return False
    #         else:
    #             return True
    #     return cleaned_data


class EmployeeRegisterForm(BasicForm):
    firstname = forms.CharField(max_length=50)
    setup_field(firstname, 'Enter first name here')
    lastname = forms.CharField(max_length=50)
    setup_field(lastname, 'Enter a last name here')
    email = forms.EmailField(max_length=50, validators=[validate_username_available])
    setup_field(email, 'Enter email here')
    password_first = forms.CharField(label='Password', min_length=1, max_length=50, widget=forms.PasswordInput())
    setup_field(password_first, "Enter password here")
    password_second = forms.CharField(label='', min_length=1, max_length=50, widget=forms.PasswordInput())
    setup_field(password_second, "Enter password again")
    employee = forms.ChoiceField(required=False, choices=Account.EMPLOYEE_TYPES)
    setup_field(employee)

    """
    This is to make sure both passwords fields have the same values in them. If they don't mark
    them as errous.
    """

    def clean(self):
        cleaned_data = super(EmployeeRegisterForm, self).clean()
        password_first = cleaned_data.get('password_first')
        password_second = cleaned_data.get('password_second')
        if password_first and password_second and password_first != password_second:
            self.mark_error('password_second', 'Passwords do not match')
        return cleaned_data


class AdmissionForm(BasicForm):
    reason = forms.CharField(required=True, max_length=50)
    setup_field(reason, 'Enter reason of admission')
    patient = forms.ModelChoiceField(queryset=Account.objects.filter(role=10), validators=[validate_not_admitted])
    setup_field(patient)
    time = forms.TimeField()
    setup_field(time)
    date = forms.DateField()
    setup_field(date)
    hospital = forms.ModelChoiceField(queryset=Hospital.objects.all())
    setup_field(hospital)

    def assign(self, admission):
        """
        """
        admission.reason = self.cleaned_data['reason']
        admission.hospital = self.cleaned_data['hospital']
        admission.patient = self.cleaned_data['patient'].user
        admission.time = self.cleaned_data['time']
        admission.date = self.cleaned_data['date']


class PrescriptionForm(BasicForm):
    patient = forms.ModelChoiceField(queryset=Account.objects.filter(role=10))
    setup_field(patient)
    doctor = forms.ModelChoiceField(queryset=Account.objects.filter(role=30))
    setup_field(doctor)
    date = forms.DateField()
    setup_field(date)
    medication = forms.CharField(max_length=100)
    setup_field(medication, "Enter the medication here")
    strength = forms.CharField(max_length=30)
    setup_field(strength, "Enter the strength here")
    instruction = forms.CharField(max_length=200)
    setup_field(instruction, "Enter the instruction here")
    refill = forms.IntegerField()
    setup_field(refill, "Enter the number of refills")


# class MedTestImageForm(BasicForm):
# image1 = forms.FileField(label='Image 1', required=False)
# setup_field(image1)
#     image2 = forms.FileField(label='Image 2', required=False)
#     setup_field(image2)
#     image3 = forms.FileField(label='Image 3', required=False)
#     setup_field(image3)
#     image4 = forms.FileField(label='Image 4', required=False)
#     setup_field(image4)
#     image5 = forms.FileField(label='Image 5', required=False)
#     setup_field(image5)
#
#     def assign(self, mtimage):
#         mtimage.image1 = self.cleaned_data['image1']
#         mtimage.image2 = self.cleaned_data['image2']
#         mtimage.image3 = self.cleaned_data['image3']
#         mtimage.image4 = self.cleaned_data['image4']
#         mtimage.image5 = self.cleaned_data['image5']

# class MedTestImageField(forms.FileField):
#     picture = forms.FileField(required=False)

class MedTestForm(BasicForm):
    name = forms.CharField(max_length=50)
    setup_field(name)
    date = forms.DateField()
    setup_field(date)
    hospital = forms.ModelChoiceField(queryset=Hospital.objects.all())
    setup_field(hospital)
    description = forms.CharField(max_length=200)
    setup_field(description, "Enter description here")
    doctor = forms.ModelChoiceField(queryset=Account.objects.filter(role=30))
    setup_field(doctor)
    patient = forms.ModelChoiceField(queryset=Account.objects.filter(role=10))
    setup_field(patient)
    private = forms.BooleanField(required=False)
    setup_field(private)
    completed = forms.BooleanField(required=False)
    setup_field(completed)
    # image1 = MedTestImageField(label='Image 1', required=False)
    # setup_field(image1)
    # image2 = MedTestImageField(label='Image 2', required=False)
    # setup_field(image2)
    # image3 = MedTestImageField(label='Image 3', required=False)
    # setup_field(image3)
    # image4 = MedTestImageField(label='Image 4', required=False)
    # setup_field(image4)
    # image5 = MedTestImageField(label='Image 5', required=False)
    # setup_field(image5)

    def assign(self, medtest):
        """
        """
        medtest.name = self.cleaned_data['name']
        medtest.date = self.cleaned_data['date']
        medtest.hospital = self.cleaned_data['hospital']
        medtest.description = self.cleaned_data['description']
        medtest.doctor = self.cleaned_data['doctor'].user
        medtest.patient = self.cleaned_data['patient'].user
        medtest.private = self.cleaned_data['private']
        medtest.completed = self.cleaned_data['completed']
        # medtest.image1 = self.cleaned_data['image1']
        # medtest.image2 = self.cleaned_data['image2']
        # medtest.image3 = self.cleaned_data['image3']
        # medtest.image4 = self.cleaned_data['image4']
        # medtest.image5 = self.cleaned_data['image5']

class MedicalInfoForm(BasicForm):
    patient = forms.ModelChoiceField(queryset=Account.objects.filter(role=10))
    setup_field(patient)
    bloodType = forms.ChoiceField(choices=MedicalInfo.BLOOD, required=False)
    setup_field(bloodType)
    allergy = forms.CharField(max_length=100, required=False)
    setup_field(allergy,"Enter allergies here")
    alzheimer = forms.BooleanField(required=False)
    setup_field(alzheimer)
    asthma = forms.BooleanField(required=False)
    setup_field(asthma)
    diabetes = forms.BooleanField(required=False)
    setup_field(diabetes)
    stroke = forms.BooleanField(required=False)
    setup_field(stroke)
    comments= forms.CharField(max_length=500, required=False)
    setup_field(comments, "Enter additional information here")

    def assign(self, medicalInfo):
        medicalInfo.patient = self.cleaned_data['patient'].user
        medicalInfo.bloodType = self.cleaned_data['bloodType']
        medicalInfo.allergy = self.cleaned_data['allergy']
        medicalInfo.alzheimer = self.cleaned_data['alzheimer']
        medicalInfo.asthma = self.cleaned_data['asthma']
        medicalInfo.stroke = self.cleaned_data['stroke']
        medicalInfo.comments = self.cleaned_data['comments']
    
class MessageForm(BasicForm):
    target = forms.ModelChoiceField(queryset=Account.objects.all())
    setup_field(target)
    header = forms.CharField(max_length=300)
    setup_field(header, "Message header")
    body = forms.CharField(max_length=1000)
    setup_field(body, "Message body")
