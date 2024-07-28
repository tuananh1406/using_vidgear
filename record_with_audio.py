import os
import subprocess
import sys
import threading
import time
import wave
from datetime import datetime

import cv2
import pyaudio

# import time
# from datetime import datetime


def get_audio_device_info_by_name(name="1,0"):
    p = pyaudio.PyAudio()
    device_info = None
    for i in range(p.get_device_count()):
        dev = p.get_device_info_by_index(i)
        if name in dev["name"]:
            device_info = dev
    p.terminate()
    return device_info


def get_audio_device_id_and_rate(name="1,0"):
    p = pyaudio.PyAudio()
    device_id = None
    for i in range(p.get_device_count()):
        dev = p.get_device_info_by_index(i)
        if name in dev["name"]:
            device_id = i
            rate = int(dev["defaultSampleRate"])
    p.terminate()
    return device_id, rate


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
        input_device="default",
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
        self.video_filename = os.path.join("raw_videos", f"{name}.avi")
        self.audio_filename = os.path.join("raw_audios", f"{name}.wav")
        self.out_filename = os.path.join("final_videos", f"{name}.mp4")
        self.video_writer_fourcc = cv2.VideoWriter_fourcc(*self.fourcc)
        self.frame_counts = 1
        self.start_time = time.time()
        self.open = True
        self.frames_per_buffer = fpb
        self.format = pyaudio.paInt16
        # device_info = get_audio_device_info_by_name(input_device)
        # self.input_device_index = device_info["index"]
        self.rate = rate
        self.channels = channels
        # self.rate = int(device_info["defaultSampleRate"])
        # self.channels = (
        #     channels
        #     if channels <= device_info["maxInputChannels"]
        #     else device_info["maxInputChannels"]
        # )

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

    def record_by_ffmpeg(self):
        cmd = f"ffmpeg -f v4l2 -input_format {self.fourcc.lower()} -framerate {self.fps} -video_size {self.frame_size[0]}x{self.frame_size[1]} -i /dev/video{self.camindex} -c:v libx264 -vf format=yuv420p {self.video_filename}"
        self.call_cmd(cmd)

    def record_audio_stream(self):
        with wave.open(self.audio_filename, "wb") as waveFile:
            audio = pyaudio.PyAudio()
            stream = audio.open(
                format=self.format,
                channels=self.channels,
                rate=self.rate,
                input=True,
                frames_per_buffer=self.frames_per_buffer,
                # input_device_index=self.input_device_index,
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

    def start(self, time_limit=10):
        "Launches the video recording function using a thread"
        print("Recording")
        now = time.time()
        self.video_thread = threading.Thread(target=self.record_video)
        self.video_thread.start()

        "Launches the audio recording function using a thread"
        self.audio_thread = threading.Thread(target=self.record_audio_stream)
        self.audio_thread.start()
        while True:
            if time.time() - now > time_limit:
                self.stop_AVrecording()
                break

    def stop_AVrecording(self):
        self.stop()
        elapsed_time = time.time() - self.start_time
        recorded_fps = self.frame_counts / elapsed_time
        print(f"Recorded fps: {recorded_fps:.2f}")

        if os.path.exists(self.out_filename):
            os.remove(self.out_filename)

        # Makes sure the threads have finished
        while self.video_thread.is_alive() or self.audio_thread.is_alive():
            time.sleep(1)

        # Merging audio and video signal
        if (
            abs(recorded_fps - self.fps) >= 5.0
        ):  # If the fps rate was higher/lower than expected, re-encode it to the expected
            cmd = f"ffmpeg -y -r {recorded_fps} -i {self.video_filename} -input_format {self.fourcc.lower()} -pix_fmt yuv420p -r {self.fps} {self.video_filename}"
            if os.path.exists(self.video_filename):
                self.call_cmd(cmd)
            else:
                print("Video file was not found")
        cmd = f"ffmpeg -y -ac 2 -channel_layout stereo -i {self.audio_filename} -i {self.video_filename} -input_format {self.fourcc.lower()} -pix_fmt yuv420p {self.out_filename}"
        if os.path.exists(self.video_filename):
            self.call_cmd(cmd)
        else:
            print("Video file was not found")
        # self.clean()

    def call_cmd(self, cmd):
        subprocess.Popen(cmd.split())

    def clean(self):
        if os.path.exists(self.video_filename):
            os.remove(self.video_filename)
        if os.path.exists(self.audio_filename):
            os.remove(self.audio_filename)


if __name__ == "__main__":
    if not os.path.exists("raw_videos"):
        os.makedirs("raw_videos")
    if not os.path.exists("raw_audios"):
        os.makedirs("raw_audios")
    if not os.path.exists("final_videos"):
        os.makedirs("final_videos")
    machine = sys.argv[1]
    machine_map = {
        "pc-lan": [(1280, 720), 30],
        "vivobook": [(1280, 720), 15],
    }
    time_format = "%Y-%m-%d_%H-%M-%S"
    time_limit = 30
    while True:
        filename = f"{datetime.now().strftime(time_format)}"
        rec = Recorder(
            sizex=machine_map[machine][0][0],
            sizey=machine_map[machine][0][1],
            fps=machine_map[machine][1],
            name=filename,
            # camindex=2,
            # fourcc="YV12",
            # input_device="1,1",
        )
        new_thread = threading.Thread(target=rec.start, args=(time_limit,))
        new_thread.start()
        time.sleep(time_limit)
        # time.sleep(30)
        # rec.stop_AVrecording()
        print(f"Done {filename}")
