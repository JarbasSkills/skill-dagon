from ovos_utils.waiting_for_mycroft.common_play import \
    CommonPlaySkill, CPSMatchLevel, CPSMatchType, CPSTrackStatus
from ovos_utils import create_daemon
from pyvod.utils import get_audio_stream, get_video_stream
import re
from os.path import join, dirname


class DagonSkill(CommonPlaySkill):

    def __init__(self):
        super().__init__("Dagon")
        if "download_audio" not in self.settings:
            self.settings["download_audio"] = False
        if "download_video" not in self.settings:
            self.settings["download_video"] = False
        if "audio_only" not in self.settings:
            self.settings["audio_only"] = False
        if "mp3_audio" not in self.settings:
            self.settings["mp3_audio"] = True
        self.supported_media = [CPSMatchType.GENERIC,
                                CPSMatchType.AUDIOBOOK,
                                CPSMatchType.VISUAL_STORY,
                                CPSMatchType.VIDEO]
        self.default_bg = join(dirname(__file__), "ui", "bg.png")
        self.default_image = join(dirname(__file__), "ui", "logo.png")

    def initialize(self):
        self.add_event('skill-dagon.jarbasskills.home',
                       self.handle_homescreen)
        create_daemon(self._bootstrap)

    def _bootstrap(self):
        # bootstrap, so data is cached
        url = "https://www.youtube.com/watch?v=Gv1I0y6PHfg"
        try:
            if self.settings["download_audio"]:
                get_audio_stream(url, download=True,
                                 to_mp3=self.settings["mp3_audio"])
            if self.settings["download_video"]:
                get_video_stream(url, download=True)
        except:
            pass

    def get_intro_message(self):
        self.speak_dialog("intro")
        self.gui.show_image(join(dirname(__file__), "ui", "dagon.png"))

    # homescreen
    def handle_homescreen(self, message):
        self.CPS_start("dagon", {"media_type": CPSMatchType.VIDEO})

    # common play
    def remove_voc(self, utt, voc_filename, lang=None):
        lang = lang or self.lang
        cache_key = lang + voc_filename

        if cache_key not in self.voc_match_cache:
            self.voc_match(utt, voc_filename, lang)

        if utt:
            # Check for matches against complete words
            for i in self.voc_match_cache[cache_key]:
                # Substitute only whole words matching the token
                utt = re.sub(r'\b' + i + r"\b", "", utt)

        return utt

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

    def CPS_start(self, phrase, data):
        bg = data.get("background") or self.default_bg
        image = data.get("image") or self.default_image
        url = data.get("stream")
        if self.gui.connected and not self.settings["audio_only"]:
            url = get_video_stream(url,
                                   download=self.settings["download_video"])
            self.CPS_send_status(uri=url,
                                 image=image,
                                 background_image=bg,
                                 playlist_position=0,
                                 status=CPSTrackStatus.PLAYING_GUI)
            self.gui.play_video(url, "Dagon , by H. P. Lovecraft")
        else:
            url = get_audio_stream(url,
                                   download=self.settings["download_audio"],
                                   to_mp3=self.settings["mp3_audio"])
            self.audioservice.play(url, utterance=self.play_service_string)
            self.CPS_send_status(uri=url,
                                 image=image,
                                 background_image=bg,
                                 playlist_position=0,
                                 status=CPSTrackStatus.PLAYING_AUDIOSERVICE)

    def stop(self):
        self.gui.release()


def create_skill():
    return DagonSkill()
