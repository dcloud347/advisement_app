from rest_framework.routers import SimpleRouter

from advisement_datastore.views import PatientViewSet, MedicationStatementViewSet, ChatViewSet

router = SimpleRouter()
router.register('patients', PatientViewSet)
router.register('medication-statement', MedicationStatementViewSet)
router.register('chat', ChatViewSet)

urlpatterns = router.urls
