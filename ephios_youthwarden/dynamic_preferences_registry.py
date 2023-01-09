from django.utils.translation import gettext_lazy as _
from dynamic_preferences.types import BooleanPreference
from ephios.core.dynamic_preferences_registry import event_type_preference_registry


@event_type_preference_registry.register
class NeedsYouthwardenApproval(BooleanPreference):
    name = "needs_youthwarden_approval"
    verbose_name = _("Minors need to be approved by youthwardens before participating in this eventtype")
    default = False
