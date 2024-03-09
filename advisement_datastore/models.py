from django.db import models


class Patient(models.Model):
    id = models.BigIntegerField(primary_key=True, unique=True)
    name = models.CharField(max_length=300, blank=True, null=True, verbose_name="Patient Name")
    address = models.CharField(max_length=300, blank=True, null=True, verbose_name="Patient Address")
    telephone = models.CharField(max_length=30, blank=True, null=True, verbose_name="telephone")

    class Meta:
        db_table = "Patient"
        verbose_name = 'Patient'
        verbose_name_plural = verbose_name


class MedicationStatement(models.Model):
    id = models.BigIntegerField(primary_key=True, unique=True)
    medication_statement = models.CharField(max_length=300, verbose_name="Medication Statement")
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="medication_statement",
                                verbose_name="Patient", null=True, blank=True)

    class Meta:
        db_table = "MedicationStatement"
        verbose_name = 'MedicationStatement'
        verbose_name_plural = verbose_name


class Chats(models.Model):
    medication_statement = models.ForeignKey(MedicationStatement, on_delete=models.CASCADE,
                                             related_name="chats", verbose_name="Medication Statement")

    class Meta:
        db_table = "Chats"
        verbose_name = 'Chats'
        verbose_name_plural = verbose_name


class Messages(models.Model):
    chat = models.ForeignKey(Chats, on_delete=models.CASCADE, related_name="messages", verbose_name="Chat")
    content = models.CharField(max_length=400, verbose_name="Message")
    role = models.CharField(max_length=400, verbose_name="role")

    class Meta:
        db_table = "Messages"
        verbose_name = 'Messages'
        verbose_name_plural = verbose_name
