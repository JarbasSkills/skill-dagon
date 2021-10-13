from os.path import join, dirname

from json_database import JsonStorage
from ovos_workshop.skills.common_play import OVOSCommonPlaybackSkill, \
    MediaType, PlaybackType, ocp_search


class LovecraftComicsSkill(OVOSCommonPlaybackSkill):

    def __init__(self):
        super().__init__("LovecraftComics")
        self.supported_media = [MediaType.GENERIC,
                                MediaType.AUDIOBOOK,
                                MediaType.VISUAL_STORY,
                                MediaType.VIDEO]
        self.default_bg = join(dirname(__file__), "ui", "bg.png")
        self.default_image = join(dirname(__file__), "ui", "dagon.png")
        self.skill_icon = join(dirname(__file__), "ui", "icon.png")
        self.db = JsonStorage(join(dirname(__file__), "res",
                                   "JeremyZahn_lovecraft_comics.json"))
        self.db2 = JsonStorage(join(dirname(__file__), "res",
                                    "TanabeGou_lovecraft_comics.json"))

    def get_base_score(self, original, media_type):
        score = 0
        if media_type == MediaType.AUDIOBOOK:
            score += 10
        elif media_type == MediaType.VIDEO:
            score += 5
        elif media_type == MediaType.VISUAL_STORY:
            score += 30

        if self.voc_match(original, "reading") or \
                self.voc_match(original, "audio_theatre"):
            score += 10

        if self.voc_match(original, "lovecraft"):
            score += 30
            if self.voc_match(original, "video"):
                score += 10

        if self.voc_match(original, "comic"):
            score += 10
        return score

    @ocp_search()
    def ocp_motioncomics_lovecraft_playlist(self, phrase, media_type):
        score = self.get_base_score(phrase, media_type)
        if self.voc_match(phrase, "comic") or \
                media_type == MediaType.VISUAL_STORY:
            score += 10
            if self.voc_match(phrase, "lovecraft"):
                score += 30
        pl = [
            {
                "match_confidence": score,
                "media_type": MediaType.VISUAL_STORY,
                "uri": entry["uri"],
                "playback": PlaybackType.VIDEO,
                "image": entry["image"],
                "bg_image": self.default_bg,
                "skill_icon": self.skill_icon,
                "title": entry["title"],
                "author": "H. P. Lovecraft",
                "album": "Lovecraft Motion Comics by Jeremy Zahn"
            } for title, entry in self.db.items()
        ]
        pl2 = [
            {
                "match_confidence": score,
                "media_type": MediaType.VISUAL_STORY,
                "uri": entry["uri"],
                "playback": PlaybackType.VIDEO,
                "image": entry["image"],
                "bg_image": self.default_bg,
                "skill_icon": self.skill_icon,
                "title": entry["title"],
                "author": "H. P. Lovecraft",
                "album": "Lovecraft Illustrated by Tanabe Gou"
            } for title, entry in self.db2.items()
        ]

        return [{
            "match_confidence": score,
            "media_type": MediaType.VISUAL_STORY,
            "playlist": pl,
            "playback": PlaybackType.VIDEO,
            "skill_icon": self.skill_icon,
            "image": "https://img.youtube.com/vi/Gv1I0y6PHfg/hqdefault.jpg",
            "bg_image": self.default_image,
            "title": "Lovecraft Comics by Jeremy Zahn (Playlist)",
            "author": "H. P. Lovecraft",
            "album": "Lovecraft Motion Comics by Jeremy Zahn"
        }, {
            "match_confidence": score,
            "media_type": MediaType.VISUAL_STORY,
            "playlist": pl2,
            "playback": PlaybackType.VIDEO,
            "skill_icon": self.skill_icon,
            "image": "https://img.youtube.com/vi/jW_G7cGxCWY/hqdefault.jpg",
            "bg_image": self.default_image,
            "title": "Lovecraft Illustrated by Tanabe Gou (Playlist)",
            "author": "H. P. Lovecraft",
            "album": "Lovecraft Illustrated by Tanabe Gou"
        }]


def create_skill():
    return LovecraftComicsSkill()
