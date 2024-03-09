from django.contrib import admin
from .models import Patient, MedicationStatement, Chats
# Register your models here.


admin.site.register(Patient)
admin.site.register(MedicationStatement)
admin.site.register(Chats)