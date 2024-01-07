from os.path import join, dirname

from json_database import JsonStorage

from ovos_utils.ocp import MediaType, PlaybackType
from ovos_workshop.decorators.ocp import ocp_search, ocp_featured_media
from ovos_workshop.skills.common_play import OVOSCommonPlaybackSkill


class LovecraftComicsSkill(OVOSCommonPlaybackSkill):

    def __init__(self, *args, **kwargs):
        self.supported_media = [MediaType.AUDIOBOOK,
                                MediaType.VISUAL_STORY,
                                MediaType.VIDEO]
        self.default_bg = join(dirname(__file__), "ui", "bg.png")
        self.default_image = join(dirname(__file__), "ui", "dagon.png")
        self.skill_icon = join(dirname(__file__), "ui", "icon.png")
        self.db = JsonStorage(join(dirname(__file__), "res",
                                   "JeremyZahn_lovecraft_comics.json"))
        self.db2 = JsonStorage(join(dirname(__file__), "res",
                                    "TanabeGou_lovecraft_comics.json"))
        super().__init__(*args, **kwargs)
        self.load_ocp_keywords()

    def load_ocp_keywords(self):
        book_names = list(self.db.keys()) + list(self.db2.keys())
        book_authors = ["H. P. Lovecraft", "Lovecraft"]
        director = ["Tanabe Gou", "Jeremy Zahn"]
        playlist = ["Lovecraft Illustrated by Tanabe Gou",
                    "Lovecraft Motion Comics by Jeremy Zahn"]

        self.register_ocp_keyword(MediaType.AUDIOBOOK,
                                  "book_author",
                                  list(set(book_authors)))
        self.register_ocp_keyword(MediaType.AUDIOBOOK,
                                  "book_name",
                                  list(set(book_names)))
        self.register_ocp_keyword(MediaType.VISUAL_STORY,
                                  "comic_director",
                                  list(set(director)))
        self.register_ocp_keyword(MediaType.VISUAL_STORY,
                                  "comic_playlist",
                                  list(set(playlist)))
        self.register_ocp_keyword(MediaType.VISUAL_STORY,
                                  "comic_streaming_provider",
                                  ["Lovecraft", "LovecraftComics",
                                   "Lovecraft Comics"])

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
    def search_db(self, phrase, media_type):
        score = 15 if media_type == MediaType.VISUAL_STORY else 0
        entities = self.ocp_voc_match(phrase)
        score += 30 * len(entities)
        title = entities.get("book_name")

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

        if title:
            score += 30
            if title in self.db:
                entry = self.db.get(title)
                yield {
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
                }
            if title in self.db2:
                entry = self.db2.get(title)
                yield {
                    "match_confidence": score,
                    "media_type": MediaType.VISUAL_STORY,
                    "uri": entry["uri"],
                    "playback": PlaybackType.VIDEO,
                    "image": entry["image"],
                    "bg_image": self.default_bg,
                    "skill_icon": self.skill_icon,
                    "title": entry["title"],
                    "author": "H. P. Lovecraft",
                    "album": "Lovecraft Motion Comics by Tanabe Gou"
                }
        elif entities.get("comic_director", "") == "Jeremy Zahn":
            yield {
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
            }
        elif entities.get("comic_director", "") == "Tanabe Gou":
            yield {
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
            }
        elif media_type == MediaType.VISUAL_STORY:
            yield {
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
            }

            yield {
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
            }

    @ocp_featured_media()
    def featured_media(self):
        pl = [
            {
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
        return pl + pl2


if __name__ == "__main__":
    from ovos_utils.messagebus import FakeBus

    s = LovecraftComicsSkill(bus=FakeBus(), skill_id="t.fake")
    for r in s.search_db("Dagon", MediaType.VISUAL_STORY):
        print(r)
        # {'match_confidence': 75, 'media_type': <MediaType.VISUAL_STORY: 13>, 'uri': 'youtube//https://www.youtube.com/watch?v=Gv1I0y6PHfg', 'playback': <PlaybackType.VIDEO: 1>, 'image': 'https://img.youtube.com/vi/Gv1I0y6PHfg/hqdefault.jpg', 'bg_image': '/home/miro/PycharmProjects/OCP_sprint/skills/skill-dagon/ui/bg.png', 'skill_icon': 'https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/raw/master/ovos_plugin_common_play/ocp/res/ui/images/ocp.png', 'title': 'Dagon (Motion Comic)', 'author': 'H. P. Lovecraft', 'album': 'Lovecraft Motion Comics by Jeremy Zahn'}
        # {'match_confidence': 75, 'media_type': <MediaType.VISUAL_STORY: 13>, 'uri': 'youtube//https://www.youtube.com/watch?v=EskPmtogx18', 'playback': <PlaybackType.VIDEO: 1>, 'image': 'https://img.youtube.com/vi/EskPmtogx18/hqdefault.jpg', 'bg_image': '/home/miro/PycharmProjects/OCP_sprint/skills/skill-dagon/ui/bg.png', 'skill_icon': 'https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/raw/master/ovos_plugin_common_play/ocp/res/ui/images/ocp.png', 'title': 'Dagon', 'author': 'H. P. Lovecraft', 'album': 'Lovecraft Motion Comics by Tanabe Gou'}
