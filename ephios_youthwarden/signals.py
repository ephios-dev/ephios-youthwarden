import sys

from django.dispatch import receiver
from django.template.loader import render_to_string
from django.utils.translation import gettext as _
from dynamic_preferences.registries import global_preferences_registry

from ephios.core.models import Consequence
from ephios.core.signals import (
    participant_signup_checkers,
    register_consequence_handlers,
    insert_html,
    register_group_permission_fields, periodic_signal, HTML_SHIFT_INFO,
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
        return
    if "ephios_youthwarden" not in global_preferences_registry.manager().get(
            "general__enabled_plugins"
    ):
        return
    try:
        request = MinorParticipationRequest.objects.get(
            user=participant.user, shift=shift
        )
        if request.state == MinorParticipationRequest.States.APPROVED:
            pass  # all good
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


@receiver(insert_html, sender=HTML_SHIFT_INFO, dispatch_uid="ephios_youthwarden.signals.shift_info")
def shift_info(sender, shift, request, **kwargs):
    if (
        not request.user.is_anonymous
        and request.user.is_minor
        and shift.event.type.preferences["needs_youthwarden_approval"]
        and not MinorParticipationRequest.objects.filter(
            user=request.user, shift=shift
        ).exists()
    ):
        return render_to_string(
            "ephios_youthwarden/minor_shift_request.html", {"shift": shift}
        )
    return ""


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


@receiver(
    periodic_signal,
    dispatch_uid="ephios_youthwarden.signals.periodic",
)
def periodic_signal(sender, **kwargs):
    Consequence.objects.filter(
        slug=MinorParticipationRequestConsequenceHandler.slug,
        minor_request=None,  # it got deleted, perhaps because the shift was deleted
    ).delete()