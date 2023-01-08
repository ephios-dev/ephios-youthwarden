from django.db import models
from django.utils.translation import gettext as _
from ephios.core.models import UserProfile, Shift


class MinorParticipationRequest(models.Model):
    class States(models.IntegerChoices):
        PENDING = 0, _("Pending")
        APPROVED = 1, _("Approved")
        DENIED = 2, _("Denied")

    class Meta:
        unique_together = ("user", "shift")

    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    shift = models.ForeignKey(Shift, on_delete=models.CASCADE)
    state = models.IntegerField(_("state"), choices=States.choices, default=States.PENDING)

    def __str__(self):
        return f"MinorParticipationRequest for {self.user} in {self.shift}"
