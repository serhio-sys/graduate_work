from django.utils.translation import gettext_lazy as _

LOG_PATTERNS = {
    "attack":{
        "simple": _("<a href=\"#\">%s</a> провів атаку по <a href=\"#\">%s</a> завдавши %d урона."),
        
        "shooter": _("<a href=\"#\">%s</a> збільшивши відстань між ворогом "
        "<a href=\"#\">%s</a> робить декілька пострілів лишивши поранення у вигляді %d урона."),
        
        "agility": _("<a href=\"#\">%s</a> ухиляючись від атаки наносить по "
        "<a href=\"#\">%s</a> колюче поранення в розмірі %d урона.")
    },
    "defence":{
        "simple": _("<a href=\"#\">%s</a> заблокував атаку <a href=\"#\">%s</a>."),
        "shooter": _("<a href=\"#\">%s</a> відчувши атаку ворога"
        " <a href=\"#\">%s</a> було заблоковано атаку."),
        "agility": _("<a href=\"#\">%s</a> відчувши атаку ворога"
        " <a href=\"#\">%s</a> було заблоковано атаку.")
    },
    "effect":{
        "bliding":_("<a href=\"#\">%s</a> дуже прудким і ріжучим ударом у"
        " <a href=\"#\">%s</a> сталася сильна кровотеча."),
        "bones":_("<a href=\"#\">%s</a> сильним ударом ноги у"
        " <a href=\"#\">%s</a> було накладено ефект перелому.")
    }
}


def get_text_effect(who: str, whom:str, type_l: str) -> str:
    log_pattern = LOG_PATTERNS.get("effect", {}).get(type_l, "")
    return log_pattern % (who, whom)


def get_text_attack(who: str, whom:str, type_l:str, **kwargs) -> str:
    log_pattern = LOG_PATTERNS.get("attack", {}).get(type_l, "")
    return log_pattern % (who, whom, kwargs['dmg'])


def get_text_defence(who: str, whom:str, type_l:str) -> str:
    log_pattern = LOG_PATTERNS.get("defence", {}).get(type_l, "")
    return log_pattern % (whom, who)


def select_log(who: str, whom:str, dmg: int, type: str = "simple") -> callable:
    if dmg > 0:
        return get_text_attack(who, whom, type, dmg=dmg)
    return get_text_defence(who, whom, type)
    