from datetime import date
import datetime

from django.db import models
from django.contrib.auth.models import User


INSURANCES = (
    (0, "N/A"),
    (1, "Aetna"),
    (2, "United HealthCare"),
    (3, "Humana"),
    (4, "Celtic Healthcare"),
    (5, "BlueCross BlueShield"),
    (6, "Cigna"),
    (7, "Emblem Healthcare"),
    (8, "Amerigroup"),
    (9, "Kaiser Permanente"),
    (10, "Wellpoint"),
)


class Location(models.Model):
    city = models.CharField(max_length=50)
    zip = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    country = models.CharField(max_length=50)
    address = models.CharField(max_length=50)

    def __str__(self):
        return self.address

    class Admin:
        list_display = ('city', 'country')


class Hospital(models.Model):
    name = models.CharField(max_length=50)
    phone = models.CharField(max_length=20)
    location = models.OneToOneField(Location)

    def __str__(self):
        return self.name

    class Admin:
        list_display = (
            'name',
            'phone',
            'location'
        )


class Profile(models.Model):
    GENDER = (
        ('M', "Male"),
        ('F', "Female"),
    )

    @staticmethod
    def toGender(key):
        for item in Profile.GENDER:
            if item[0] == key:
                return item[1]
        return "None"

    firstname = models.CharField(blank=True, max_length=50)
    lastname = models.CharField(blank=True, max_length=50)
    insurance = models.CharField(max_length=50)
    emergencyContactName = models.CharField(blank=True, max_length=50)
    emergencyContactNumber = models.CharField(blank=True, max_length=20)
    sex = models.CharField(blank=True, max_length=1, choices=GENDER)
    birthday = models.DateField(default=date(1000, 1, 1))
    phone = models.CharField(blank=True, max_length=20)
    allergies = models.CharField(blank=True, max_length=250)
    created = models.DateTimeField(auto_now_add=True)
    prefHospital = models.ForeignKey(Hospital, null=True)

    def get_populated_fields(self):
        """
        This is used by the form to collect the data.
        """
        fields = {}
        if self.firstname is not None:
            fields['firstname'] = self.firstname
        if self.lastname is not None:
            fields['lastname'] = self.lastname
        if self.sex is not None:
            fields['sex'] = self.sex
        if not self.birthday.year == 1000:
            fields['birthday'] = self.birthday
        if self.phone is not None:
            fields['phone'] = self.phone
        if self.allergies is not None:
            fields['allergies'] = self.allergies
        if self.insurance is not None:
            fields['insurance'] = self.insurance
        if self.emergencyContactName is not None:
            fields['emergencyContactName'] = self.emergencyContactName
        if self.emergencyContactNumber is not None:
            fields['emergencyContactNumber'] = self.emergencyContactNumber
        if self.prefHospital is not None:
            fields['prefHospital'] = self.prefHospital
        return fields

    def __str__(self):
        return self.firstname + " " + self.lastname


class Account(models.Model):
    ACCOUNT_UNKNOWN = 0
    ACCOUNT_PATIENT = 10
    ACCOUNT_NURSE = 20
    ACCOUNT_DOCTOR = 30
    ACCOUNT_ADMIN = 40
    ACCOUNT_TYPES = (
        (ACCOUNT_UNKNOWN, "Unknown"),
        (ACCOUNT_PATIENT, "Patient"),
        (ACCOUNT_NURSE, "Nurse"),
        (ACCOUNT_DOCTOR, "Doctor"),
        (ACCOUNT_ADMIN, "Admin"),
    )
    EMPLOYEE_TYPES = (
        (ACCOUNT_NURSE, "Nurse"),
        (ACCOUNT_DOCTOR, "Doctor"),
        (ACCOUNT_ADMIN, "Admin"),
    )

    @staticmethod
    def toAccount(key):
        """
        Parses an integer value to a string representing an account role.
        :param key: The account role
        :return: The string representation of the name for the account role
        """
        for item in Account.ACCOUNT_TYPES:
            if item[0] == key:
                return item[1]
        return "None"

    role = models.IntegerField(default=0, choices=ACCOUNT_TYPES)
    profile = models.OneToOneField(Profile)
    user = models.OneToOneField(User)

    def __str__(self):
        if self.role == 30:
            return "Dr. " + self.profile.__str__()
        elif self.role == 20:
            return "Nurse " + self.profile.__str__()
        else:
            return self.profile.__str__()

    class Admin:
        list_display = (
            'role',
            'profile',
            'user'
        )


