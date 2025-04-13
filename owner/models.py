from django.db import models
import hashlib
class Owner(models.Model):
    owner_id = models.CharField(max_length=10, primary_key=True, blank=True)  # Use owner ID as primary key
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)  # Store hashed passwords
    # Add other relevant fields
    name = models.CharField(max_length=100)  # Example field for owner name
    dob = models.DateField(null=True)
    aadhar_number = models.CharField(max_length=12, unique=True, blank=True, null=True)  # New field for Aadhar number
    mobile_number = models.CharField(max_length=10, blank=True, null=True)  # New field for mobile number

    def __str__(self):
        return f"{self.name} ({self.owner_id})"  # Display name and ID in admin
    
    def save(self, *args, **kwargs):

        if not self.owner_id:
            combined_data = f"{self.name}{self.email}{self.dob}{self.mobile_number}{self.aadhar_number}" # Use first 8 characters of hash
            counter = 0
            while True:
                hashed_data = hashlib.sha256(f"{combined_data}{counter}".encode()).hexdigest()
                numeric_hash = int(hashed_data, 16) % 900000 + 100000  # Ensure it's between 100000 and 999999
                if not Owner.objects.filter(owner_id=numeric_hash).exists():
                    self.owner_id = numeric_hash
                    break
                counter += 1

        super().save(*args, **kwargs)

    @property
    def masked_aadhar_number(self):
        """Return last four digits of Aadhar number"""
        return f"xxxx xxxx {self.aadhar_number[-4:]}"
