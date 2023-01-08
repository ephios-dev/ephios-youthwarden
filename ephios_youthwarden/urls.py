from django.urls import path

from ephios_youthwarden.views import MinorParticipationRequestView

app_name = "ephios_youthwarden"

urlpatterns = [
    path("minors/shift-request/<int:pk>/", MinorParticipationRequestView.as_view(), name="minor_shift_request"),
]
