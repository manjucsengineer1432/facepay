from django.core.validators import RegexValidator
from django.db import models
from django.contrib.auth.models import User
aadhaar_validator = RegexValidator(
    regex=r'^\d{12}$',
    message="Aadhaar number must be exactly 12 digits"
)

'''class Customer(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    identity_proof = models.CharField(max_length=50, default="Aadhaar")
    identity_number = models.CharField(
        max_length=12,
        validators=[aadhaar_validator],
        unique=True
    )
    mobile_number = models.CharField(max_length=15, unique=True)
    bank_name = models.CharField(max_length=100)
    account_number = models.CharField(max_length=20)
    face_image = models.TextField(null=True,blank=True)  # Base64 encoded face image
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
'''

class Customer(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    identity_proof = models.CharField(max_length=50)
    identity_number = models.CharField(max_length=50)
    mobile_number = models.CharField(max_length=15, unique=True)
    bank_name = models.CharField(max_length=100)
    account_number = models.CharField(max_length=50)
    face_image = models.ImageField(default='default.jpg', upload_to='faces/')
    #face_encoding = models.TextField(default='')  # empty string for new rows
    face_encoding = models.BinaryField(null=True, blank=True)
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.mobile_number})"

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    identity_proof = models.CharField(max_length=50)
    identity_number = models.CharField(max_length=50)
    mobile_number = models.CharField(max_length=15)
    bank_name = models.CharField(max_length=100)
    account_number = models.CharField(max_length=30)
    face_image = models.ImageField(upload_to="faces/", null=True, blank=True)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} ({self.mobile_number})"


class Transaction(models.Model):
    sender = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='sent_transactions')
    receiver = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='received_transactions')
    amount = models.FloatField()
    status = models.CharField(max_length=20)  # "Success" or "Failed"
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender} -> {self.receiver} : {self.amount} ({self.status})"
