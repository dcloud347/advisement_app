from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from .models import Patient, MedicationStatement, Chats, Messages
from .serializers import PatientSerializer, MedicationStatementSerializer, ChatSerializer, MessagesSerializer
from util.Req import Req, patient_info_url, medication_statement_info_url
from util.openai_tools import OpenAITools


def get_name(resource):
    try:
        name_resource = resource['name']
    except KeyError:
        return None
    name = name_resource[0]
    try:
        return name['text']
    except KeyError:
        pass
    try:
        family_name = name['family']
    except KeyError:
        family_name = ""
    try:
        given_name = " ".join(name['given'])
    except KeyError:
        given_name = ""
    return given_name + " " + family_name


def process_patient_data(patient_data):
    try:
        data = patient_data['entry']
    except KeyError:
        return Response(data="No Patient Found", status=status.HTTP_400_BAD_REQUEST)
    for i in data:
        resource = i['resource']
        id = resource['id']
        name = get_name(resource)
        try:
            phone = resource['phone'][0]['value']
        except KeyError:
            phone = None
        try:
            address = ','.join(resource['address'][0]['line'])
        except KeyError:
            address = None
        Patient.objects.update_or_create(defaults={'id': id, 'name': name, 'telephone': phone, 'address': address},
                                         id=id)


class PatientViewSet(ReadOnlyModelViewSet):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    lookup_field = 'id'

    @action(detail=False, methods=['get'])
    def save(self, request, *args, **kwargs):
        data = Req.get(patient_info_url, data=request.query_params)
        process_patient_data(data)
        return Response(status=status.HTTP_200_OK)


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
        patient_id_array = []
        for i in data:
            resource = i['resource']
            id = resource['id']
            try:
                medication_statement = resource['medicationCodeableConcept']['text'] + " " + resource['dosage'][0][
                    'text']
            except KeyError:
                medication_statement = None
            patient_id = resource['subject']['reference'].split('/')[1]
            try:
                if patient_id != "":
                    patient_id = Patient.objects.get(id=patient_id).id
            except Patient.DoesNotExist:
                patient_id_array.append(patient_id)
            if medication_statement is not None:
                result.append({'id': id, 'medication_statement': medication_statement, 'patient_id': patient_id})
        patient_id_array = list(set(patient_id_array))
        process_patient_data(Req.get(patient_info_url, {"_id": ",".join(patient_id_array)}))
        for data in result:
            MedicationStatement.objects.update_or_create(defaults=data, id=data['id'])
        return Response(status=status.HTTP_200_OK)

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
        return Response({"result": result, "chat": chat.id}, status=status.HTTP_200_OK)


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