class Action(models.Model):
    ACTION_NONE = 0
    ACTION_ACCOUNT = 1
    ACTION_PATIENT = 2
    ACTION_ADMIN = 3
    ACTION_APPOINTMENT = 4
    ACTION_MEDTEST = 5
    ACTION_PRESCRIPTION = 6
    ACTION_ADMISSION = 7
    ACTION_MEDICALINFO = 8
    ACTION_MESSAGE = 9
    ACTION_TYPES = (
        (ACTION_NONE, "None"),
        (ACTION_ACCOUNT, "Account"),
        (ACTION_PATIENT, "Patient"),
        (ACTION_ADMIN, "Admin"),
        (ACTION_APPOINTMENT, "Appointment"),
        (ACTION_MEDTEST, "Medical Test"),
        (ACTION_PRESCRIPTION, "Prescription"),
        (ACTION_ADMISSION, "Admission"),
        (ACTION_MEDICALINFO, "Medical Info"),
        (ACTION_MESSAGE, "Message"),
    )

    @staticmethod
    def toAction(key):
        """
        Parses an integer value to a string representing an action.
        :param key: The action number
        :return: The string representation of the name for action
        """
        for item in Action.ACTION_TYPES:
            if item[0] == key:
                return item[1]
        return "None"

    type = models.IntegerField(default=0, choices=ACTION_TYPES)
    timePerformed = models.DateTimeField(auto_now_add=True)
    description = models.CharField(max_length=100)
    user = models.ForeignKey(User)
    """
    Might have to add this field to specify:
    - where action was committed
    - exclude actions that are done at a hospital for which a specific
      admin is not in control of ?
    hospital = models.ForeignKey(Hospital)
    """


class Appointment(models.Model):
    doctor = models.ForeignKey(User, related_name="doctors")
    patient = models.ForeignKey(User, related_name="patients")
    description = models.CharField(max_length=200)
    active = models.BooleanField(default=True)
    hospital = models.ForeignKey(Hospital)
    startTime = models.TimeField()
    endTime = models.TimeField()
    date = models.DateField()

    def get_populated_fields(self):
        """
        This is used by the form to collect the data.
        """
        fields = {
            'doctor': self.doctor.account,
            'patient': self.patient.account,
            'description': self.description,
            'hospital': self.hospital,
            'startTime': self.startTime,
            'endTime': self.endTime,
            'date': self.date,
        }
        return fields


class Message(models.Model):
    target = models.ForeignKey(Account, related_name="messages_received")
    sender = models.ForeignKey(Account, related_name="messages_sent")
    header = models.CharField(max_length=300)
    body = models.CharField(max_length=1000)
    read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

class Notification(models.Model):
    user = models.ForeignKey(Account, related_name="notifications_all")
    message = models.CharField(max_length=200)
    read = models.BooleanField(default=False)
    sent_timestamp = models.DateTimeField(auto_now_add=True)
    read_timestamp = models.DateTimeField(blank=True, null=True)


class Admission(models.Model):
    patient = models.ForeignKey(User, related_name="patients1")
    time = models.TimeField(default=datetime.datetime.now)
    date = models.DateField(default=datetime.date.today())
    reason = models.CharField(max_length=200)
    hospital = models.ForeignKey(Hospital)
    active = models.BooleanField(default=True)


