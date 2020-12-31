from ovos_utils.skills.templates.media_player import MediaSkill, \
    CPSMatchType, CPSMatchLevel
from os.path import join, dirname


class DagonSkill(MediaSkill):

    def __init__(self):
        super().__init__("Dagon")
        self.supported_media = [CPSMatchType.GENERIC,
                                CPSMatchType.AUDIOBOOK,
                                CPSMatchType.VISUAL_STORY,
                                CPSMatchType.VIDEO]
        self.default_bg = join(dirname(__file__), "ui", "bg.png")
        self.default_image = join(dirname(__file__), "ui", "logo.png")
        self.message_namespace = 'skill-dagon.jarbasskills.home'
        self.bootstrap_list = ["https://www.youtube.com/watch?v=Gv1I0y6PHfg"]

    def get_intro_message(self):
        self.speak_dialog("intro")
        self.gui.show_image(join(dirname(__file__), "ui", "dagon.png"))

    # common play
    def clean_vocs(self, phrase):
        phrase = self.remove_voc(phrase, "reading")
        phrase = self.remove_voc(phrase, "lovecraft")
        phrase = self.remove_voc(phrase, "video")
        phrase = self.remove_voc(phrase, "audio_theatre")
        phrase = self.remove_voc(phrase, "play")
        phrase = phrase.strip()
        return phrase

    def CPS_match_query_phrase(self, phrase, media_type):

        original = phrase
        match = None
        score = 0

        if media_type == CPSMatchType.AUDIOBOOK:
            score += 0.1
            match = CPSMatchLevel.GENERIC
        elif media_type == CPSMatchType.VIDEO:
            score += 0.15
            match = CPSMatchLevel.GENERIC
        elif media_type == CPSMatchType.VISUAL_STORY:
            score += 0.3
            match = CPSMatchLevel.CATEGORY

        if self.voc_match(original, "reading"):
            score += 0.1
            match = CPSMatchLevel.GENERIC

        if self.voc_match(original, "audio_theatre"):
            score += 0.1
            match = CPSMatchLevel.CATEGORY

        if self.voc_match(original, "video"):
            score += 0.1
            match = CPSMatchLevel.CATEGORY

        phrase = self.clean_vocs(phrase)

        if self.voc_match(phrase, "lovecraft"):
            score += 0.3
            match = CPSMatchLevel.ARTIST
            if self.voc_match(original, "video"):
                score += 0.1
                match = CPSMatchLevel.MULTI_KEY

        if self.voc_match(phrase, "dagon"):
            score += 0.75
            if match is not None:
                match = CPSMatchLevel.MULTI_KEY
            else:
                match = CPSMatchLevel.TITLE

        if score >= 0.9:
            match = CPSMatchLevel.EXACT

        if match is not None:
            return (phrase, match,
                    {"media_type": media_type, "query": original,
                     "image": self.default_image, "background": self.default_bg,
                     "stream": "https://www.youtube.com/watch?v=Gv1I0y6PHfg"})
        return None


def create_skill():
    return DagonSkill()
