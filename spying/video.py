from moviepy.editor import VideoFileClip
from pydub import AudioSegment
from typing import Union
import cv2
import pyaudio
import wave
import threading
import time
import subprocess
import os

from spying.consts import DEFAULT_VIDEO_NAME, DEFAULT_AUDIO_NAME, FFMPEG_PATH


class Recorder:
    def __init__(self, filename):
        self.start_time = 0
        self.end_time = 0
        self.filename = filename
        self.open = False

    @property
    def length(self) -> Union[int, float]:
        if self.start_time == 0:
            return 0
        elif self.end_time == 0:
            return time.time() - self.start_time
        else:
            return self.end_time - self.start_time

    def _record(self) -> None:
        raise NotImplemented

    def stop(self) -> bool:
        raise NotImplemented

    def start(self) -> None:
        """Launches the recording function using a thread"""
        thread = threading.Thread(target=self._record)
        thread.start()


class AudioRecorder(Recorder):
    """Audio class based on pyAudio and Wave"""
    def __init__(self, filename=DEFAULT_AUDIO_NAME, rate=44100, fpb=1024, channels=None):
        super(AudioRecorder, self).__init__(filename)
        if not self.filename.endswith(".wav"): self.filename += ".wav"
        self.rate = rate
        self.frames_per_buffer = fpb
        self.format = pyaudio.paInt16
        self.audio = pyaudio.PyAudio()
        self.channels = channels if channels else self.audio.get_default_input_device_info()["maxInputChannels"]
        self.stream = self.audio.open(format=self.format,
                                      channels=self.channels,
                                      rate=self.rate,
                                      input=True,
                                      frames_per_buffer=self.frames_per_buffer)
        self.audio_frames = []

    def _record(self):
        """Audio starts being recorded"""
        self.open = True
        self.stream.start_stream()
        self.start_time = time.time()
        while self.open:
            data = self.stream.read(self.frames_per_buffer)
            self.audio_frames.append(data)
            if not self.open:
                break

    def stop(self):
        """Finishes the audio recording therefore the thread too"""
        if self.open:
            self.open = False
            self.stream.stop_stream()
            self.stream.close()
            self.audio.terminate()
            self.end_time = time.time()
            waveFile = wave.open(self.filename, 'wb')
            waveFile.setnchannels(self.channels)
            waveFile.setsampwidth(self.audio.get_sample_size(self.format))
            waveFile.setframerate(self.rate)
            waveFile.writeframes(b''.join(self.audio_frames))
            waveFile.close()
            return True
        else:
            return False
            # RuntimeError("cannot close a closed recorder")


