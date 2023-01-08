from django.dispatch import receiver
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _
from ephios.core.signals import check_participant_signup, register_consequence_handlers, shift_info
from ephios.core.signup.methods import ParticipantUnfitError, check_participant_age
from ephios.core.signup.participants import LocalUserParticipant

from ephios_youthwarden.consequences import MinorParticipationRequestConsequenceHandler
from ephios_youthwarden.models import MinorParticipationRequest


@receiver(check_participant_signup, dispatch_uid="ephios_youthwarden.signals.check_minors")
def check_minors(sender, method, participant, **kwargs):
    if not isinstance(participant, LocalUserParticipant) or not participant.user.is_minor or check_participant_age(method, participant):
        return None
    try:
        request = MinorParticipationRequest.objects.get(user=participant.user, shift=method.shift)
        if request.state == MinorParticipationRequest.States.APPROVED:
            return None
        elif request.state == MinorParticipationRequest.States.DENIED:
            return ParticipantUnfitError(_("Your youth warden does not allow you to participate in this shift."))
        elif request.state == MinorParticipationRequest.States.PENDING:
            return ParticipantUnfitError(_("Approval from your youth warden is pending."))
    except MinorParticipationRequest.DoesNotExist:
        return ParticipantUnfitError(_("You need to get approval from your youth warden first."))


@receiver(register_consequence_handlers, dispatch_uid="ephios_youthwarden.signals.register_consequence_handlers")
def register_consequence_handlers(sender, **kwargs):
    return [MinorParticipationRequestConsequenceHandler]


@receiver(shift_info, dispatch_uid="ephios_youthwarden.signals.shift_info")
def shift_info(sender, shift, request,**kwargs):
    if request.user.is_minor and not MinorParticipationRequest.objects.filter(user=request.user, shift=shift).exists() and not check_participant_age(shift.signup_method, request.user.as_participant()):
        return render_to_string("ephios_youthwarden/minor_shift_request.html", {"shift": shift})
