from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.views.generic import RedirectView
from django.utils.translation import gettext as _
from ephios.core.models import Shift

from ephios_youthwarden.consequences import MinorParticipationRequestConsequenceHandler
from ephios_youthwarden.models import MinorParticipationRequest


class MinorParticipationRequestView(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        shift = get_object_or_404(Shift, pk=kwargs["pk"])
        if not MinorParticipationRequest.objects.filter(user=self.request.user, shift=shift).exists():
            if self.request.user.is_minor:
                MinorParticipationRequest.objects.create(user=self.request.user, shift=shift)
                MinorParticipationRequestConsequenceHandler.create(self.request.user, shift)
                messages.success(self.request, _("Your request has been sent."))
        return shift.get_absolute_url()
