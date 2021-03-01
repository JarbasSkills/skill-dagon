from ovos_utils import create_daemon
from ovos_utils.skills.templates.common_play import BetterCommonPlaySkill
from ovos_utils.playback import CPSMatchType, CPSPlayback, CPSMatchConfidence
from pyvod.utils import get_audio_stream, get_video_stream
import re
from os.path import join, dirname


class DagonSkill(BetterCommonPlaySkill):

    def __init__(self):
        super().__init__("Dagon")
        self.supported_media = [CPSMatchType.GENERIC,
                                CPSMatchType.AUDIOBOOK,
                                CPSMatchType.VISUAL_STORY,
                                CPSMatchType.VIDEO]
        self.default_bg = join(dirname(__file__), "ui", "bg.png")
        self.default_image = join(dirname(__file__), "ui", "logo.png")

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
            score += 0.1
        elif media_type == CPSMatchType.VIDEO:
            score += 0.15
        elif media_type == CPSMatchType.VISUAL_STORY:
            score += 0.3

        if self.voc_match(original, "reading"):
            score += 0.1

        if self.voc_match(original, "audio_theatre"):
            score += 0.1

        if self.voc_match(original, "video"):
            score += 0.1

        if self.voc_match(original, "lovecraft"):
            score += 0.3
            if self.voc_match(original, "video"):
                score += 0.1

        if self.voc_match(phrase, "dagon"):
            score += 0.75

        score = score * 100
        if score >= CPSMatchConfidence.AVERAGE_LOW:
            # let's differentiate GUI vs AUDIO
            # TODO restore skill settings to allow override
            if self.gui.connected:
                return [
                    {
                        "match_confidence": min(100, score),
                        "media_type": CPSMatchType.VISUAL_STORY,
                        "uri": "https://www.youtube.com/watch?v=Gv1I0y6PHfg",
                        "playback": CPSPlayback.GUI
                    }]
            else:
                return [
                    {
                        "match_confidence": min(100, score - 15),
                        "media_type": CPSMatchType.AUDIOBOOK,
                        "uri": "https://www.youtube.com/watch?v=Gv1I0y6PHfg",
                        "playback": CPSPlayback.AUDIO,
                        "image": self.default_image,
                        "bg_image": self.default_bg
                    }]
        return None


def create_skill():
    return DagonSkill()
