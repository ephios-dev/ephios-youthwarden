from django.dispatch import receiver
from django.template.loader import render_to_string
from django.utils.translation import gettext as _
from ephios.core.signals import (
    participant_signup_checkers,
    register_consequence_handlers,
    shift_info,
    register_group_permission_fields,
)
from ephios.core.signup.flow.participant_validation import ParticipantUnfitError
from ephios.core.signup.participants import LocalUserParticipant
from ephios.extra.permissions import PermissionField

from ephios_youthwarden.consequences import MinorParticipationRequestConsequenceHandler
from ephios_youthwarden.models import MinorParticipationRequest


def check_minors(shift, participant):
    if (
        not isinstance(participant, LocalUserParticipant)
        or not participant.user.is_minor
        or not shift.event.type.preferences["needs_youthwarden_approval"]
    ):
        return None
    try:
        request = MinorParticipationRequest.objects.get(
            user=participant.user, shift=shift
        )
        if request.state == MinorParticipationRequest.States.APPROVED:
            return
        elif request.state == MinorParticipationRequest.States.DENIED:
            raise ParticipantUnfitError(
                _("Your youth warden does not allow you to participate in this shift.")
            )
        elif request.state == MinorParticipationRequest.States.PENDING:
            raise ParticipantUnfitError(
                _("Approval from your youth warden is pending.")
            )
    except MinorParticipationRequest.DoesNotExist:
        raise ParticipantUnfitError(
            _("You need to get approval from your youth warden first.")
        )


@receiver(
    participant_signup_checkers,
    dispatch_uid="ephios_youthwarden.signals.register_check_minors",
)
def register_check_minors(sender, **kwargs):
    return [check_minors]


@receiver(
    register_consequence_handlers,
    dispatch_uid="ephios_youthwarden.signals.register_consequence_handlers",
)
def register_consequence_handlers(sender, **kwargs):
    return [MinorParticipationRequestConsequenceHandler]


@receiver(shift_info, dispatch_uid="ephios_youthwarden.signals.shift_info")
def shift_info(sender, shift, request, **kwargs):
    if (
        not request.user.is_anonymous
        and request.user.is_minor
        and not MinorParticipationRequest.objects.filter(
            user=request.user, shift=shift
        ).exists()
        and shift.event.type.preferences["needs_youthwarden_approval"]
    ):
        return render_to_string(
            "ephios_youthwarden/minor_shift_request.html", {"shift": shift}
        )


@receiver(
    register_group_permission_fields,
    dispatch_uid="ephios_youthwarden.signals.register_group_permission_fields",
)
def group_permission_fields(sender, **kwargs):
    return [
        (
            "decide_minor_participation_request",
            PermissionField(
                label=_("Decide about participation of minors"),
                help_text=_(
                    "Enables this group to approve or deny participation of minors in shifts."
                ),
                permissions=[
                    "ephios_youthwarden.view_minorparticipationrequest",
                    "ephios_youthwarden.add_minorparticipationrequest",
                    "ephios_youthwarden.change_minorparticipationrequest",
                    "ephios_youthwarden.delete_minorparticipationrequest",
                ],
            ),
        )
    ]
