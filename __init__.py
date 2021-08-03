from ovos_utils import create_daemon
from ovos_workshop.skills.common_play import OVOSCommonPlaybackSkill
from ovos_workshop.frameworks.playback import CPSMatchType, CPSPlayback, \
    CPSMatchConfidence
import re
from os.path import join, dirname


class DagonSkill(OVOSCommonPlaybackSkill):

    def __init__(self):
        super().__init__("Dagon")
        self.supported_media = [CPSMatchType.GENERIC,
                                CPSMatchType.AUDIOBOOK,
                                CPSMatchType.VISUAL_STORY,
                                CPSMatchType.VIDEO]
        self.default_bg = join(dirname(__file__), "ui", "bg.png")
        self.default_image = join(dirname(__file__), "ui", "dagon.png")
        self.skill_logo = join(dirname(__file__), "ui", "logo.png")
        self.skill_icon = join(dirname(__file__), "ui", "icon.png")

    # better common play
    def CPS_search(self, phrase, media_type):
        """Analyze phrase to see if it is a play-able phrase with this skill.

        Arguments:
            phrase (str): User phrase uttered after "Play", e.g. "some music"
            media_type (CPSMatchType): requested CPSMatchType to search for

        Returns:
            search_results (list): list of dictionaries with result entries
            {
                "match_confidence": CPSMatchConfidence.HIGH,
                "media_type":  CPSMatchType.MUSIC,
                "uri": "https://audioservice.or.gui.will.play.this",
                "playback": CPSPlayback.GUI,
                "image": "http://optional.audioservice.jpg",
                "bg_image": "http://optional.audioservice.background.jpg"
            }
        """
        # there is a single video in this skill, let's simply calculate a
        # match score
        original = phrase
        score = 0

        if media_type == CPSMatchType.AUDIOBOOK:
            score += 10
        elif media_type == CPSMatchType.VIDEO:
            score += 5
        elif media_type == CPSMatchType.VISUAL_STORY:
            score += 30

        if self.voc_match(original, "reading") or\
                self.voc_match(original, "audio_theatre"):
            score += 10

        if self.voc_match(original, "lovecraft"):
            score += 30
            if self.voc_match(original, "video"):
                score += 10

        if self.voc_match(phrase, "dagon"):
            score += 70

        if score >= CPSMatchConfidence.AVERAGE_LOW:
            # returning both GUI and AUDIO options, better-playback-skill
            # will select which one to play, a check for self.gui.connected
            # in here introduces latency and penalizes this skill
            return [
                {
                    "match_confidence": min(100, score),
                    "media_type": CPSMatchType.VISUAL_STORY,
                    "uri": "https://www.youtube.com/watch?v=Gv1I0y6PHfg",
                    "playback": CPSPlayback.GUI,
                    "image": self.default_image,
                    "bg_image": self.default_bg,
                    "skill_icon": self.skill_icon,
                    "skill_logo": self.skill_logo,
                    "title": "DAGON",
                    "author": "H. P. Lovecraft",
                    'length': 1135 * 1000
                },
                {   # bonus score for GUI playback
                    "match_confidence": min(100, score - 1),
                    "media_type": CPSMatchType.AUDIOBOOK,
                    "uri": "https://www.youtube.com/watch?v=Gv1I0y6PHfg",
                    "playback": CPSPlayback.AUDIO,
                    "image": self.default_image,
                    "bg_image": self.default_bg,
                    "skill_icon": self.skill_icon,
                    "skill_logo": self.skill_logo,
                    "title": "DAGON (audio)",
                    "author": "H. P. Lovecraft",
                    'length': 1135 * 1000,
                    "album": "read by Wayne June"
                }]
        return None


def create_skill():
    return DagonSkill()


