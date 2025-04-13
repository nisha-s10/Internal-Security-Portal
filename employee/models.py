from django.db import models
import qrcode
from io import BytesIO
from django.core.files.base import ContentFile
import hashlib
from django.db.models.signals import post_delete
from django.dispatch import receiver
import os
class Employee(models.Model):
    employee_id = models.CharField(max_length=10, primary_key=True, blank=True)  # Use employee ID as primary key
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)  # Store hashed passwords
    # Add other relevant fields
    name = models.CharField(max_length=100)  # Example field for employee name
    dob = models.DateField()
    aadhar_number = models.CharField(max_length=12, unique=True, blank=True, null=True)  # New field for Aadhar number
    mobile_number = models.CharField(max_length=10, blank=True, null=True)  # New field for mobile number
    qr_code_data = models.BinaryField(blank=True, null=True)  # Store QR code as binary data
    photo = models.ImageField(upload_to='employee_photos/', blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.employee_id})"  # Display name and ID in admin

    def save(self, *args, **kwargs):

        if not self.employee_id:
            combined_data = f"{self.name}{self.email}{self.dob}{self.mobile_number}{self.aadhar_number}" # Use first 8 characters of hash
            counter = 0
            while True:
                hashed_data = hashlib.sha256(f"{combined_data}{counter}".encode()).hexdigest()
                numeric_hash = int(hashed_data, 16) % 900000 + 100000  # Ensure it's between 100000 and 999999
                if not Employee.objects.filter(employee_id=numeric_hash).exists():
                    self.employee_id = numeric_hash
                    break
                counter += 1

        # Generate a URL that redirects to the employee's details page
        qr_data = f"https://yourdomain.com/details/{self.employee_id}/"

        # Generate QR Code
        qr = qrcode.QRCode(
            version=1,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_data)
        qr.make(fit=True)

        # Create an image from the QR Code instance
        img = qr.make_image(fill_color="black", back_color="white")

        # Save image to a BytesIO buffer
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)

        # Save image to the ImageField
        self.qr_code_data = buffer.read()

        super().save(*args, **kwargs)

    @property
    def masked_aadhar_number(self):
        """Return last four digits of Aadhar number"""
        return f"xxxx xxxx {self.aadhar_number[-4:]}"
    
@receiver(post_delete, sender=Employee)
def delete_employee_photo(sender, instance, **kwargs):
    if instance.photo and instance.photo.path:
        if os.path.isfile(instance.photo.path):
            os.remove(instance.photo.path)