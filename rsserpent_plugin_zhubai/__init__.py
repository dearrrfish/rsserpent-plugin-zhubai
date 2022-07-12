from rsserpent.models import Persona, Plugin

from . import route


plugin = Plugin(
    name="rsserpent-plugin-zhubai",
    author=Persona(
        name="dearrrfish",
        link="https://github.com/dearrrfish/rsserpent-plugin-zhubai",
        email="im@yjin.dev",
    ),
    prefix="/zhubai",
    repository="https://github.com/dearrrfish/rsserpent-plugin-zhubai",
    routers={route.path: route.provider},
)
