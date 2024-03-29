from rest_framework import serializers
from .models import Patient, MedicationStatement, Messages, Chats


class PatientSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()

    class Meta:
        model = Patient
        fields = "__all__"


class MedicationStatementSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source='patient.name')
    id = serializers.IntegerField()

    class Meta:
        model = MedicationStatement
        fields = "__all__"


class MessagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Messages
        fields = ['content', 'role']


class ChatSerializer(serializers.ModelSerializer):
    medical_statement = MedicationStatementSerializer(read_only=True)
    messages = MessagesSerializer(read_only=True, many=True)

    class Meta:
        model = Chats
        fields = "__all__"
