HealthNet README.txt

INSTALLATION

1. Make sure that the target environment for HealthNet has Python 3.2.2 and Django 1.6.5 installed and running correctly.

2. Unzip the compressed folder containing the HealthNet application into a suitable directory of your choice.

3. Once that is done, open a command prompt window (Windows) or a Terminal window (Mac OS).

4. Navigate to the folder where the application was opened and traverse deeper through the directory until you are in the same directory that contains the file called manage.py.

5. Type in the command "python manage.py runserver" on your command prompt or Terminal window and run it.

6. Take the HTTP address from the line beginning with "Starting development server at...".Put that web address into a web browser of your choice and go to it. The URL you enter should look something like this: http://127.0.0.1:8000

7. You now have the HealthNet application running. Enjoy!


LOGINS AND PASSWORDS

To sign into the administrator interface for the entire HealthNet application, you can use the following credentials:

Username: admin
Password: password

To sign into HealthNet as an administrator, you can use the following credentials:

Username: admina@test.com
Password: a

Some of the sample credentials for Doctor, Nurse, and Patient users:

Username: doctora@test.com
Password: a

Username: nursea@test.com
Password: a

Username: patienta@test.com
Password: a


DISCLAIMERS

For our beta release of the HealthNet application, we tried to most of the key features. These are the features we have currently implemented.

- Patient Registration
- Administrator Registration
- Update Patient Profile Information
- Update Patient Medical Information
- Create or Update Patient Appointment
- Cancel Patient Appointment
- Appointment Calendar
- Add/Remove Prescriptions
- Viewing Patient Medical Information, Prescriptions and Tests and Results
- Release Test Results
- Logging System Activity
- Admission and Discharge to/from Hospital
- Viewing Activity Log
- Viewing System Statistics
- Patient Transfer
- Upload Patient Information
- Send Private Message

Unfortunately, things don't always work how we want them to. Here is a list of known bugs currently in the HealthNet system:

- Unable to link to another patient in our system as an emergency contact
- Unable to check if a newly created appointment or updated appointment overlaps with a
  previously made appointment, so overlapping appointments can be made
- You are able to enter two accounts with the same email if the case is different
  (DoctorA@test.com & doctora@test.com are seen as different credentials so it is allowed to be done)
- Administrator is able to change its role to any of the other roles(Patient, Nurse, Doctor)
- Insurance is required for employees when it should not be
- Unable to add images or files to Medical Tests when uploading them
- Unable to view system statistics in HealthNet


TEST LIASON

If you are having any issues testing our HealthNet application, please contact our Test Coordinator. His contact info is listed below.

Arshdeep Khalsa
ask7708@rit.edu


DOCUMENTS

Project Curry's Requirements Document
- Requirements.pdf (located under the public_html/Release-R2Beta/cross-team-testing directory)

Project Curry's Test Plan Document
- ProjectCurryTestPlanTracker.xls.xlsx (located under the public_html/Release-R2Beta/cross-team-testing directory)