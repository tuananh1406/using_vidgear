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
        sizex=1280,
        sizey=720,
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
        self.frame_size = (
            sizex,
            sizey,
        )  # video formats and sizes also depend and vary according to the camera used
        self.video_filename = f"temp_{name}.avi"
        self.audio_filename = f"temp_{name}.wav"
        self.video_writer_fourcc = cv2.VideoWriter_fourcc(*self.fourcc)
        self.frame_counts = 1
        self.start_time = time.time()
        self.clean()
        self.out_filename = f"{name}.mp4"
        self.open = True
        self.rate = rate
        self.frames_per_buffer = fpb
        self.channels = channels
        self.format = pyaudio.paInt16

    def record_video(self):
        "Video starts being recorded"
        video_cap = cv2.VideoCapture(self.device_index)
        video_cap.set(cv2.CAP_PROP_FOURCC, self.video_writer_fourcc)
        video_cap.set(3, self.frame_size[0])
        video_cap.set(4, self.frame_size[1])
        video_out = cv2.VideoWriter(
            self.video_filename, self.video_writer_fourcc, self.fps, self.frame_size
        )
        self.start_time = time.time()

        font = cv2.FONT_HERSHEY_SIMPLEX
        # counter = 1
        prev_frame_time = 0
        while self.open:
            ret, video_frame = video_cap.read()
            new_frame_time = time.time()
            fps = 1 / (new_frame_time - prev_frame_time)
            fps = int(fps)
            fps = str(fps)
            prev_frame_time = new_frame_time
            if ret:
                cv2.putText(
                    video_frame,
                    f"{self.frame_size[0]}x{self.frame_size[1]} - {fps}",
                    (7, 70),
                    font,
                    3,
                    (100, 255, 0),
                    3,
                    cv2.LINE_AA,
                )
                video_out.write(video_frame)
                self.frame_counts += 1

                # cv2.imshow('video_frame', gray)
                # cv2.waitKey(1)
            else:
                break
        video_out.release()
        video_cap.release()
        cv2.destroyAllWindows()

    def stop(self):
        "Finishes the video recording therefore the thread too"
        if self.open:
            self.open = False

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

    def record_audio_stream(self):
        with wave.open(self.audio_filename, "wb") as waveFile:
            audio = pyaudio.PyAudio()
            stream = audio.open(
                format=self.format,
                channels=self.channels,
                rate=self.rate,
                input=True,
                frames_per_buffer=self.frames_per_buffer,
            )

            waveFile.setnchannels(self.channels)
            waveFile.setsampwidth(audio.get_sample_size(self.format))
            waveFile.setframerate(self.rate)

            # self.audio_frames = []

            while self.open:
                try:
                    waveFile.writeframes(stream.read(self.frames_per_buffer))
                except Exception as e:
                    print(f"An exception occurred: {e}")
                if not self.open:
                    break
            stream.stop_stream()
            stream.close()
            audio.terminate()

    def start(self):
        "Launches the video recording function using a thread"
        self.video_thread = threading.Thread(target=self.record_video)
        self.video_thread.start()

        "Launches the audio recording function using a thread"
        self.audio_thread = threading.Thread(target=self.record_audio_stream)
        self.audio_thread.start()

    def stop_AVrecording(self):
        self.stop()
        elapsed_time = time.time() - self.start_time
        recorded_fps = self.frame_counts / elapsed_time
        print(f"Recorded fps: {recorded_fps:.2f}")

        if os.path.exists(self.out_filename):
            os.remove(self.out_filename)

        # Makes sure the threads have finished
        while threading.active_count() > 1:
            time.sleep(1)

        # Merging audio and video signal
        if (
            abs(recorded_fps - self.fps) >= 5.0
        ):  # If the fps rate was higher/lower than expected, re-encode it to the expected
            cmd = f"ffmpeg -y -r {recorded_fps} -i {self.video_filename} -input_format mjpeg -pix_fmt yuv420p -r {self.fps} {self.video_filename}"
            self.call_cmd(cmd)
        cmd = f"ffmpeg -y -ac 2 -channel_layout stereo -i {self.audio_filename} -i {self.video_filename} -input_format mjpeg -pix_fmt yuv420p {self.out_filename}"
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
    rec = Recorder(sizex=1920, sizey=1080, fps=30, name="pc-lan")
    rec.start()
    time.sleep(30)
    rec.stop_AVrecording()
    print("Done")
