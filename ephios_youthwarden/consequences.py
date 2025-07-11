from django.db.models import Q, BooleanField, Value
from ephios.core.consequences import BaseConsequenceHandler
from ephios.core.models import UserProfile, Shift, Consequence

from ephios_youthwarden.models import MinorParticipationRequest

from django.utils.translation import gettext as _


class MinorParticipationRequestConsequenceHandler(BaseConsequenceHandler):
    slug = "ephios_youthwarden.decide_minor_participation_request"

    @classmethod
    def create(cls, minor_request: MinorParticipationRequest):
        return Consequence.objects.create(
            slug=cls.slug,
            user=minor_request.user,
            data=dict(shift=minor_request.shift_id),
        )

    @classmethod
    def execute(cls, consequence):
        try:
            request = MinorParticipationRequest.objects.get(
                user=consequence.user,
                shift=consequence.data["shift"],
            )
            request.state = MinorParticipationRequest.States.APPROVED
            request.save()
        except (MinorParticipationRequest.DoesNotExist, Shift.DoesNotExist):
            # e.g. shift was deleted
            pass

    @classmethod
    def render(cls, consequence):
        try:
            shift_str = str(Shift.objects.get(pk=consequence.data['shift']))
        except Shift.DoesNotExist:
            shift_str = _("deleted shift")
        return _("{user} wants to participate in {shift}").format(
            user=consequence.user.get_full_name(),
            shift=shift_str,
        )

    @classmethod
    def filter_queryset(cls, qs, user: UserProfile):
        if not user.has_perm("ephios_youthwarden.change_minorparticipationrequest"):
            return qs.filter(
                ~Q(slug=cls.slug)
            )
        return qs
