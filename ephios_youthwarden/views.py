from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.views.generic import RedirectView
from django.utils.translation import gettext as _
from django.views.generic.detail import SingleObjectMixin

from ephios.core.models import Shift
from ephios.extra.mixins import CustomPermissionRequiredMixin

from ephios_youthwarden.consequences import MinorParticipationRequestConsequenceHandler
from ephios_youthwarden.models import MinorParticipationRequest


class MinorParticipationRequestView(CustomPermissionRequiredMixin, SingleObjectMixin, RedirectView):
    model = Shift
    permission_required = "core.view_event"

    def get_permission_object(self):
        return self.get_object().event

    def get_redirect_url(self, *args, **kwargs):
        shift = self.get_object()
        if not MinorParticipationRequest.objects.filter(user=self.request.user, shift=shift).exists():
            if self.request.user.is_minor:
                MinorParticipationRequest.objects.create(user=self.request.user, shift=shift)
                MinorParticipationRequestConsequenceHandler.create(self.request.user, shift)
                messages.success(self.request, _("Your request has been sent."))
        return shift.get_absolute_url()
