from django.db.models import Q, BooleanField, Value
from ephios.core.consequences import BaseConsequenceHandler
from ephios.core.models import UserProfile, Shift, Consequence

from ephios_youthwarden.models import MinorParticipationRequest

from django.utils.translation import gettext as _


class MinorParticipationRequestConsequenceHandler(BaseConsequenceHandler):
    slug = "ephios_youthwarden.decide_minor_participation_request"

    @classmethod
    def create(cls, user: UserProfile, shift: Shift):
        return Consequence.objects.create(
            slug=cls.slug,
            user=user,
            data=dict(shift=shift.pk),
        )

    @classmethod
    def execute(cls, consequence):
        request = MinorParticipationRequest.objects.get(
            user=consequence.user,
            shift=consequence.data["shift"],
        )
        request.state = MinorParticipationRequest.States.APPROVED
        request.save()

    @classmethod
    def render(cls, consequence):
        return _("{user} wants to participate in {shift}").format(
            user=consequence.user.get_full_name(),
            shift=Shift.objects.get(pk=consequence.data["shift"]),
        )

    @classmethod
    def filter_queryset(cls, qs, user: UserProfile):
        if not user.has_perm("ephios_youthwarden.change_minorparticipationrequest"):
            return qs.filter(
                ~Q(slug=cls.slug)
            )
        return qs
