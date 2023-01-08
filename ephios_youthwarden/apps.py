from ephios.core.plugins import PluginConfig


class PluginApp(PluginConfig):
    name = "ephios_youthwarden"

    class EphiosPluginMeta:
        name = "ephios_youthwarden"
        author = "Julian B. <julian@ephios.de>"
        description = "This plugin lets youth wardens decide about participations of minors"

    def ready(self):
        from . import signals  # NOQA