class Prescription(models.Model):
    patient = models.ForeignKey(User, related_name="patient")
    doctor = models.ForeignKey(User, related_name="doctor")
    date = models.DateField()
    medication = models.CharField(max_length=100)
    strength = models.CharField(max_length=30)
    instruction = models.CharField(max_length=200)
    refill = models.IntegerField()
    active = models.BooleanField(default=True)

class MedicalInfo(models.Model):
    BLOOD = (
    ('A+', 'A+ Type'),
    ('B+', 'B+ Type'),
    ('AB+', 'AB+ Type'),
    ('O+', 'O+ Type'),
    ('A-', 'A- Type'),
    ('B-', 'B- Type'),
    ('AB-', 'AB- Type'),
    ('O-', 'O- Type'),
)
    @staticmethod
    def toBlood(key):
        for item in MedicalInfo.BLOOD:
            if item[0] == key:
                return item[1]
        return "None"

    patient = models.ForeignKey(User, related_name="patiento")
    bloodType = models.CharField(max_length=10, choices=BLOOD)
    allergy = models.CharField(max_length=100)
    alzheimer = models.BooleanField()
    asthma = models.BooleanField()
    diabetes = models.BooleanField()
    stroke = models.BooleanField()
    comments= models.CharField(max_length=700)

    def get_populated_fields(self):
        fields = {
            'patient': self.patient.account,
            'bloodType': self.bloodType,
            'allergy': self.allergy,
            'alzheimer': self.alzheimer,
            'asthma': self.asthma,
            'diabetes': self.diabetes,
            'stroke': self.stroke,
            'comments': self.comments,
        }
        return fields


class MedicalTest(models.Model):
    name = models.CharField(max_length=50)
    date = models.DateField()
    hospital = models.ForeignKey(Hospital)
    description = models.CharField(max_length=200)
    doctor = models.ForeignKey(User, related_name="docs")
    patient = models.ForeignKey(User, related_name="pts")
    private = models.BooleanField(default=True)
    completed = models.BooleanField()
    # image1 = models.FileField(blank=True, null=True, upload_to='images/%Y/%m/%d')
    # image2 = models.FileField(blank=True, null=True, upload_to='images/%Y/%m/%d')
    # image3 = models.FileField(blank=True, null=True, upload_to='images/%Y/%m/%d')
    # image4 = models.FileField(blank=True, null=True, upload_to='images/%Y/%m/%d')
    # image5 = models.FileField(blank=True, null=True, upload_to='images/%Y/%m/%d')

    def get_populated_fields(self):
        """
        This is used by the form to collect the data.
        """
        fields = {
            'name': self.name,
            'date': self.date,
            'hospital': self.hospital,
            'description': self.description,
            'doctor': self.doctor.account,
            'patient': self.patient.account,
            'private': self.private,
            'completed': self.completed,
            # 'image1': self.image1,
            # 'image2': self.image2,
            # 'image3': self.image3,
            # 'image4': self.image4,
            # 'image5': self.image5,
        }
        return fields


        # class TestImage(models.Model):
        # picture = models.FileField(blank=True, null=True, upload_to='images/%Y/%m/%d')
        # test = models.ForeignKey(MedicalTest)
        #
        #     def get_populated_fields(self):
        #         """
        #         This is used by the form to collect the data.
        #         """
        #         fields = {
        #             'picture': self.picture,
        #             'test':    self.test,
        #         }
        #         return fields

class Statistics(models.Model):
    stats = models.CharField(max_length=100)
    freq = models.IntegerField(default=0)
    """
    STATS_NONE = 0,
    STATS_LOGIN = 1
    STAT_TYPES = (
        (STATS_LOGIN, "User Login")
    )
    @staticmethod
    def toStatistic(key):

        Parses an integer value to a string representing an action.
        :param key: The action number
        :return: The string representation of the name for action

        for stat in Statistics.STAT_TYPES:
            if stat[0] == key
                return stat[1]
        return "None"
    stats =  models.IntegerField(default=0, choices=STAT_TYPES)
    """