class VideoRecorder(Recorder):
    def __init__(self, filename=DEFAULT_VIDEO_NAME, fourcc="MJPG", sizex=None, sizey=None, camindex=None, fps=30):
        super(VideoRecorder, self).__init__(filename)
        if not self.filename.endswith(".avi"): self.filename += ".avi"
        self.device_index = camindex if camindex else get_available_cameras()[0]
        self.fps = fps  # fps should be the minimum constant rate at which the camera can
        self.fourcc = fourcc  # capture images (with no decrease in speed over time; testing is required)
        self.video_cap = cv2.VideoCapture(self.device_index)
        sizex = int(self.video_cap.get(cv2.CAP_PROP_FRAME_WIDTH)) if not sizex else sizex
        sizey = int(self.video_cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) if not sizey else sizey
        self.frameSize = (sizex, sizey)  # video formats and sizes also depend and vary according to the camera used
        self.video_writer = cv2.VideoWriter_fourcc(*self.fourcc)
        self.video_out = cv2.VideoWriter(self.filename, self.video_writer, self.fps, self.frameSize)
        self.frame_counts = 1

    def _record(self):
        """starts to record"""
        self.start_time = time.time()
        self.open = True
        while self.open:
            ret, video_frame = self.video_cap.read()
            if ret:
                self.video_out.write(video_frame)
                #               print str(counter) + " " + str(self.frame_counts) + " frames written " + str(timer_current)
                self.frame_counts += 1
                #               counter += 1
                #               timer_current = time.time() - timer_start
                # time.sleep(1 / self.fps)
            #               gray = cv2.cvtColor(video_frame, cv2.COLOR_BGR2GRAY)
            #               cv2.imshow('video_frame', gray)
            #               cv2.waitKey(1)
            else:
                break

    def stop(self):
        """Finishes the video recording therefore the thread too"""
        if self.open:
            self.open = False
            self.video_out.release()
            self.video_cap.release()
            cv2.destroyAllWindows()
            self.end_time = time.time()

            frame_counts = self.frame_counts
            elapsed_time = self.length
            if elapsed_time == 0:
                return False
            recorded_fps = frame_counts / elapsed_time
            print("total frames " + str(frame_counts))
            print("elapsed time " + str(elapsed_time))
            print("recorded fps " + str(recorded_fps))

            # Makes sure the threads have finished
            #while threading.active_count() > 1:
            #    time.sleep(1)


            if abs(recorded_fps - 6) >= 0.01:  # If the fps rate was higher/lower than expected, re-encode it to the expected
               # print("Re-encoding")
                filename = self.filename
                if not self.filename.endswith("avi"):
                    filename += ".avi"
                else:
                    filename = filename[0:-4]
                # cmd = f"{FFMPEG_PATH} -r {recorded_fps} -i {filename}.avi -pix_fmt yuv420p -r 6 {filename}2.avi"
                # cmd = f"{FFMPEG_PATH} -i {filename}.avi -filter:v fps={recorded_fps} {filename}2.avi"
                # subprocess.call(cmd, shell=False)
                # os.remove(f"{filename}.avi")
                # os.rename(f"{filename}2.avi", f"{filename}.avi")
            return True
        else:
            # RuntimeError("cannot close a closed recorder")
            return False

    def stop_merge(self, audio: AudioRecorder, filename: str):
        audio.stop()
        self.stop()
        new_audio = AudioSegment.from_wav(audio.filename)
        audio_dur = new_audio.duration_seconds*1000
        clip = VideoFileClip(self.filename)
        video_dur = clip.duration * 1000
        clip.close()
        if audio_dur > video_dur:
            new_audio = new_audio[audio_dur-video_dur:audio_dur]
            new_audio.export(audio.filename, format="wav")
        if not filename.endswith("mkv"):
            filename += "mkv"
        # cmd = f"{FFMPEG_PATH} -y -ac 2 -channel_layout {'mono' if audio.channels == 1 else 'stereo'} -i {self.filename} -i {self.filename[0:-4]}.avi -pix_fmt yuv420p {filename}.avi"
        cmd = f"{FFMPEG_PATH} -y -i {audio.filename}  -r 30 -i {self.filename}  -filter:a aresample=async=1 -c:a flac -c:v copy {filename}"
        subprocess.call(cmd, shell=False)
        # input_video = {FFMPEG_PATH}.input(self.filename)
        # input_audio = {FFMPEG_PATH}.input(audio.filename)
        # {FFMPEG_PATH}.concat(input_video, input_audio, v=1, a=1).output(filename).run()
        # print("Normal recording\nMuxing")
        # print("..")
        os.remove(f"{self.filename}")
        os.remove(f"{audio.filename}")


def get_available_cameras():
    l = []
    i = 0
    while True:
        if test_camera(i):
            l.append(i)
        else:
            break
        i += 1
    l = list(filter(test_camera_twice, l))
    return l


def test_camera(source):
    cap = cv2.VideoCapture(source)
    return cap is not None and cap.isOpened()


def test_camera_twice(source):
    cap = cv2.VideoCapture(source)
    if cap is not None and cap.isOpened():
        ret, video_frame = cap.read()
        if not ret:
            return False
    return True
