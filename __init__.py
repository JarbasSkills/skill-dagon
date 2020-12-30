from ovos_utils.waiting_for_mycroft.common_play import \
    CommonPlaySkill, CPSMatchLevel, CPSMatchType, CPSTrackStatus
import pafy
from tempfile import gettempdir
import re
import subprocess
from os.path import join, dirname, exists


class DagonSkill(CommonPlaySkill):

    def __init__(self):
        super().__init__("Dagon")
        if "download_audio" not in self.settings:
            self.settings["download_audio"] = True
        if "download_video" not in self.settings:
            self.settings["download_video"] = False
        if "audio_only" not in self.settings:
            self.settings["audio_only"] = False

        self.supported_media = [CPSMatchType.GENERIC,
                                CPSMatchType.AUDIOBOOK,
                                CPSMatchType.VISUAL_STORY,
                                CPSMatchType.VIDEO]

    def initialize(self):
        self.add_event('skill-dagon.jarbasskills.home',
                       self.handle_homescreen)
        if self.settings["download_audio"]:
            self.get_audio_stream(download=True)
        # if self.settings["download_video"]:
        #    self.get_video_stream(download=True)

    def get_intro_message(self):
        self.speak_dialog("intro")
        self.gui.show_image(join(dirname(__file__), "ui", "bg.png"))

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
            score += 0.2
            match = CPSMatchLevel.GENERIC
        elif media_type == CPSMatchType.VISUAL_STORY:
            score += 0.3
            match = CPSMatchLevel.CATEGORY

        if self.voc_match(original, "audio_theatre"):
            score += 0.15
            match = CPSMatchLevel.CATEGORY

        if self.voc_match(original, "lovecraft"):
            score += 0.5
            match = CPSMatchLevel.ARTIST

        phrase = self.clean_vocs(phrase)

        if self.voc_match(phrase, "dagon"):
            score += 0.75
            match = CPSMatchLevel.TITLE

        if score >= 0.85:
            match = CPSMatchLevel.EXACT

        if match is not None:
            return (phrase, match,
                    {"media_type": media_type, "query": original})
        return None

    def CPS_start(self, phrase, data):
        bg = join(dirname(__file__), "ui", "bg.png")
        image = join(dirname(__file__), "ui", "logo.png")
        url = "https://www.youtube.com/watch?v=Gv1I0y6PHfg"
        if self.gui.connected and not self.settings["audio_only"]:
            url = self.get_video_stream(url, self.settings["download_video"])
            self.gui.play_video(url)
        else:
            url = self.get_audio_stream(url, self.settings["download_audio"])
            self.audioservice.play(url, utterance=self.play_service_string)
            self.CPS_send_status(uri=url,
                                 image=image,
                                 background_image=bg,
                                 playlist_position=0,
                                 status=CPSTrackStatus.PLAYING_AUDIOSERVICE)

    def stop(self):
        self.gui.clear()

    # youtube handling
    @staticmethod
    def get_audio_stream(url="https://www.youtube.com/watch?v=Gv1I0y6PHfg",
                         download=False):
        myvid = pafy.new(url)
        stream = myvid.getbestaudio()

        # TODO check if https supported, if not download=True without
        #  needing user changing settings.json
        if download:
            path = join(gettempdir(),
                        url.split("watch?v=")[-1] + "." + stream.extension)
            mp3 = join(gettempdir(), url.split("watch?v=")[-1] + ".mp3")

            if not exists(mp3) and not exists(path):
                stream.download(path)

            if not exists(mp3):
                # convert file to allow playback with simple audio backend
                command = ["ffmpeg", "-n", "-i", path, "-acodec",
                           "libmp3lame",
                           "-ab", "128k", mp3]
                subprocess.call(command)

            return mp3
        return stream.url

    @staticmethod
    def get_video_stream(url="https://www.youtube.com/watch?v=Gv1I0y6PHfg",
                         download=False):
        video = pafy.new(url)
        playstream = video.streams[0]
        # TODO dl video ?
        # not worth caching
        return playstream.url


def create_skill():
    return DagonSkill()
