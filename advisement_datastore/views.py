from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from .models import Patient, MedicationStatement, Chats, Messages
from .serializers import PatientSerializer, MedicationStatementSerializer, ChatSerializer, MessagesSerializer
from util.Req import Req, patient_info_url, medication_statement_info_url
from util.openai_tools import OpenAITools


class PatientViewSet(ReadOnlyModelViewSet):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    lookup_field = 'id'

    @action(detail=False, methods=['get'])
    def save(self, request, *args, **kwargs):
        patient_data = Req.get(patient_info_url, data=request.query_params)
        try:
            data = patient_data['entry']
        except KeyError:
            return Response(data="No Patient Found", status=status.HTTP_400_BAD_REQUEST)
        result = []
        for i in data:
            resource = i['resource']
            id = resource['id']
            try:
                name = resource['name'][0]['text']
            except KeyError:
                name = None
            try:
                phone = resource['phone'][0]['value']
            except KeyError:
                phone = None
            try:
                address = ','.join(resource['address'][0]['line'])
            except KeyError:
                address = None
            result.append({'id': id, 'name': name, 'phone': phone, 'address': address})
        serializer = PatientSerializer(data=result, many=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        return Response(data=result, status=status.HTTP_200_OK)


class MedicationStatementViewSet(ReadOnlyModelViewSet):
    queryset = MedicationStatement.objects.all()
    serializer_class = MedicationStatementSerializer
    lookup_field = 'id'

    @action(detail=False, methods=['get'])
    def save(self, request, *args, **kwargs):
        medication_statement_data = Req.get(medication_statement_info_url, data=request.query_params)
        try:
            data = medication_statement_data['entry']
        except KeyError:
            return Response(data="No Medication Statement Found", status=status.HTTP_400_BAD_REQUEST)
        result = []
        for i in data:
            resource = i['resource']
            id = resource['id']
            try:
                medication_statement = resource['medicationCodeableConcept']['text'] + resource['dosage'][0]['text']
            except KeyError:
                medication_statement = None
            try:
                patient_id = Patient.objects.get(id=request.query_params.get('patient')).id
            except Patient.DoesNotExist:
                patient_id = None
            if medication_statement is not None:
                result.append({'id': id, 'medication_statement': medication_statement, 'patient_id': patient_id})
        serializer = MedicationStatementSerializer(data=result, many=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        return Response(data=result, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def start(self, request, *args, **kwargs):
        medication_statement = self.get_object()
        chat = Chats.objects.create(medication_statement=medication_statement)
        Messages.objects.create(chat=chat, content='You are now an expert in medication,'
                                                   ' please introduce the medication statement.', role='system')
        messages = MessagesSerializer(chat.messages, many=True).data
        result, role = OpenAITools.get_advisement(medication_statement.medication_statement, messages)
        Messages.objects.create(chat=chat, content=medication_statement.medication_statement, role='user')
        Messages.objects.create(chat=chat, content=result, role=role)
        return Response(result, status=status.HTTP_200_OK)


class ChatViewSet(ReadOnlyModelViewSet):
    queryset = Chats.objects.all()
    serializer_class = ChatSerializer
    lookup_field = 'id'

    @action(detail=True, methods=['post'])
    def chat(self, request, *args, **kwargs):
        chat = self.get_object()
        messages = MessagesSerializer(chat.messages, many=True).data
        result, role = OpenAITools.get_advisement(request.data['message'], messages)
        Messages.objects.create(chat=chat, content=request.data['message'], role='user')
        Messages.objects.create(chat=chat, content=result, role=role)
        return Response(data=result, status=status.HTTP_200_OK)
