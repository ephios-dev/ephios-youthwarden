from django.dispatch import receiver
from django.template.loader import render_to_string
from django.utils.translation import gettext as _
from ephios.core.signals import check_participant_signup, register_consequence_handlers, shift_info, \
    register_group_permission_fields
from ephios.core.signup.methods import ParticipantUnfitError, check_participant_age
from ephios.core.signup.participants import LocalUserParticipant
from ephios.extra.permissions import PermissionField

from ephios_youthwarden.consequences import MinorParticipationRequestConsequenceHandler
from ephios_youthwarden.models import MinorParticipationRequest


@receiver(check_participant_signup, dispatch_uid="ephios_youthwarden.signals.check_minors")
def check_minors(sender, method, participant, **kwargs):
    if not isinstance(participant, LocalUserParticipant) or not participant.user.is_minor or check_participant_age(method, participant) or not method.shift.event.type.preferences["needs_youthwarden_approval"]:
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
def shift_info(sender, shift, request, **kwargs):
    if request.user.is_minor and not MinorParticipationRequest.objects.filter(user=request.user, shift=shift).exists() and not check_participant_age(shift.signup_method, request.user.as_participant()) and shift.event.type.preferences["needs_youthwarden_approval"]:
        return render_to_string("ephios_youthwarden/minor_shift_request.html", {"shift": shift})


@receiver(register_group_permission_fields, dispatch_uid="ephios_youthwarden.signals.register_group_permission_fields")
def group_permission_fields(sender, **kwargs):
    return [("decide_minor_participation_request", PermissionField(
        label=_("Decide about participation of minors"),
        help_text=_("Enables this group to approve or deny participation of minors in shifts."),
        permissions=[
            "ephios_youthwarden.view_minorparticipationrequest",
            "ephios_youthwarden.add_minorparticipationrequest",
            "ephios_youthwarden.change_minorparticipationrequest",
            "ephios_youthwarden.delete_minorparticipationrequest",
        ],
    ))]
