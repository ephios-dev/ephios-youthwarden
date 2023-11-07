from ephios.core.plugins import PluginConfig
from django.utils.translation import gettext_lazy as _

class PluginApp(PluginConfig):
    name = "ephios_youthwarden"

    class EphiosPluginMeta:
        name = _("Youth warden flow")
        author = "Julian B. <julian@ephios.de>"
        description = _("This plugin lets youth wardens decide about participations of minors.")

    def ready(self):
        from . import signals  # NOQA
