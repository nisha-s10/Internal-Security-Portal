from django.db import models
import qrcode
from io import BytesIO
from django.core.files.base import ContentFile
import hashlib
from django.db.models.signals import post_delete
from django.dispatch import receiver
import os
from datetime import datetime
from django.urls import reverse
from PIL import Image
from django.utils.text import slugify

def employee_photo_path(instance, filename):
    ext = filename.split('.')[-1]
    name = instance.name.strip().replace(" ", "_")
    filename = f"{name}.{ext}"
    return os.path.join('employee_photos', filename)
class Employee(models.Model):
    employee_id = models.CharField(max_length=10, primary_key=True, blank=True)  # Use employee ID as primary key
    name = models.CharField(max_length=100)  # Example field for employee name
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    ] 
    gender = models.CharField(
        max_length=6,
        choices=GENDER_CHOICES,
        null=True,  # Optional: allows null values if gender isn't provided
        blank=True,  # Optional: allows blank values if gender isn't provided
    )
    designation = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)  # Store hashed passwords
    dob = models.DateField()
    aadhar_number = models.CharField(max_length=12, unique=True, blank=True, null=True)  # New field for Aadhar number
    mobile_number = models.CharField(max_length=10, blank=True, null=True)  # New field for mobile number
    qr_code_data = models.BinaryField(blank=True, null=True)  # Store QR code as binary data
    photo = models.ImageField(upload_to=employee_photo_path, blank=True, null=True)
    location_lat = models.FloatField(null=True, blank=True)
    location_lon = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.employee_id})"  # Display name and ID in admin

    def save(self, *args, **kwargs):
        if not self.employee_id:
            combined_data = f"{self.name}{self.gender}{self.designation}{self.email}{self.dob}{self.mobile_number}{self.aadhar_number}" # Use first 8 characters of hash
            counter = 0
            while True:
                hashed_data = hashlib.sha256(f"{combined_data}{counter}".encode()).hexdigest()
                numeric_hash = int(hashed_data, 16) % 900000 + 100000  # Ensure it's between 100000 and 999999
                if not Employee.objects.filter(employee_id=numeric_hash).exists():
                    self.employee_id = numeric_hash
                    break
                counter += 1

        qr_data = f"https://internalakhandbharatcommando.com{reverse('employee:employee-attendance', kwargs={'employee_id': self.employee_id})}"

        # Generate QR Code
        qr = qrcode.QRCode(
        version=1,
        box_size=10,
        border=4,
        error_correction=qrcode.constants.ERROR_CORRECT_H  # High error correction for logo tolerance
    )
        qr.add_data(qr_data)
        qr.make(fit=True)

        # Create an image from the QR Code instance
        img = qr.make_image(fill_color="black", back_color="white").convert('RGB')

        # === Add logo in the center ===
        logo_path = 'static/images/logo.jpeg'  # Adjust path if needed
        try:
            logo = Image.open(logo_path)
            # Resize logo
            qr_width, qr_height = img.size
            logo_size = int(qr_width * 0.25)  # 25% of the QR code
            logo = logo.resize((logo_size, logo_size), Image.LANCZOS)

            # Calculate position to paste
            pos = ((qr_width - logo_size) // 2, (qr_height - logo_size) // 2)

            # Paste logo (with transparency mask if available)
            if logo.mode in ("RGBA", "LA"):
                img.paste(logo, pos, mask=logo)
            else:
                img.paste(logo, pos)
        except FileNotFoundError:
            # If logo is not found, just use the plain QR
            pass

        # Save image to a BytesIO buffer
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)

        # Save binary data to qr_code_data field
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

class Attendance(models.Model):
    employee = models.ForeignKey('Employee', on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)  # Automatically set to today's date
    entry_time = models.TimeField(blank=True, null=True)
    exit_time = models.TimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.employee.name} - {self.date}"