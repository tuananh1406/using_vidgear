import os
import subprocess
import threading
import time
import wave

import cv2
import pyaudio

# import time
# from datetime import datetime


class Recorder:
    def __init__(
        self,
        name="video",
        fourcc="MJPG",
        sizex=640,
        sizey=480,
        camindex=0,
        fps=7,
        rate=44100,
        fpb=1024,
        channels=2,
    ):
        self.open = True
        self.device_index = camindex
        self.fps = (
            fps  # fps should be the minimum constant rate at which the camera can
        )
        self.fourcc = fourcc  # capture images (with no decrease in speed over time; testing is required)
        self.frameSize = (
            sizex,
            sizey,
        )  # video formats and sizes also depend and vary according to the camera used
        self.video_filename = f"temp_{name}.avi"
        self.audio_filename = f"temp_{name}.wav"
        self.clean()
        self.out_filename = f"{name}.mp4"
        self.video_cap = cv2.VideoCapture(self.device_index)
        self.video_writer = cv2.VideoWriter_fourcc(*self.fourcc)
        self.video_cap.set(cv2.CAP_PROP_FOURCC, self.video_writer)
        self.video_cap.set(3, sizex)
        self.video_cap.set(4, sizey)
        self.video_out = cv2.VideoWriter(
            self.video_filename, self.video_writer, self.fps, self.frameSize
        )
        self.frame_counts = 1
        self.start_time = time.time()
        self.open = True
        self.rate = rate
        self.frames_per_buffer = fpb
        self.channels = channels
        self.format = pyaudio.paInt16
        self.audio = pyaudio.PyAudio()
        self.stream = self.audio.open(
            format=self.format,
            channels=self.channels,
            rate=self.rate,
            input=True,
            frames_per_buffer=self.frames_per_buffer,
        )
        self.audio_frames = []

    def record_video(self):
        "Video starts being recorded"
        # counter = 1
        while self.open:
            ret, video_frame = self.video_cap.read()
            if ret:
                self.video_out.write(video_frame)
                self.frame_counts += 1

                # cv2.imshow('video_frame', gray)
                # cv2.waitKey(1)
            else:
                break

    def stop(self):
        "Finishes the video recording therefore the thread too"
        if self.open:
            self.open = False

            self.video_out.release()
            self.video_cap.release()
            cv2.destroyAllWindows()

            self.stream.stop_stream()
            self.stream.close()
            self.audio.terminate()
            waveFile = wave.open(self.audio_filename, "wb")
            waveFile.setnchannels(self.channels)
            waveFile.setsampwidth(self.audio.get_sample_size(self.format))
            waveFile.setframerate(self.rate)
            waveFile.writeframes(b"".join(self.audio_frames))
            waveFile.close()

    def record_audio(self):
        "Audio starts being recorded"
        self.stream.start_stream()
        while self.open:
            try:
                self.audio_frames.append(self.stream.read(self.frames_per_buffer))
            except Exception as e:
                print(f"An exception occurred: {e}")
            if not self.open:
                break

    def start(self):
        "Launches the video recording function using a thread"
        self.video_thread = threading.Thread(target=self.record_video)
        self.video_thread.start()

        "Launches the audio recording function using a thread"
        self.audio_thread = threading.Thread(target=self.record_audio)
        self.audio_thread.start()

    def stop_AVrecording(self):
        self.stop()
        elapsed_time = time.time() - self.start_time
        recorded_fps = self.frame_counts / elapsed_time

        if os.path.exists(self.out_filename):
            os.remove(self.out_filename)

        # Makes sure the threads have finished
        while threading.active_count() > 1:
            time.sleep(1)

        # Merging audio and video signal
        if (
            abs(recorded_fps - self.fps) >= 0.01
        ):  # If the fps rate was higher/lower than expected, re-encode it to the expected
            cmd = f"ffmpeg -r {recorded_fps} -i {self.video_filename} -pix_fmt mjpg -r {self.fps} {self.video_filename}"
            self.call_cmd(cmd)
        cmd = f"ffmpeg -y -ac 2 -channel_layout stereo -i {self.audio_filename} -i {self.video_filename} -pix_fmt mjpg {self.out_filename}"
        self.call_cmd(cmd)
        self.clean()

    def call_cmd(self, cmd):
        subprocess.call(cmd, shell=True)

    def clean(self):
        if os.path.exists(self.video_filename):
            os.remove(self.video_filename)
        if os.path.exists(self.audio_filename):
            os.remove(self.audio_filename)


if __name__ == "__main__":
    rec = Recorder()
    rec.start()
    time.sleep(10)
    rec.stop_AVrecording()
    print("Done")
