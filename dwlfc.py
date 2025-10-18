from gpiozero import Button
from threading import Timer
from picamera2 import Picamera2, Preview, Metadata
from itertools import cycle
import numpy as np
import time
import cv2
import pickle
from picamera2.encoders import H264Encoder, Quality
#from picamera2.outputs import FfmpegOutput, PyavOutput
from pathlib import Path
import subprocess
import os
import getpass

username = getpass.getuser()
cam = Picamera2()

display = False
computing = False
settings = False

recording = False
blink = 0
blink_lock = False
rec_start = 0.0

vd_dur = 0.0
audioing = False
channels = 0
c1 = 0
c2 = 0
c3 = 0
c4 = 0
c5 = 0
c6 = 0
c7 = 0
c8 = 0
inf = 0
inf_data = {"0": 0}
inf_high = 0
asr = 1.5

actions = 0
shots = 0
audio_recorded = 0
video_recorded = 0

timelapse = False

# the text font used!
font = cv2.FONT_HERSHEY_SIMPLEX
font_scale = 0.325

# setting settings for photo and video,
preview_main_data = {"format": 'RGB888', "size": (320, 240)}

fps_mode = False
fps = 30

# buttons!
btn1 = Button(6)
btn2 = Button(12)
btn3 = Button(1)
btn4 = Button(5)
btn5 = Button(0)
btn6 = Button(13)
btn7 = Button(21)
btn8 = Button(26)
btn9 = Button(3)
timeout = 0.575
btn_timeout = None
btn_count = 0

# after N button presses, we evoke save()
btn_save_times = 0
btn_save = 10

# in a hurry logic variables
hurry_lock = False
hurry_timeout = 3.5
btnx = None
hurry = 0
hurry1 = 3
hurry2 = 6
hurrx = "o"

# define modes and set it to pta (phtoto, automatic) initially
modes = cycle(["pta", "ptm", "tla", "tlm", "vda", "vdm", "ado"])
# set mode to the first value of the above array!
mode = next(modes)

# showing or hiding information, 0 for none, 1 for information depth, 2 more depth etc.
info = False
info_depth = 0
disable_preview = False
disable_preview_audio = False
last_info = info
last_info_depth = info_depth
last_disable_preview_audio = disable_preview_audio

# gate to check if we need to restart the camera to update the new FPS when FPS mode is True
last_exposure = 0
fps_refresh = 0

pta_data = {
    "AeEnable": True,
    "AeExposureMode": 0,
    "AeConstraintMode": 0,
    "AeMeteringMode": 0,
    "ExposureValue": 0.0,
    "AwbEnable": True,
    "AwbMode": 0,
    "Brightness": 0.0,
    "Contrast": 1.0,
    "Sharpness": 1.0,
    "Saturation": 1.0,
    "NoiseReductionMode": 0,
    "ScalerCrop": (0, 0, 1450, 1088)
    }
pta_controls = cycle(["AeExposureMode", "AeConstraintMode", "AeMeteringMode", "ExposureValue", "Brightness", "Contrast", "Sharpness", "Saturation", "NoiseReductionMode"])
pta_control = next(pta_controls)
pta_cluster1 = pta_control
pta_cluster2 = next(pta_controls)
pta_frames = cycle([30, 60, 0.25, 0.5, 0.75, 1, 3, 5, 15, 24])
pta_fxdfps = next(pta_frames)
pta_info_controls = cycle(["fixed FPS", "font size", "button timeout", "hurry timeout", "hurry 1", "hurry 2", "save frequency"])
pta_info_data = {"FPS mode": False, "fixed FPS": pta_fxdfps, "font size": font_scale, "button timeout": timeout, "hurry timeout": hurry_timeout, "hurry 1": hurry1, "hurry 2": hurry2, "save frequency": btn_save}
pta_info_control = next(pta_info_controls)
pta_info_cluster1 = pta_info_control
pta_info_cluster2 = next(pta_info_controls)
#
ptm_data = {
    "AeEnable": False,
    "AnalogueGain": 1.0,
    "ExposureTime": 1000,
    "AwbEnable": True,
    "AwbMode": 0,
    "Contrast": 1.0,
    "Brightness": 0.0,
    "Saturation": 1.0,
    "Sharpness": 1.0,
    "NoiseReductionMode": 0,
    "ScalerCrop": (0, 0, 1450, 1088)
           }
ptm_controls = cycle(["AnalogueGain", "ExposureTime", "AwbEnable", "AwbMode", "Brightness", "Contrast", "Sharpness", "Saturation", "NoiseReductionMode"])
ptm_control = next(ptm_controls)
ptm_cluster1 = ptm_control
ptm_cluster2 = next(ptm_controls)
ptm_frames = cycle([30, 60, 0.25, 0.5, 0.75, 1, 3, 5, 15, 24])
ptm_fxdfps = next(ptm_frames)
ptm_info_controls = cycle(["FPS mode", "fixed FPS", "font size", "button timeout", "hurry timeout", "hurry 1", "hurry 2", "save frequency"])
ptm_info_data = {"FPS mode": fps_mode, "fixed FPS": pta_fxdfps, "font size": font_scale, "button timeout": timeout, "hurry timeout": hurry_timeout, "hurry 1": hurry1, "hurry 2": hurry2, "save frequency": btn_save}
ptm_info_control = next(ptm_info_controls)
ptm_info_cluster1 = ptm_info_control
ptm_info_cluster2 = next(ptm_info_controls)
#
tla_data = {
    "AeEnable": True,
    "AeExposureMode": 0,
    "AeConstraintMode": 0,
    "AeMeteringMode": 0,
    "ExposureValue": 0.0,
    "AwbEnable": True,
    "AwbMode": 0,
    "Brightness": 0.0,
    "Contrast": 1.0,
    "Sharpness": 1.0,
    "Saturation": 1.0,
    "NoiseReductionMode": 0,
    "ScalerCrop": (0, 0, 1450, 1088)
    }
tla_controls = cycle(["AeExposureMode", "AeConstraintMode", "AeMeteringMode", "ExposureValue", "Brightness", "Contrast", "Sharpness", "Saturation", "NoiseReductionMode"])
tla_control = next(tla_controls)
tla_cluster1 = tla_control
tla_cluster2 = next(tla_controls)
tla_frames = cycle([30, 60, 0.25, 0.5, 0.75, 1, 3, 5, 15, 24])
tla_fxdfps = next(tla_frames)
tla_info_controls = cycle(["interval", "shots", "battery saver", "fixed FPS", "font size", "button timeout", "hurry timeout", "hurry 1", "hurry 2", "save frequency"])
tla_info_data = {"interval": 10, "shots": 0, "battery saver": False, "FPS mode": False, "fixed FPS": pta_fxdfps, "font size": font_scale, "button timeout": timeout, "hurry timeout": hurry_timeout, "hurry 1": hurry1, "hurry 2": hurry2, "save frequency": btn_save}
tla_info_control = next(tla_info_controls)
tla_info_cluster1 = tla_info_control
tla_info_cluster2 = next(tla_info_controls)
#
tlm_data = {
    "AeEnable": False,
    "AnalogueGain": 1.0,
    "ExposureTime": 1000,
    "AwbEnable": True,
    "AwbMode": 0,
    "Contrast": 1.0,
    "Brightness": 0.0,
    "Saturation": 1.0,
    "Sharpness": 1.0,
    "NoiseReductionMode": 0,
    "ScalerCrop": (0, 0, 1450, 1088)
    }
tlm_controls = cycle(["AnalogueGain", "ExposureTime", "AwbEnable", "AwbMode", "Brightness", "Contrast", "Sharpness", "Saturation", "NoiseReductionMode"])
tlm_control = next(tlm_controls)
tlm_cluster1 = tlm_control
tlm_cluster2 = next(tlm_controls)
tlm_frames = cycle([30, 60, 0.25, 0.5, 0.75, 1, 3, 5, 15, 24])
tlm_fxdfps = next(tlm_frames)
tlm_info_controls = cycle(["interval", "shots", "battery saver", "FPS mode", "fixed FPS", "font size", "button timeout", "hurry timeout", "hurry 1", "hurry 2", "save frequency"])
tlm_info_data = {"interval": 10, "shots": 0, "battery saver": False, "FPS mode": fps_mode, "fixed FPS": pta_fxdfps, "font size": font_scale, "button timeout": timeout, "hurry timeout": hurry_timeout, "hurry 1": hurry1, "hurry 2": hurry2, "save frequency": btn_save}
tlm_info_control = next(tlm_info_controls)
tlm_info_cluster1 = tlm_info_control
tlm_info_cluster2 = next(tlm_info_controls)
#
vda_data = {
    "AeEnable": True,
    "AeExposureMode": 0,
    "AeConstraintMode": 0,
    "AeMeteringMode": 0,
    "ExposureValue": 0.0,
    "AwbEnable": True,
    "AwbMode": 0,
    "Brightness": 0.0,
    "Contrast": 1.0,
    "Sharpness": 1.0,
    "Saturation": 1.0,
    "NoiseReductionMode": 0,
    "ScalerCrop": (0, 0, 1450, 1088)
    }
vda_controls = cycle(["AeExposureMode", "AeConstraintMode", "AeMeteringMode", "ExposureValue", "Brightness", "Contrast", "Sharpness", "Saturation", "NoiseReductionMode"])
vda_control = next(vda_controls)
vda_cluster1 = vda_control
vda_cluster2 = next(vda_controls)
vda_frames = cycle([30, 60, 0.25, 0.5, 0.75, 1, 3, 5, 15, 24])
vda_fxdfps = next(vda_frames)
vda_info_controls = cycle(["fixed FPS", "audio mode", "intrinsic audio", "audio safe range", "font size", "button timeout", "hurry timeout", "hurry 1", "hurry 2", "save frequency"])
vda_audio_modes = cycle(["mono", "stereo", "5.1", "7.1", "inf.", "muted"])
vda_audio_mode = next(vda_audio_modes)
vda_info_data = {"FPS mode": False, "fixed FPS": pta_fxdfps, "audio mode": vda_audio_mode, "intrinsic audio": True, "audio safe range": asr, "font size": font_scale, "button timeout": timeout, "hurry timeout": hurry_timeout, "hurry 1": hurry1, "hurry 2": hurry2, "save frequency": btn_save}
vda_info_control = next(vda_info_controls)
vda_info_cluster1 = vda_info_control
vda_info_cluster2 = next(vda_info_controls)
#
vdm_data = {
    "AeEnable": False,
    "AnalogueGain": 1.0,
    "ExposureTime": 1000,
    "AwbEnable": True,
    "AwbMode": 0,
    "Contrast": 1.0,
    "Brightness": 0.0,
    "Saturation": 1.0,
    "Sharpness": 1.0,
    "NoiseReductionMode": 0,
    "ScalerCrop": (0, 0, 1450, 1088)
    }
vdm_controls = cycle(["AnalogueGain", "ExposureTime", "AwbEnable", "AwbMode", "Brightness", "Contrast", "Sharpness", "Saturation", "NoiseReductionMode"])
vdm_control = next(vdm_controls)
vdm_cluster1 = vdm_control
vdm_cluster2 = next(vdm_controls)
vdm_frames = cycle([30, 60, 0.25, 0.5, 0.75, 1, 3, 5, 15, 24])
vdm_fxdfps = next(vdm_frames)
vdm_info_controls = cycle(["FPS mode", "fixed FPS", "audio mode", "intrinsic audio", "audio safe range", "font size", "button timeout", "hurry timeout", "hurry 1", "hurry 2", "save frequency"])
vdm_audio_modes = cycle(["mono", "stereo", "5.1", "7.1", "inf.", "muted"])
vdm_audio_mode = next(vdm_audio_modes)
vdm_intrinsic_audio = True
vdm_info_data = {"FPS mode": fps_mode, "fixed FPS": pta_fxdfps, "audio mode": vdm_audio_mode, "intrinsic audio": True, "audio safe range": asr, "font size": font_scale, "button timeout": timeout, "hurry timeout": hurry_timeout, "hurry 1": hurry1, "hurry 2": hurry2, "save frequency": btn_save}
vdm_info_control = next(vdm_info_controls)
vdm_info_cluster1 = vdm_info_control
vdm_info_cluster2 = next(vdm_info_controls)

data = {}
info_data = pta_info_data
cluster1 = ""
cluster2 = ""

space = 0.0
pt_space = 0
vd_space = 0
ad_space = 0
def storage_info():
    global space, pt_space, vd_space, ad_space
    x = os.statvfs('/')
    o = (x.f_bavail * x.f_frsize)
    
    space = round(o / 1024 / 1024 / 1024, 2)
    
    pt_space = int(space / 0.002)
    
    if fps >= 55:
        vd_space = int(space / 0.005)
    elif fps >= 30:
        vd_space = int(space / 0.0025)
    elif fps >= 15:
        vd_space = int(space / 0.00125)
    elif fps >= 5:
        vd_space = int(space / 0.000416)
    
    ad_space = int(space / 0.0003)

def fps_config(reboot):
    global fps
    
    # maybe some logic for reseting the FPS in case frame is too big!?
    
    if info_data['FPS mode'] == True and mode in {"ptm", "tlm", "vdm"}: # need to remove vdm... if we can't get past 30 fps reliably
        frame = data['ExposureTime']
        # 1 second in microseconds 1000000
        fps = 1000000 / frame
    
    if reboot == 1:
        cam.stop()
    
    cam_config()
    time.sleep(2)
    
    if reboot == 1:
        cam.start()

def cam_config():
    global still, video, fps
    
    if info_data['FPS mode'] == False:
        if mode == "pta":
            fps = pta_info_data['fixed FPS']
        elif mode == "ptm":
            fps = ptm_info_data['fixed FPS']
        elif mode == "tla":
            fps = tla_info_data['fixed FPS']
        elif mode == "tlm":
            fps = tlm_info_data['fixed FPS']
        elif mode == "vda":
            fps = vda_info_data['fixed FPS']
        elif mode == "vdm":
            fps = vdm_info_data['fixed FPS']
        elif mode == "ado":
            fps = 30
        
    if mode in {"pta", "ptm", "tla", "tlm", "ado"}:
        #preview_still = cam.create_preview_configuration(main= preview_main_data, controls= {"FrameRate": fps})
        #still = cam.create_still_configuration(raw={})
        still = cam.create_preview_configuration(main= preview_main_data, raw={}, controls= {"FrameRate": fps})
        cam.configure(still)
        #cam.configure(preview_still)
    elif mode in {"vda", "vdm"}:
        video = cam.create_video_configuration(main= {"size": (1450, 1088), "format": "RGB888"}, lores= {"size": (320, 240), "format": "YUV420"}, controls= {"FrameRate": fps})
        #video = cam.create_video_configuration(main= {"size": (1400, 1080)}, lores= {"size": (300, 250), "format": "YUV420"}, controls= {"FrameRate": fps}, encode= "lores")
        #cam.configure(video)
        cam.configure(video)

def save():
    with open('/home/%s/Downloads/fermented.pkl' % (username), 'wb') as f:
        pickle.dump([timeout, preview_main_data, mode, modes, info, info_depth, disable_preview, disable_preview_audio, pta_data, ptm_data, tla_data, tlm_data, vda_data, vdm_data, pta_control, pta_controls, ptm_control, ptm_controls, tla_control, tla_controls, tlm_control, tlm_controls, vda_control, vda_controls, vdm_control, vdm_controls, cluster1, cluster2, pta_cluster1, pta_cluster2, ptm_cluster1, ptm_cluster2, tla_cluster1, tla_cluster2, tlm_cluster1, tlm_cluster2, vda_cluster1, vda_cluster2, vdm_cluster1, vdm_cluster2, data, fps_mode, pta_frames, pta_fxdfps, pta_info_controls, pta_info_control, pta_info_cluster1, pta_info_cluster2, ptm_frames, ptm_fxdfps, ptm_info_controls, ptm_info_control, ptm_info_cluster1, ptm_info_cluster2, tla_frames, tla_fxdfps, tla_info_controls, tla_info_control, tla_info_cluster1, tla_info_cluster2, tlm_frames, tlm_fxdfps, tlm_info_controls, tlm_info_control, tlm_info_cluster1, tlm_info_cluster2, vda_frames, vda_fxdfps, vda_info_controls, vda_info_control, vda_info_cluster1, vda_info_cluster2, vdm_frames, vdm_fxdfps, vdm_info_controls, vdm_info_control, vdm_info_cluster1, vdm_info_cluster2, pta_info_data,ptm_info_data, tla_info_data, tlm_info_data, vda_info_data, vdm_info_data, info_data, font_scale, hurry1, hurry2, hurry_timeout, btn_save, actions, shots, audio_recorded, video_recorded, vda_audio_modes, vda_audio_mode, vdm_audio_modes, vdm_audio_mode, audioing, channels, vd_dur, c1, c2, c3, c4, c5, c6, c7, c8, inf, inf_high, asr, inf_data, display, last_info, last_info_depth, last_disable_preview_audio, computing, last_exposure], f)

def load():
    with open('/home/%s/Downloads/fermented.pkl' % (username), 'rb') as f:
        global timeout, preview_main_data, mode, modes, info, info_depth, disable_preview, disable_preview_audio, pta_data, ptm_data, tla_data, tlm_data, vda_data, vdm_data, pta_control, pta_controls, ptm_control, ptm_controls, tla_control, tla_controls, tlm_control, tlm_controls, vda_control, vda_controls, vdm_control, vdm_controls, cluster1, cluster2, pta_cluster1, pta_cluster2, ptm_cluster1, ptm_cluster2, tla_cluster1, tla_cluster2, tlm_cluster1, tlm_cluster2, vda_cluster1, vda_cluster2, vdm_cluster1, vdm_cluster2, data, fps_mode, pta_frames, pta_fxdfps, pta_info_controls, pta_info_control, pta_info_cluster1, pta_info_cluster2, ptm_frames, ptm_fxdfps, ptm_info_controls, ptm_info_control, ptm_info_cluster1, ptm_info_cluster2, tla_frames, tla_fxdfps, tla_info_controls, tla_info_control, tla_info_cluster1, tla_info_cluster2, tlm_frames, tlm_fxdfps, tlm_info_controls, tlm_info_control, tlm_info_cluster1, tlm_info_cluster2, vda_frames, vda_fxdfps, vda_info_controls, vda_info_control, vda_info_cluster1, vda_info_cluster2, vdm_frames, vdm_fxdfps, vdm_info_controls, vdm_info_control, vdm_info_cluster1, vdm_info_cluster2, pta_info_data,ptm_info_data, tla_info_data, tlm_info_data, vda_info_data, vdm_info_data, info_data, font_scale, hurry1, hurry2, hurry_timeout, btn_save, actions, shots, audio_recorded, video_recorded, vda_audio_modes, vda_audio_mode, vdm_audio_modes, vdm_audio_mode, audioing, channels, vd_dur, c1, c2, c3, c4, c5, c6, c7, c8, inf, inf_high, asr, inf_data, display, last_info, last_info_depth, last_disable_preview_audio, computing, last_exposure
        timeout, preview_main_data, mode, modes, info, info_depth, disable_preview, disable_preview_audio, pta_data, ptm_data, tla_data, tlm_data, vda_data, vdm_data, pta_control, pta_controls, ptm_control, ptm_controls, tla_control, tla_controls, tlm_control, tlm_controls, vda_control, vda_controls, vdm_control, vdm_controls, cluster1, cluster2, pta_cluster1, pta_cluster2, ptm_cluster1, ptm_cluster2, tla_cluster1, tla_cluster2, tlm_cluster1, tlm_cluster2, vda_cluster1, vda_cluster2, vdm_cluster1, vdm_cluster2, data, fps_mode, pta_frames, pta_fxdfps, pta_info_controls, pta_info_control, pta_info_cluster1, pta_info_cluster2, ptm_frames, ptm_fxdfps, ptm_info_controls, ptm_info_control, ptm_info_cluster1, ptm_info_cluster2, tla_frames, tla_fxdfps, tla_info_controls, tla_info_control, tla_info_cluster1, tla_info_cluster2, tlm_frames, tlm_fxdfps, tlm_info_controls, tlm_info_control, tlm_info_cluster1, tlm_info_cluster2, vda_frames, vda_fxdfps, vda_info_controls, vda_info_control, vda_info_cluster1, vda_info_cluster2, vdm_frames, vdm_fxdfps, vdm_info_controls, vdm_info_control, vdm_info_cluster1, vdm_info_cluster2, pta_info_data,ptm_info_data, tla_info_data, tlm_info_data, vda_info_data, vdm_info_data, info_data, font_scale, hurry1, hurry2, hurry_timeout, btn_save, actions, shots, audio_recorded, video_recorded, vda_audio_modes, vda_audio_mode, vdm_audio_modes, vdm_audio_mode, audioing, channels, vd_dur, c1, c2, c3, c4, c5, c6, c7, c8, inf, inf_high, asr, inf_data, display, last_info, last_info_depth, last_disable_preview_audio, computing, last_exposure = pickle.load(f)

def init():
    global cluster1, cluster2, data, computing, info
    
    pointer = subprocess.Popen("unclutter", shell=True)
    
    file = Path('/home/%s/Downloads/records' % (username))
    if file.exists():
        pass
    else:
        os.makedirs(file)
    
    file = Path('/home/%s/Downloads/fermented.pkl' % (username))
    if file.exists():
        load()
    else:
        save()
    
    if computing == True:
        computing = False
        info = last_info
    
    fps_config(0)
    
    if mode == "pta":
        data = pta_data
        cam_config()
        cam.set_controls(pta_data)
        if info_depth == 0:
            cluster1 = pta_cluster1
            cluster2 = pta_cluster2
        elif info_depth == 1:
            cluster1 = pta_info_cluster1
            cluster2 = pta_info_cluster2
    elif mode == "ptm":
        data = ptm_data
        cam_config()
        cam.set_controls(ptm_data)
        if info_depth == 0:
            cluster1 = ptm_cluster1
            cluster2 = ptm_cluster2
        elif info_depth == 1:
            cluster1 = ptm_info_cluster1
            cluster2 = ptm_info_cluster2
    elif mode == "tla":
        data = tla_data
        cam_config()
        cam.set_controls(tla_data)
        if info_depth == 0:
            cluster1 = tla_cluster1
            cluster2 = tla_cluster2
        elif info_depth == 1:
            cluster1 = tla_info_cluster1
            cluster2 = tla_info_cluster2
    elif mode == "tlm":
        data = tlm_data
        cam_config()
        cam.set_controls(tlm_data)
        if info_depth == 0:
            cluster1 = tlm_cluster1
            cluster2 = tlm_cluster2
        elif info_depth == 1:
            cluster1 = tlm_info_cluster1
            cluster2 = tlm_info_cluster2
    elif mode == "vda":
        data = vda_data
        cam_config()
        cam.set_controls(vda_data)
        if info_depth == 0:
            cluster1 = vda_cluster1
            cluster2 = vda_cluster2
        elif info_depth == 1:
            cluster1 = vda_info_cluster1
            cluster2 = vda_info_cluster2
    elif mode == "vdm":
        data = vdm_data
        cam_config()
        cam.set_controls(vdm_data)
        if info_depth == 0:
            cluster1 = vdm_cluster1
            cluster2 = vdm_cluster2
        elif info_depth == 1:
            cluster1 = vdm_info_cluster1
            cluster2 = vdm_info_cluster2
    elif mode == "ado":
        cam_config()
        cluster1 = ""
        cluster2 = ""
    
    if disable_preview == True:
        return
    
    cam.start()
    
    # without starting camera again on manual modes, we can't set ExposureTime!
    # feels like a bug?
    if mode in {"ptm", "tlm", "vdm"}:
        cam.stop()
        cam_config()
        cam.start()
init()

def cluster_cycle(cluster):
    global cluster1, cluster2, pta_cluster1, pta_cluster2, ptm_cluster1, ptm_cluster2, tla_cluster1, tla_cluster2, tlm_cluster1, tlm_cluster2, vda_cluster1, vda_cluster2, vdm_cluster1, vdm_cluster2, pta_controls, ptm_controls, tla_controls, tlm_controls, vda_controls, vdm_controls, pta_info_controls, pta_info_control, pta_info_cluster1, pta_info_cluster2, ptm_info_controls, ptm_info_control, ptm_info_cluster1, ptm_info_cluster2, tla_info_controls, tla_info_control, tla_info_cluster1, tla_info_cluster2, tlm_info_controls, tlm_info_control, tlm_info_cluster1, tlm_info_cluster2, vda_info_controls, vda_info_control, vda_info_cluster1, vda_info_cluster2, vdm_info_controls, vdm_info_control, vdm_info_cluster1, vdm_info_cluster2
    
    if cluster == 1:
        if mode == "pta":
            if info_depth == 0:
                cluster1 = next(pta_controls)
                if cluster1 == cluster2:
                    cluster1 = next(pta_controls)
                pta_cluster1 = cluster1
            elif info_depth == 1:
                cluster1 = next(pta_info_controls)
                if cluster1 == cluster2:
                    cluster1 = next(pta_info_controls)
                pta_info_cluster1 = cluster1
        elif mode == "ptm":
            if info_depth == 0:
                cluster1 = next(ptm_controls)
                if cluster1 == cluster2:
                    cluster1 = next(ptm_controls)
                ptm_cluster1 = cluster1
            elif info_depth == 1:
                cluster1 = next(ptm_info_controls)
                if cluster1 == cluster2:
                    cluster1 = next(ptm_info_controls)
                ptm_info_cluster1 = cluster1
        elif mode == "tla":
            if info_depth == 0:
                cluster1 = next(tla_controls)
                if cluster1 == cluster2:
                    cluster1 = next(tla_controls)
                tla_cluster1 = cluster1
            elif info_depth == 1:
                cluster1 = next(tla_info_controls)
                if cluster1 == cluster2:
                    cluster1 = next(tla_info_controls)
                tla_info_cluster1 = cluster1
        elif mode == "tlm":
            if info_depth == 0:
                cluster1 = next(tlm_controls)
                if cluster1 == cluster2:
                    cluster1 = next(tlm_controls)
                tlm_cluster1 = cluster1
            elif info_depth == 1:
                cluster1 = next(tlm_info_controls)
                if cluster1 == cluster2:
                    cluster1 = next(tlm_info_controls)
                tlm_info_cluster1 = cluster1
        elif mode == "vda":
            if info_depth == 0:
                cluster1 = next(vda_controls)
                if cluster1 == cluster2:
                    cluster1 = next(vda_controls)
                vda_cluster1 = cluster1
            elif info_depth == 1:
                cluster1 = next(vda_info_controls)
                if cluster1 == cluster2:
                    cluster1 = next(vda_info_controls)
                vda_info_cluster1 = cluster1
        elif mode == "vdm":
            if info_depth == 0:
                cluster1 = next(vdm_controls)
                if cluster1 == cluster2:
                    cluster1 = next(vdm_controls)
                vdm_cluster1 = cluster1
            elif info_depth == 1:
                cluster1 = next(vdm_info_controls)
                if cluster1 == cluster2:
                    cluster1 = next(vdm_info_controls)
                vdm_info_cluster1 = cluster1
        elif mode == "ado":
            pass
        
    if cluster == 2:
        if mode == "pta":
            if info_depth == 0:
                cluster2 = next(pta_controls)
                if cluster2 == cluster1:
                    cluster2 = next(pta_controls)
                pta_cluster2 = cluster2
            elif info_depth == 1:
                cluster2 = next(pta_info_controls)
                if cluster2 == cluster1:
                    cluster2 = next(pta_info_controls)
                pta_info_cluster2 = cluster2
        elif mode == "ptm":
            if info_depth == 0:
                cluster2 = next(ptm_controls)
                if cluster2 == cluster1:
                    cluster2 = next(ptm_controls)
                ptm_cluster2 = cluster2
            elif info_depth == 1:
                cluster2 = next(ptm_info_controls)
                if cluster2 == cluster1:
                    cluster2 = next(ptm_info_controls)
                ptm_info_cluster2 = cluster2
        elif mode == "tla":
            if info_depth == 0:
                cluster2 = next(tla_controls)
                if cluster2 == cluster1:
                    cluster2 = next(tla_controls)
                tla_cluster2 = cluster2
            elif info_depth == 1:
                cluster2 = next(tla_info_controls)
                if cluster2 == cluster1:
                    cluster2 = next(tla_info_controls)
                tla_info_cluster2 = cluster2
        elif mode == "tlm":
            if info_depth == 0:
                cluster2 = next(tlm_controls)
                if cluster2 == cluster1:
                    cluster2 = next(tlm_controls)
                tlm_cluster2 = cluster2
            elif info_depth == 1:
                cluster2 = next(tlm_info_controls)
                if cluster2 == cluster1:
                    cluster2 = next(tlm_info_controls)
                tlm_info_cluster2 = cluster2
        elif mode == "vda":
            if info_depth == 0:
                cluster2 = next(vda_controls)
                if cluster2 == cluster1:
                    cluster2 = next(vda_controls)
                vda_cluster2 = cluster2
            elif info_depth == 1:
                cluster2 = next(vda_info_controls)
                if cluster2 == cluster1:
                    cluster2 = next(vda_info_controls)
                vda_info_cluster2 = cluster2
        elif mode == "vdm":
            if info_depth == 0:
                cluster2 = next(vdm_controls)
                if cluster2 == cluster1:
                    cluster2 = next(vdm_controls)
                vdm_cluster2 = cluster2
            elif info_depth == 1:
                cluster2 = next(vdm_info_controls)
                if cluster2 == cluster1:
                    cluster2 = next(vdm_info_controls)
                vdm_info_cluster2 = cluster2
        elif mode == "ado":
            pass

def clusterment(cluster, click, ment, btn):
# we either increment or decrement values here!
# cluster is from each cluster, click to check if it's hold/single/double/+, ment checks if it's a decrement or increment action
    global pta_data, ptm_data, tla_data, tlm_data, vda_data, vdm_data, data, fps_mode, fps, pta_frames, pta_fxdfps, ptm_frames, ptm_fxdfps, tla_frames, tla_fxdfps, tlm_frames, tlm_fxdfps, vda_frames, vda_fxdfps, vdm_frames, vdm_fxdfps, pta_info_data,ptm_info_data, tla_info_data, tlm_info_data, vda_info_data, vdm_info_data, info_data, font_scale, timeout, btnx, hurry, hurry_lock, hurry1, hurry2, hurry_start, hurry_timeout, btn_save, vda_audio_modes, vda_audio_mode, vdm_audio_modes, vdm_audio_mode, channels, inf, inf_high, asr, hurrx, last_exposure
    
    # "inf." should invert values...
    if audioing == True and cluster == 1:
        if ment == "+" :
            if click == 0:
                if mode == "vda" and vda_audio_mode == "inf.":
                    inf = inf_high
                    channels = inf + 10
                    return
                elif mode == "vdm" and vdm_audio_mode == "inf.":
                    inf = inf_high
                    channels = inf - 10
                    return
                else:
                    channels = 0
                    return
            elif click == 1:
                z = 1
            elif click == 2:
                z = 2
            elif click == 3:
                z = 3
            if mode == "vda" and vda_audio_mode == "inf.":
                z = z * -1
            elif mode == "vdm" and vdm_audio_mode == "inf.":
                z = z * -1
            
            # note we are subtracting as we interpret channels from downwards...
            # with the exception of "inf." mode!
            channels = channels - z
            inf = channels - 10
            
            if channels <= 0:
                channels = 0
            return
        
        elif ment == "-":
            if click == 0:
                channels = 9
                z = 0
            elif click == 1:
                z = 1
            elif click == 2:
                z = 2
            elif click == 3:
                z = 3
            
            if mode == "vda" and vda_audio_mode == "inf.":
                z = z * -1
            elif mode == "vdm" and vdm_audio_mode == "inf.":
                z = z * -1
            
            channels = channels + z
            
            if mode == "vda":
                if vda_audio_mode == "stereo":
                    if channels >= 2:
                        channels = 2
                elif vda_audio_mode == "5.1":
                    if channels >= 6:
                        channels = 6
                elif vda_audio_mode == "7.1":
                    if channels >= 8:
                        channels = 8
            elif mode == "vdm":
                if vdm_audio_mode == "stereo":
                    if channels >= 2:
                        channels = 2
                elif vdm_audio_mode == "5.1":
                    if channels >= 6:
                        channels = 6
                elif vdm_audio_mode == "7.1":
                    if channels >= 8:
                        channels = 8
            
            if mode == "vda":
                if vda_audio_mode == "inf.":
                    if channels <= 9:
                        channels = 9
            elif mode == "vdm":
                if vdm_audio_mode == "inf.":
                    if channels <= 9:
                        channels = 9
            
            inf = channels - 10
            return
    
    if cluster == 1:
        cluster = cluster1
    elif cluster == 2:
        cluster = cluster2
    
    # in a hurry logic
    # where we check for multiple, same button presses to activate a multiplication of + or - on value
    if hurry_lock == True:
        if hurrx == ment:
            hurry_end = time.time()
            hurry_lenght = hurry_end - hurry_start
            if hurry_lenght < hurry_timeout:
                if btnx == btn:
                    hurry += 1
                    hurry_start = time.time()
            else:
                hurry = 0
                hurry_lock = False
    else:
        hurry = 0
        btnx = btn
        hurry_lock = True
        hurrx = ment
        hurry_start = time.time()
    
    if info_depth == 0:
        
        if mode == "pta":
            data = pta_data
        elif mode == "ptm":
            data = ptm_data
        elif mode == "tla":
            data = tla_data
        elif mode == "tlm":
            data = tlm_data
        elif mode == "vda":
            data = vda_data
        elif mode == "vdm":
            data = vdm_data
            
        if cluster == "AnalogueGain":
            # maybe we can have a logic of "if user repeats too much click 2 or 3, value increases drastically"
            if ment == "o":
                value = 1 - data[cluster]
            elif click == 0:
                value = 0.1
            elif click == 1:
                value = 0.5
            elif click == 2:
                value = 5
            elif click == 3:
                value = 25
                
        elif cluster == "ExposureTime":
            # for the global shutter, min.: 29 and max.: 15534385
            if click == 0:
                if ment == "o":
                    value = 1000 - data[cluster]
                elif ment == "+":
                    value = data[cluster] // 4
                elif ment == "-":
                    value = data[cluster] // 6
                    ment = "skip"
            elif click == 1:
                if ment == "+":
                    value = data[cluster] // 2
                elif ment == "-":
                    value = data[cluster] // 4
            elif click == 2:
                if ment == "+":
                    value = data[cluster]
                elif ment == "-":
                    value = data[cluster] // 2
            elif click == 3:
                if ment == "+":
                    value = data[cluster] * 2
                elif ment == "-":
                    value = data[cluster] // 3
                    
        elif cluster == "AwbEnable":
            value = 1
            
        elif cluster == "AwbMode":
            if ment == "o":
                value = 0 - data[cluster]
            elif click == 1:
                value = 1
            elif click == 2:
                value = 2
            elif click == 3:
                value = 3
                
        elif cluster == "AeExposureMode":
            if ment == "o":
                value = 0 - data[cluster]
            elif click == 1:
                value = 1
            elif click == 2:
                value = 2
            elif click == 3:
                value = 3
            
        elif cluster == "AeConstraintMode":
            if ment == "o":
                value = 0 - data[cluster]
            elif click == 1:
                value = 1
            elif click == 2:
                value = 2
            elif click == 3:
                value = 3
            
        elif cluster == "AeMeteringMode":
            if ment == "o":
                value = 0 - data[cluster]
            elif click == 1:
                value = 1
            elif click == 2:
                value = 2
            elif click == 3:
                value = 3
            
        elif cluster == "ExposureValue":
            if ment == "o":
                value = 0 - data[cluster]
            elif click == 0:
                value = 0.25
            elif click == 1:
                value = 0.5
            elif click == 2:
                value = 2.5
            elif click == 3:
                value = 5
            
        elif cluster == "Brightness":
            if ment == "o":
                value = 0 - data[cluster]
            elif click == 0:
                value = 0.05
            elif click == 1:
                value = 0.1
            elif click == 2:
                value = 0.25
            elif click == 3:
                value = 0.5
            
        elif cluster == "Contrast":
            if ment == "o":
                value = 1 - data[cluster]
            elif click == 0:
                value = 0.125
            elif click == 1:
                value = 0.25
            elif click == 2:
                value = 0.5
            elif click == 3:
                value = 1
            
        elif cluster == "Sharpness":
            if ment == "o":
                value = 1 - data[cluster]
            elif click == 0:
                value = 0.1
            elif click == 1:
                value = 0.25
            elif click == 2:
                value = 0.5
            elif click == 3:
                value = 1
            
        elif cluster == "Saturation":
            if ment == "o":
                value = 1 - data[cluster]
            elif click == 0:
                value = 0.125
            elif click == 1:
                value = 0.25
            elif click == 2:
                value = 0.5
            elif click == 3:
                value = 1
            
        elif cluster == "NoiseReductionMode":
            if ment == "o":
                value = 0 - data[cluster]
            elif click == 1:
                value = 1
            elif click == 2:
                value = 2
            elif click == 3:
                value = 3
        
        if hurry >= hurry2:
            value = value * 4
        elif hurry >= hurry1:
            value = value * 2
        
        # are we summing or not?
        if ment == "-":
            value = value * -1
        
        # compute!
        result = data[cluster] + value
        
        # there are limits!
        minimum, maximum, default = cam.camera_controls[cluster]
        if result >= maximum:
            result = maximum
        elif result <= minimum:
            result = minimum
        # sets the control + value
        cam.set_controls({cluster: result})

        if mode in {"ptm", "tlm", "vdm"} and cluster == 'ExposureTime':
            last_exposure = data['ExposureTime']

        # we need to update the data into the presistent variables...
        data[cluster] = result
        if mode == "pta":
            pta_data = data
        elif mode == "ptm":
            ptm_data = data
        elif mode == "tla":
            tla_data = data
        elif mode == "tlm":
            tlm_data = data
        elif mode == "vda":
            vda_data = data
        elif mode == "vdm":
            vdm_data = data
        
    elif info_depth == 1:
        
        if mode == "pta":
            fxdfps = pta_frames
            info_data = pta_info_data
        elif mode == "ptm":
            fxdfps = ptm_frames
            info_data = ptm_info_data
        elif mode == "tla":
            fxdfps = tla_frames
            info_data = tla_info_data
        elif mode == "tlm":
            fxdfps = tlm_frames
            info_data = tlm_info_data
        elif mode == "vda":
            fxdfps = vda_frames
            info_data = vda_info_data
            audio_mode = vda_audio_mode
            audio_modes = vda_audio_modes
        elif mode == "vdm":
            fxdfps = vdm_frames
            info_data = vdm_info_data
            audio_mode = vdm_audio_mode
            audio_modes = vdm_audio_modes
        
        # different from controls at info_depth == 0
        # here we need to set each variable beyond the dictionary update
        # as we don't have a set_controls()...
        if cluster == "FPS mode":
        # note that we only have the + button doing its function!
        # the - button is reserved to trigger fps_config() if
        # the mode is activated!
            if mode in {"ptm", "tlm", "vdm"}:
                if click == 1:
                    if ment == "+":
                        if info_data[cluster] == True:
                            fps_mode = False
                            info_data[cluster] = False
                        else:
                            fps_mode = True
                            info_data[cluster] = True
                    fps_config(1)
                    
        elif cluster == "fixed FPS":
            if click == 1:
                fps_mode = False
                info_data['FPS mode'] = False
                if ment == "+":
                    fps = next(fxdfps)
                    info_data['fixed FPS'] = fps
                elif ment == "-":
                    for i in range(8):
                        # we cycle 8 times as the previous value is 10 positions "ahead"
                        next(fxdfps)
                    # the 9° time
                    fps = next(fxdfps)
                    info_data['fixed FPS'] = fps
                fps_config(1)
                
        elif cluster == "font size":
            if click == 0:
                font_scale = 0.325
            elif click == 1:
                if ment == "+":
                    font_scale = font_scale + 0.005
                elif ment == "-":
                    font_scale = font_scale - 0.005
            elif click == 2:
                if ment == "+":
                    font_scale = font_scale + 0.025
                elif ment == "-":
                    font_scale = font_scale - 0.025
            elif click == 3:
                if ment == "+":
                    font_scale = font_scale + 0.05
                elif ment == "-":
                    font_scale = font_scale - 0.05
            info_data['font size'] = font_scale
        
        elif cluster == "button timeout":
            if click == 0:
                timeout = 0.575
            elif click == 1:
                if ment == "+":
                    timeout = timeout + 0.05
                elif ment == "-":
                    timeout = timeout - 0.05
            elif click == 2:
                if ment == "+":
                    timeout = timeout + 0.1
                elif ment == "-":
                    timeout = timeout - 0.1
            elif click == 3:
                if ment == "+":
                    timeout = timeout + 0.25
                elif ment == "-":
                    timeout = timeout - 0.25
            info_data['button timeout'] = timeout
        
        elif cluster == "hurry timeout":
            if click == 0:
                value = 3.5 - hurry_timeout
            elif click == 1:
                value = 0.5
            elif click == 2:
                value = 1
            elif click == 3:
                value = 1.5
            if ment == "-":
                value * -1
            hurry_timeout = hurry_timeout + value
            info_data[cluster] = hurry_timeout + value
        
        elif cluster == "hurry 1":
            if click == 0:
                hurry1 = 3
            elif click == 1:
                if ment == "+":
                    hurry1 = hurry1 + 1
                elif ment == "-":
                    hurry1 = hurry1 - 1
            elif click == 2:
                if ment == "+":
                    hurry1 = hurry1 + 2
                elif ment == "-":
                    hurry1 = hurry1 - 2
            elif click == 3:
                if ment == "+":
                    hurry1 = hurry1 + 3
                elif ment == "-":
                    hurry1 = hurry1 - 3
            if hurry1 <= 0:
                    hurry1 = 0
            if hurry1 >= hurry2:
                hurry1 = hurry2 - 1
            info_data['hurry 1'] = hurry1
        
        elif cluster == "hurry 2":
            if click == 0:
                hurry2 = 6
            elif click == 1:
                if ment == "+":
                    hurry2 = hurry2 + 1
                elif ment == "-":
                    hurry2 = hurry2 - 1
            elif click == 2:
                if ment == "+":
                    hurry2 = hurry2 + 2
                elif ment == "-":
                    hurry2 = hurry2 - 2
            elif click == 3:
                if ment == "+":
                    hurry2 = hurry2 + 3
                elif ment == "-":
                    hurry2 = hurry2 - 3
            if hurry2 <= hurry1:
                hurry2 = hurry1 + 1
            info_data['hurry 2'] = hurry2
        
        elif cluster == "save frequency":
            if click == 0:
                btn_save = 10
            elif click == 1:
                if ment == "+":
                    btn_save = btn_save + 1
                elif ment == "-":
                    btn_save = btn_save - 1
            elif click == 2:
                if ment == "+":
                    btn_save = btn_save + 2
                elif ment == "-":
                    btn_save = btn_save - 2
            elif click == 3:
                if ment == "+":
                    btn_save = btn_save + 3
                elif ment == "-":
                    btn_save = btn_save - 3
                if btn_save <= 0:
                    btn_save = 0
            info_data['save frequency'] = btn_save
        
        elif cluster == "audio mode":
        #vda_audio_modes, vda_audio_mode, vdm_audio_modes, vdm_audio_mode
            if click == 0:
                if ment == "+":
                    for i in range(6):
                        if audio_mode == "inf.":
                            break
                        audio_mode = next(audio_modes)
                elif ment == "-":
                    for i in range(6):
                        if audio_mode == "muted":
                            break
                        audio_mode = next(audio_modes)
            elif click == 1:
                if ment == "+":
                    audio_mode = next(audio_modes)
                elif ment == "-":
                    for i in range(5):
                        audio_mode = next(audio_modes)
            elif click == 2:
                if ment == "+":
                    for i in range(6):
                        if audio_mode == "stereo":
                            break
                        audio_mode = next(audio_modes)
                elif ment == "-":
                    for i in range(6):
                        if audio_mode == "mono":
                            break
                        audio_mode = next(audio_modes)
            elif click == 3:
                if ment == "+":
                    for i in range(6):
                        if audio_mode == "7.1":
                            break
                        audio_mode = next(audio_modes)
                elif ment == "-":
                    for i in range(6):
                        if audio_mode == "5.1":
                            break
                        audio_mode = next(audio_modes)
            info_data['audio mode'] = audio_mode
        
        elif cluster == "intrinsic audio":
            if ment == "+":
                info_data['intrinsic audio'] = True
            elif ment == "-":
                info_data['intrinsic audio'] = False
        
        elif cluster == "audio safe range":
            if click == 0:
                asr = 1.5
            elif click == 1:
                if ment == "+":
                    asr += 0.05
                elif ment == "-":
                    asr -= 0.05
            elif click == 2:
                if ment == "+":
                    asr += 0.1
                elif ment == "-":
                    asr -= 0.1
            elif click == 3:
                if ment == "+":
                    asr += 0.5
                elif ment == "-":
                    asr -= 0.5
            info_data['audio safe range'] = asr
        
        elif cluster == "interval":
            if click == 0:
                info_data['interval'] = 10
                x = 0
            elif click == 1:
                x = 1
            elif click == 2:
                x = 5
            elif click == 3:
                x = 10
            if hurry >= hurry2:
                x = x * 4
            elif hurry >= hurry1:
                x = x * 2
            if ment == "-":
                info_data['interval'] = info_data['interval'] - x
            elif ment == "+":
                info_data['interval'] = info_data['interval'] + x
            if info_data['interval'] <= 0:
                info_data['interval'] = 1
        
        elif cluster == "shots":
            if click == 0:
                x = 0
                info_data['shots'] = 0
            elif click == 1:
                x = 5
            elif click == 2:
                x = 10
            elif click == 3:
                x = 25
            if hurry >= hurry2:
                x = x * 4
            elif hurry >= hurry1:
                x = x * 2
            if ment == "-":
                info_data['shots'] = info_data['shots'] - x
            elif ment == "+":
                info_data['shots'] = info_data['shots'] + x
            if info_data['shots'] <= 0:
                info_data['shots'] = 0
        
        elif cluster == "battery saver":
            if ment == "+":
                info_data['battery saver'] = True
            else:
                info_data['battery saver'] = False
        
        if mode == "pta":
            pta_fxdfps = fps
            info_data = pta_info_data
        elif mode == "ptm":
            ptm_fxdfps = fps
            info_data = ptm_info_data
        elif mode == "tla":
            tla_fxdfps = fps
            info_data = tla_info_data
        elif mode == "tlm":
            tlm_fxdfps = fps
            info_data = tlm_info_data
        elif mode == "vda":
            vda_fxdfps = fps
            info_data = vda_info_data
            vda_audio_mode = audio_mode
            vda_audio_modes = audio_modes
        elif mode == "vdm":
            vdm_fxdfps = fps
            info_data = vdm_info_data
            vdm_audio_mode = audio_mode
            vdm_audio_modes = audio_modes

def zoom(x):
# from: https://github.com/raspberrypi/picamera2/blob/main/examples/zoom.py
    if x == 0:
        # resets the zoom!
        cam.controls.ScalerCrop = (0, 0, 1450, 1088)
    else:
        size = cam.capture_metadata()['ScalerCrop'][2:]
        full_res = cam.camera_properties['PixelArraySize']
        size = [int(s * x) for s in size]
        offset = [(r - s) // 2 for r, s in zip(full_res, size)]
        cam.set_controls({"ScalerCrop": offset + size})

def lapsing():
    global shots, recording
    z = 0
    if info_data['shots'] == 0:
        while True:
            if info_data['battery saver'] == True:
                cam.start()
            if timelapse == False:
                save()
                break
            z += 1
            buffer, metadata = cam.switch_mode_and_capture_buffers(still, ["raw"])
            cam.helpers.save_dng(buffer[0], metadata, still["raw"], "/home/%s/Downloads/records/%s-%s.dng" % (username, actions, z))
            shots += 1
            if info_data['battery saver'] == True:
                cam.stop()
            time.sleep(info_data['interval'])
            
    else:
        for i in range(info_data['shots']):
            if timelapse == False:
                save()
                break
            z += 1
            buffer, metadata = cam.switch_mode_and_capture_buffers(still, ["raw"])
            cam.helpers.save_dng(buffer[0], metadata, still["raw"], "/home/%s/Downloads/records/%s-%s.dng" % (username, actions, z))
            shots += 1
            time.sleep(info_data['interval'])
        save()
        recording = False

def handle_btn_click(btn):
    global btn_timeout, btn_count, mode, modes, info, info_depth, disable_preview, disable_preview_audio, cluster1, cluster2, data, fps_mode, info_data, hurry_lock, btn_save_times, recording, actions, shots, audio_recorded, video_recorded, rec_start, last_info_depth, last_info, last_disable_preview_audio, audioing, channels, vd_dur, c1, c2, c3, c4, c5, c6, c7, c8, inf, inf_high, inf_data, timelapse, display, computing, settings, last_exposure
    # OLD LOGIC WAS USING THESE AS GLOBAL VARIABLES (will just let them commented here in case i missed something)
    # pta_data, ptm_data, tla_data, tlm_data, vda_data, vdm_data, pta_control, pta_controls, ptm_control, ptm_controls, tla_control, tla_controls, tlm_control, tlm_controls, vda_control, vda_controls, vdm_control, vdm_controls
    btn_timeout = None
    
    btn_save_times += 1
    
    # for re-arranging buttons if you don't care to follow
    # the <exact> diagram... at least i didn't
    #if btn in {btn1, btn2, btn3, btn4, btn5, btn6, btn7, btn8, btn9}:
     #   print(btn)
      #  return
    
    if computing == True:
        return
    
    if btn in {btn2, btn3, btn4, btn5, btn6, btn7, btn8, btn9} and disable_preview == True:
        btn_count = 0
        return
    
    if btn in {btn2, btn3, btn5, btn7, btn8, btn9} and audioing == True:
        btn_count = 0
        return
    
    if btn in {btn3, btn4, btn5, btn6, btn7, btn8, btn9} and timelapse == True:
        btn_count = 0
        return
    
    # we stop in a hurry logic on non-clusterment buttons
    if btn in {btn1, btn2, btn3, btn5, btn8}:
        hurry_lock = False
    
    # button long click
    if btn.is_pressed:
        if btn == btn1:
        # btn1 long click disables/enables the preview!
            if audioing == True or timelapse == True:
                btn_count = 0
                return
            if disable_preview == False:
                disable_preview = True
                time.sleep(0.5)
                cam.stop()
            else:
                disable_preview = False
                cam.start()
        if btn == btn2:
        # btn2 long click resets the zoom!
            zoom(0)
        if btn == btn3:
        # btn3 long click disables/enables information
            if audioing == True:
                return
            if info == True:
                info = False
                last_info = info
            else:
                info = True
                last_info = info
        
        # cluster1 long click
        if btn == btn4:
            clusterment(1, 0, "+", 4)
        if btn == btn5:
            clusterment(1, 0, "o", 5)
        if btn == btn6:
            clusterment(1, 0, "-", 6)
        
        # cluster2 long click
        if btn == btn7:
            clusterment(2, 0, "+", 7)
        if btn == btn8:
            if settings == False:
                clusterment(2, 0, "o", 8)
            # this is the button we shutdown the Pi!
            elif settings == True:
                computing = True
                save()
                zzz = subprocess.Popen("sudo shutdown -h now", shell=True)
        if btn == btn9:
            clusterment(2, 0, "-", 9)
    
    # button single click
    elif btn_count == 0:
        if btn == btn1:
            
            if timelapse == True:
                if info_data["battery saver"] == True:
                            disable_preview = False
                timelapse = False
                recording = False
                lapsing()
                btn_count = 0
                save()
                return
            
            if disable_preview == False:
                
                if mode in {"pta", "ptm"}:
                    actions += 1
                    shots += 1
                    buffer, metadata = cam.switch_mode_and_capture_buffers(still, ["raw"])
                    cam.helpers.save_dng(buffer[0], metadata, still["raw"], "/home/%s/Downloads/records/%s.dng" % (username, actions))
                    save()
                    
                elif mode in {"tla", "tlm"}:
                    if timelapse == False:
                        if info_data["battery saver"] == True:
                            disable_preview = True
                        timelapse = True
                        recording = True
                        actions += 1
                        save()
                        lapsing()
                
                elif mode in {"vda", "vdm"}:
                    
                    if recording == False:
                        
                        if audioing == True:
                            if channels <= 0 or channels == 9:
                                audioing = False
                                c1 = 0
                                c2 = 0
                                c3 = 0
                                c4 = 0
                                c5 = 0
                                c6 = 0
                                c7 = 0
                                c8 = 0
                                inf = 0
                                inf_high = 0
                                inf_data = {"0": 0}
                                save()
                                return
                            if mode == "vda":
                                if vda_audio_mode == "stereo":
                                    if channels == 2:
                                        x = ["arecord -D plughw:1 -r 48000 -f S32_LE /home/%s/Downloads/records/%s-l.wav" % (username, actions)]
                                        z = subprocess.Popen(x, shell=True)
                                    elif channels == 1:
                                        x = ["arecord -D plughw:1 -r 48000 -f S32_LE /home/%s/Downloads/records/%s-r.wav" % (username, actions)]
                                        z = subprocess.Popen(x, shell=True)
                                elif vda_audio_mode == "5.1":
                                    if channels == 6:
                                        x = ["arecord -D plughw:1 -r 48000 -f S32_LE /home/%s/Downloads/records/%s-sw.wav" % (username, actions)]
                                        z = subprocess.Popen(x, shell=True)
                                    elif channels == 5:
                                        x = ["arecord -D plughw:1 -r 48000 -f S32_LE /home/%s/Downloads/records/%s-ct.wav" % (username, actions)]
                                        z = subprocess.Popen(x, shell=True)
                                    elif channels == 4:
                                        x = ["arecord -D plughw:1 -r 48000 -f S32_LE /home/%s/Downloads/records/%s-fl.wav" % (username, actions)]
                                        z = subprocess.Popen(x, shell=True)
                                    elif channels == 3:
                                        x = ["arecord -D plughw:1 -r 48000 -f S32_LE /home/%s/Downloads/records/%s-fr.wav" % (username, actions)]
                                        z = subprocess.Popen(x, shell=True)
                                    elif channels == 2:
                                        x = ["arecord -D plughw:1 -r 48000 -f S32_LE /home/%s/Downloads/records/%s-rl.wav" % (username, actions)]
                                        z = subprocess.Popen(x, shell=True)
                                    elif channels == 1:
                                        x = ["arecord -D plughw:1 -r 48000 -f S32_LE /home/%s/Downloads/records/%s-rr.wav" % (username, actions)]
                                        z = subprocess.Popen(x, shell=True)
                                elif vda_audio_mode == "7.1":
                                    if channels == 8:
                                        x = ["arecord -D plughw:1 -r 48000 -f S32_LE /home/%s/Downloads/records/%s-sw.wav" % (username, actions)]
                                        z = subprocess.Popen(x, shell=True)
                                    elif channels == 7:
                                        x = ["arecord -D plughw:1 -r 48000 -f S32_LE /home/%s/Downloads/records/%s-ct.wav" % (username, actions)]
                                        z = subprocess.Popen(x, shell=True)
                                    elif channels == 6:
                                        x = ["arecord -D plughw:1 -r 48000 -f S32_LE /home/%s/Downloads/records/%s-fl.wav" % (username, actions)]
                                        z = subprocess.Popen(x, shell=True)
                                    elif channels == 5:
                                        x = ["arecord -D plughw:1 -r 48000 -f S32_LE /home/%s/Downloads/records/%s-fr.wav" % (username, actions)]
                                        z = subprocess.Popen(x, shell=True)
                                    elif channels == 4:
                                        x = ["arecord -D plughw:1 -r 48000 -f S32_LE /home/%s/Downloads/records/%s-sl.wav" % (username, actions)]
                                        z = subprocess.Popen(x, shell=True)
                                    elif channels == 3:
                                        x = ["arecord -D plughw:1 -r 48000 -f S32_LE /home/%s/Downloads/records/%s-sr.wav" % (username, actions)]
                                        z = subprocess.Popen(x, shell=True)
                                    elif channels == 2:
                                        x = ["arecord -D plughw:1 -r 48000 -f S32_LE /home/%s/Downloads/records/%s-rl.wav" % (username, actions)]
                                        z = subprocess.Popen(x, shell=True)
                                    elif channels == 1:
                                        x = ["arecord -D plughw:1 -r 48000 -f S32_LE /home/%s/Downloads/records/%s-rr.wav" % (username, actions)]
                                        z = subprocess.Popen(x, shell=True)
                                elif vda_audio_mode == "inf.":
                                    # since for the logic of inf. we set channels to 10 (which we can't go lower)
                                    # we subtract - 9 for the number of the record!
                                    x = ["arecord -D plughw:1 -r 48000 -f S32_LE /home/%s/Downloads/records/%s-%s.wav" % (username, actions, inf+1)]
                                    z = subprocess.Popen(x, shell=True)
                            elif mode == "vdm":
                                if vdm_audio_mode == "stereo":
                                    if channels == 2:
                                        x = ["arecord -D plughw:1 -r 48000 -f S32_LE /home/%s/Downloads/records/%s-l.wav" % (username, actions)]
                                        z = subprocess.Popen(x, shell=True)
                                    elif channels == 1:
                                        x = ["arecord -D plughw:1 -r 48000 -f S32_LE /home/%s/Downloads/records/%s-r.wav" % (username, actions)]
                                        z = subprocess.Popen(x, shell=True)
                                elif vdm_audio_mode == "5.1":
                                    if channels == 6:
                                        x = ["arecord -D plughw:1 -r 48000 -f S32_LE /home/%s/Downloads/records/%s-sw.wav" % (username, actions)]
                                        z = subprocess.Popen(x, shell=True)
                                    elif channels == 5:
                                        x = ["arecord -D plughw:1 -r 48000 -f S32_LE /home/%s/Downloads/records/%s-ct.wav" % (username, actions)]
                                        z = subprocess.Popen(x, shell=True)
                                    elif channels == 4:
                                        x = ["arecord -D plughw:1 -r 48000 -f S32_LE /home/%s/Downloads/records/%s-fl.wav" % (username, actions)]
                                        z = subprocess.Popen(x, shell=True)
                                    elif channels == 3:
                                        x = ["arecord -D plughw:1 -r 48000 -f S32_LE /home/%s/Downloads/records/%s-fr.wav" % (username, actions)]
                                        z = subprocess.Popen(x, shell=True)
                                    elif channels == 2:
                                        x = ["arecord -D plughw:1 -r 48000 -f S32_LE /home/%s/Downloads/records/%s-rl.wav" % (username, actions)]
                                        z = subprocess.Popen(x, shell=True)
                                    elif channels == 1:
                                        x = ["arecord -D plughw:1 -r 48000 -f S32_LE /home/%s/Downloads/records/%s-rr.wav" % (username, actions)]
                                        z = subprocess.Popen(x, shell=True)
                                elif vdm_audio_mode == "7.1":
                                    if channels == 8:
                                        x = ["arecord -D plughw:1 -r 48000 -f S32_LE /home/%s/Downloads/records/%s-sw.wav" % (username, actions)]
                                        z = subprocess.Popen(x, shell=True)
                                    elif channels == 7:
                                        x = ["arecord -D plughw:1 -r 48000 -f S32_LE /home/%s/Downloads/records/%s-ct.wav" % (username, actions)]
                                        z = subprocess.Popen(x, shell=True)
                                    elif channels == 6:
                                        x = ["arecord -D plughw:1 -r 48000 -f S32_LE /home/%s/Downloads/records/%s-fl.wav" % (username, actions)]
                                        z = subprocess.Popen(x, shell=True)
                                    elif channels == 5:
                                        x = ["arecord -D plughw:1 -r 48000 -f S32_LE /home/%s/Downloads/records/%s-fr.wav" % (username, actions)]
                                        z = subprocess.Popen(x, shell=True)
                                    elif channels == 4:
                                        x = ["arecord -D plughw:1 -r 48000 -f S32_LE /home/%s/Downloads/records/%s-sl.wav" % (username, actions)]
                                        z = subprocess.Popen(x, shell=True)
                                    elif channels == 3:
                                        x = ["arecord -D plughw:1 -r 48000 -f S32_LE /home/%s/Downloads/records/%s-sr.wav" % (username, actions)]
                                        z = subprocess.Popen(x, shell=True)
                                    elif channels == 2:
                                        x = ["arecord -D plughw:1 -r 48000 -f S32_LE /home/%s/Downloads/records/%s-rl.wav" % (username, actions)]
                                        z = subprocess.Popen(x, shell=True)
                                    elif channels == 1:
                                        x = ["arecord -D plughw:1 -r 48000 -f S32_LE /home/%s/Downloads/records/%s-rr.wav" % (username, actions)]
                                        z = subprocess.Popen(x, shell=True)
                                elif vdm_audio_mode == "inf.":
                                    x = ["arecord -D plughw:1 -r 48000 -f S32_LE /home/%s/Downloads/records/%s-%s.wav" % (username, actions, inf+1)]
                                    z = subprocess.Popen(x, shell=True)
                            recording = True
                            rec_start = time.time()
                            return
                        
                        recording = True
                        actions += 1
                        
                        if mode == "vda" and vda_info_data['intrinsic audio'] == True:
                            if vda_audio_mode != "muted":
                                x = ["arecord -D plughw:1 -r 48000 -f S32_LE /home/%s/Downloads/records/%s.wav" % (username, actions)]
                                z = subprocess.Popen(x, shell=True)
                        elif mode == "vdm" and vdm_info_data['intrinsic audio'] == True:
                            if vdm_audio_mode != "muted":
                                x = ["arecord -D plughw:1 -r 48000 -f S32_LE /home/%s/Downloads/records/%s.wav" % (username, actions)]
                                z = subprocess.Popen(x, shell=True)
                        
                        encoder = H264Encoder()
                        # we need to set this otherwise a 60 FPS videos is 2x slower, a 15 FPS, 2x faster and so on
                        # doesn't seem to solve anything
                        #encoder.frame_skip_count = 30 / fps
                        
                        cam.start_recording(encoder, "/home/%s/Downloads/records/%s.h264" % (username, actions), quality=Quality.VERY_HIGH)
                        rec_start = time.time()
                        
                    elif recording == True:
                        recording = False
                        
                        if audioing == True:
                            x = ["killall", "arecord"]
                            z = subprocess.Popen(x, shell=False)
                            rec_end = time.time()
                            x = rec_end - rec_start
                            if x >= vd_dur:
                                if channels == 8: c8 = 2
                                elif channels == 7: c7 = 2
                                elif channels == 6: c6 = 2
                                elif channels == 5: c5 = 2
                                elif channels == 4: c4 = 2
                                elif channels == 3: c3 = 2
                                elif channels == 2: c2 = 2
                                elif channels == 1: c1 = 2
                                elif channels >= 10:
                                    inf_data[str(channels - 10)] = 2
                            else:
                                if channels == 8: c8 = 1
                                elif channels == 7: c7 = 1
                                elif channels == 6: c6 = 1
                                elif channels == 5: c5 = 1
                                elif channels == 4: c4 = 1
                                elif channels == 3: c3 = 1
                                elif channels == 2: c2 = 1
                                elif channels == 1: c1 = 1
                                elif channels >= 10:
                                    inf_data[str(channels - 10)] = 1
                            if channels <= 8:
                                channels -= 1
                            elif channels >= 10:
                                channels += 1
                                inf = channels - 10
                                y = inf_data.get(str(inf))
                                if y == None:
                                    inf_data[str(inf)] = 0
                                if inf_high == inf:
                                    inf_high += 1
                                elif inf_high < inf:
                                    inf_high = inf
                            
                            save()
                            return
                        
                        cam.stop_recording()
                        
                        x = ["killall", "arecord"]
                        z = subprocess.Popen(x, shell=False)
                        
                        rec_end = time.time()
                        vd_dur = rec_end - rec_start
                        video_recorded += vd_dur
                        
                        # audio_safe_range
                        vd_dur += asr
                        
                        cam.start()
                        
                        if mode == "vda" and vda_audio_mode in {"stereo", "5.1", "7.1", "inf."}:
                            audioing = True
                            if vda_audio_mode == "stereo":
                                channels = 2
                            elif vda_audio_mode == "5.1":
                                channels = 6
                            elif vda_audio_mode == "7.1":
                                channels = 8
                            elif vda_audio_mode == "inf.":
                                channels = 10
                        elif mode == "vdm" and vdm_audio_mode in {"stereo", "5.1", "7.1", "inf."}:
                            audioing = True
                            if vdm_audio_mode == "stereo":
                                channels = 2
                            elif vdm_audio_mode == "5.1":
                                channels = 6
                            elif vdm_audio_mode == "7.1":
                                channels = 8
                            elif vdm_audio_mode == "inf.":
                                channels = 10
                        
                        save()
                        
                elif mode == "ado":
                    if recording == False:
                        recording = True
                        actions += 1
                        x = ["arecord -D plughw:1 -r 48000 -f S32_LE /home/%s/Downloads/records/%s.wav" % (username, actions)]
                        z = subprocess.Popen(x, shell=True)
                        rec_start = time.time()
                    else:
                        recording = False
                        x = ["killall arecord"]
                        z = subprocess.Popen(x, shell=True)
                        rec_end = time.time()
                        value = rec_end - rec_start
                        audio_recorded += value
                        save()
                
        elif btn == btn2:
        # we zoom! (by a factor of 0.5)
            zoom(0.5)
        elif btn == btn3:
        # btn3 single click cycles between modes and change previews and configurations according
            
            if recording == True or disable_preview == True or audioing == True:
                return
            
            cam.stop()
            mode = next(modes)
            
            if mode == "pta":
                cam.set_controls(pta_data)
                data = pta_data
                info_data = pta_info_data
                cam_config()
                if info_depth == 0:
                    cluster1 = pta_cluster1
                    cluster2 = pta_cluster2
                elif info_depth == 1:
                    cluster1 = pta_info_cluster1
                    cluster2 = pta_info_cluster2
            elif mode == "ptm":
                cam.set_controls(ptm_data)
                data = ptm_data
                info_data = ptm_info_data
                last_exposure = data['ExposureTime']
                cam_config()
                if info_depth == 0:
                    cluster1 = ptm_cluster1
                    cluster2 = ptm_cluster2
                elif info_depth == 1:
                    cluster1 = ptm_info_cluster1
                    cluster2 = ptm_info_cluster2
            elif mode == "tla":
                cam.set_controls(tla_data)
                data = tla_data
                info_data = tla_info_data
                cam_config()
                if info_depth == 0:
                    cluster1 = tla_cluster1
                    cluster2 = tla_cluster2
                elif info_depth == 1:
                    cluster1 = tla_info_cluster1
                    cluster2 = tla_info_cluster2
            elif mode == "tlm":
                cam.set_controls(tlm_data)
                data = tlm_data
                info_data = tlm_info_data
                last_exposure = data['ExposureTime']
                cam_config()
                if info_depth == 0:
                    cluster1 = tlm_cluster1
                    cluster2 = tlm_cluster2
                elif info_depth == 1:
                    cluster1 = tlm_info_cluster1
                    cluster2 = tlm_info_cluster2
            elif mode == "vda":
                cam.set_controls(vda_data)
                data = vda_data
                info_data = vda_info_data
                cam_config()
                if info_depth == 0:
                    cluster1 = vda_cluster1
                    cluster2 = vda_cluster2
                elif info_depth == 1:
                    cluster1 = vda_info_cluster1
                    cluster2 = vda_info_cluster2
            elif mode == "vdm":
                cam.set_controls(vdm_data)
                data = vdm_data
                info_data = vdm_info_data
                last_exposure = data['ExposureTime']
                cam_config()
                if info_depth == 0:
                    cluster1 = vdm_cluster1
                    cluster2 = vdm_cluster2
                elif info_depth == 1:
                    cluster1 = vdm_info_cluster1
                    cluster2 = vdm_info_cluster2
            elif mode == "ado":
                disable_preview_audio = True
                last_disable_preview_audio = disable_preview_audio
                cam_config()
            if mode != "ado":
                disable_preview_audio = False
                last_disable_preview_audio = disable_preview_audio
            
            cam.start()
            
            # i was somehow getting a bug where i couldn't change ExposureTime or AnalogGain
            # and to fix that i had to re-start the camera again when changing to a manual mode
            # it seems to work without it now, who knows why
            # sometimes we also don't have automatic modes doing their automatic thing!
            cam.stop()
            cam_config()
            cam.start()
            
            # we reset the zoom as stuff gets messed when we reach video mode with lores preview...
            #cam.controls.ScalerCrop = (0, 0, 1450, 1088)
        
        # cluster1 single click
        elif btn == btn4:
            clusterment(1, 1, "+", 4)
        elif btn == btn5:
            cluster_cycle(1)
        elif btn == btn6:
            clusterment(1, 1, "-", 6)
        
        # cluster2 single click
        elif btn == btn7:
            clusterment(2, 1, "+", 7)
        elif btn == btn8:
            cluster_cycle(2)
        elif btn == btn9:
            clusterment(2, 1, "-", 9)
    
    # button double click
    elif btn_count == 1:
        
        if btn == btn1:
            if audioing == True or timelapse == True:
                btn_count = 0
                return
            elif disable_preview == False:
                pass
        
        elif btn == btn2:
        # a super zoom *-*
            zoom(0.25)
        
        elif btn == btn3:
        # btn3 double click cycle between the depth levels of information!
        
            if disable_preview == True:
                return
        
            if info == True:
                info_depth += 1
                if info_depth >= 2:
                    info_depth = 0
                last_info_depth = info_depth
            if mode == "pta":
                if info_depth == 0:
                    cluster1 = pta_cluster1
                    cluster2 = pta_cluster2
                elif info_depth == 1:
                    cluster1 = pta_info_cluster1
                    cluster2 = pta_info_cluster2
            elif mode == "ptm":
                if info_depth == 0:
                    cluster1 = ptm_cluster1
                    cluster2 = ptm_cluster2
                elif info_depth == 1:
                    cluster1 = ptm_info_cluster1
                    cluster2 = ptm_info_cluster2
            elif mode == "tla":
                if info_depth == 0:
                    cluster1 = tla_cluster1
                    cluster2 = tla_cluster2
                elif info_depth == 1:
                    cluster1 = tla_info_cluster1
                    cluster2 = tla_info_cluster2
            elif mode == "tlm":
                if info_depth == 0:
                    cluster1 = tlm_cluster1
                    cluster2 = tlm_cluster2
                elif info_depth == 1:
                    cluster1 = tlm_info_cluster1
                    cluster2 = tlm_info_cluster2
            elif mode == "vda":
                if info_depth == 0:
                    cluster1 = vda_cluster1
                    cluster2 = vda_cluster2
                elif info_depth == 1:
                    cluster1 = vda_info_cluster1
                    cluster2 = vda_info_cluster2
            elif mode == "vdm":
                if info_depth == 0:
                    cluster1 = vdm_cluster1
                    cluster2 = vdm_cluster2
                elif info_depth == 1:
                    cluster1 = vdm_info_cluster1
                    cluster2 = vdm_info_cluster2
                
        #cluster1 double-click
        elif btn == btn4:
            clusterment(1, 2, "+", 4)
        elif btn == btn5:
            pass
        elif btn == btn6:
            clusterment(1, 2, "-", 6)
        
        # cluster2 double-click
        elif btn == btn7:
            clusterment(2, 2, "+", 7)
        elif btn == btn8:
            # we switch between HDMI and TFT!
            if settings == True:
                if display == False:
                    display = True
                    computing = True
                    save()
                    zzz = subprocess.Popen("sudo /home/%s/Downloads/lcd.sh" % (username), shell=True)
                else:
                    display = False
                    computing = True
                    save()
                    zzz = subprocess.Popen("sudo /home/%s/Downloads/hdmi.sh" % (username), shell=True)
        elif btn == btn9:
            clusterment(2, 2, "-", 9)
    
    # button + click
    else:
        if btn == btn1:
            if audioing == True or timelapse == True:
                btn_count = 0
                return
            #if disable_preview == False:
            save()
        elif btn == btn2:
            pass
        elif btn == btn3:
            if recording == True or audioing == True:
                return
            
            if settings == False:
                if disable_preview == True:
                    cam.start()
                storage_info()
                settings = True
                info = False
            else:
                settings = False
                info = last_info
                info_depth = last_info_depth
                disable_preview_audio = last_disable_preview_audio
                if disable_preview == True:
                    cam.stop()
                
        
        # cluster1 + click
        elif btn == btn4:
            clusterment(1, 3, "+", 4)
        elif btn == btn5:
            pass
        elif btn == btn6:
            clusterment(1, 3, "-", 6)
        
        # cluster2 + click
        elif btn == btn7:
            clusterment(2, 3, "+", 7)
        elif btn == btn8:
            pass
        elif btn == btn9:
            clusterment(2, 3, "-", 9)
    
    if btn_save_times >= btn_save:
        btn_save_times = 0
        save()
    
    # we need to reset this variable for the button click logic...
    btn_count = 0

def handle_btn(btn):
    global btn_timeout, btn_count
    if btn_timeout:
        btn_count += 1
    else:
        btn_timeout = Timer(timeout, handle_btn_click, [btn])
        btn_timeout.start()

# assign buttons to handle_btn function
for x in [btn1, btn2, btn3, btn4, btn5, btn6, btn7, btn8, btn9]:
    x.when_pressed = handle_btn

# looping!
while True:

    if disable_preview or disable_preview_audio or audioing == True or settings == True:
        frame = cv2.imread("/home/%s/Downloads/black.png" % (username))
    elif mode in {"vda", "vdm"}:
        frame = cam.capture_array("lores")
        frame = cv2.cvtColor(frame, cv2.COLOR_YUV420p2RGB)
        #frame = frame[:240, :320] # an example of how we crop stuff from the frame... we would need this if we weren't transforming YUV to RGB
    else:
        frame = cam.capture_array()
    
    # draws a black background when "disabling" the camera preview
    #if disable_preview or disable_preview_audio == True:
    #    cv2.rectangle(frame, (0, 0), (320, 240), (0, 0, 0), -1)
    
    if info_data['FPS mode'] == True and data['ExposureTime'] != last_exposure:
        fps_refresh += 1
        if fps_refresh >= 350:
            fps_refresh = 0
            last_exposure = data['ExposureTime']
            fps_config(1)
            print("foos")
    
    # information!
    if info == True and disable_preview == False:
        if audioing == False:
            # we render it twice for letters with a black border!
            # which mode
            if info_depth <= 1:
                cv2.putText(frame, mode, (5, 13), font, font_scale, (0,0,0), 2, cv2.LINE_AA)
                cv2.putText(frame, mode, (5, 13), font, font_scale, (255,255,255), 0, cv2.LINE_AA)
            if info_depth == 0:
                if mode != "ado":
                    # cluster1
                    cv2.putText(frame, cluster1 + " : " + str(data.get(cluster1)), (5, 215), font, font_scale, (0,0,0), 2, cv2.LINE_AA)
                    cv2.putText(frame, cluster1 + " : " + str(data.get(cluster1)), (5, 215), font, font_scale, (255,255,255), 0, cv2.LINE_AA)
                    # cluster2
                    cv2.putText(frame, cluster2 + " : " + str(data.get(cluster2)), (5, 233), font, font_scale, (0,0,0), 2, cv2.LINE_AA)
                    cv2.putText(frame, cluster2 + " : " + str(data.get(cluster2)), (5, 233), font, font_scale, (255,255,255), 0, cv2.LINE_AA)
                    #f"{data[cluster2]:.3f}"
            elif info_depth == 1:
                if mode != "ado":
                    # cluster1
                    cv2.putText(frame, cluster1 + " : " + str(info_data.get(cluster1)), (5, 215), font, font_scale, (0,0,0), 2, cv2.LINE_AA)
                    cv2.putText(frame, cluster1 + " : " + str(info_data.get(cluster1)), (5, 215), font, font_scale, (255,255,255), 0, cv2.LINE_AA)
                    # cluster2
                    cv2.putText(frame, cluster2 + " : " + str(info_data.get(cluster2)), (5, 233), font, font_scale, (0,0,0), 2, cv2.LINE_AA)
                    cv2.putText(frame, cluster2 + " : " + str(info_data.get(cluster2)), (5, 233), font, font_scale, (255,255,255), 0, cv2.LINE_AA)
    
    if settings == True:
        cv2.putText(frame, str(space) + " GB available", (5, 13), font, font_scale, (0,0,0), 2, cv2.LINE_AA)
        cv2.putText(frame, str(space) + " GB available", (5, 13), font, font_scale, (255,255,255), 0, cv2.LINE_AA)
        cv2.putText(frame, "~ " + str(pt_space) + " shots", (5, 31), font, font_scale, (0,0,0), 2, cv2.LINE_AA)
        cv2.putText(frame, "~ " + str(pt_space) + " shots", (5, 31), font, font_scale, (255,255,255), 0, cv2.LINE_AA)
        cv2.putText(frame, "~ " + str(vd_space) + " seconds of video", (5, 49), font, font_scale, (0,0,0), 2, cv2.LINE_AA)
        cv2.putText(frame, "~ " + str(vd_space) + " seconds of video", (5, 49), font, font_scale, (255,255,255), 0, cv2.LINE_AA)
        cv2.putText(frame, "~ " + str(ad_space) + " seconds of audio", (5, 67), font, font_scale, (0,0,0), 2, cv2.LINE_AA)
        cv2.putText(frame, "~ " + str(ad_space) + " seconds of audio", (5, 67), font, font_scale, (255,255,255), 0, cv2.LINE_AA)
        
        cv2.putText(frame, str(shots) + " shots", (5, 197), font, font_scale, (0,0,0), 2, cv2.LINE_AA)
        cv2.putText(frame, str(shots) + " shots", (5, 197), font, font_scale, (255,255,255), 0, cv2.LINE_AA)
        cv2.putText(frame, str(int(video_recorded)) + " seconds of video", (5, 215), font, font_scale, (0,0,0), 2, cv2.LINE_AA)
        cv2.putText(frame, str(int(video_recorded)) + " seconds of video", (5, 215), font, font_scale, (255,255,255), 0, cv2.LINE_AA)
        cv2.putText(frame, str(int(audio_recorded)) + " seconds of audio", (5, 233), font, font_scale, (0,0,0), 2, cv2.LINE_AA)
        cv2.putText(frame, str(int(audio_recorded)) + " seconds of audio", (5, 233), font, font_scale, (255,255,255), 0, cv2.LINE_AA)
    
    if recording == True or computing == True or audioing == True:
        
        #rec_end = time.time()
        #counting = int(rec_end - rec_start)
        #cv2.putText(frame, str(counting), (5, 31), font, font_scale, (0,0,0), 2, cv2.LINE_AA)
        #cv2.putText(frame, str(counting), (5, 31), font, font_scale, (255,255,255), 0, cv2.LINE_AA)
        
        if recording == True or computing == True:
        
            if blink_lock == False:
                # add a slower green circle if we match the lenght of last record and audioing == True
                if audioing == True:
                    rec_end = time.time()
                    x = rec_end - rec_start
                    if x >= vd_dur:
                        cv2.circle(frame, center=(305,15), radius=7, color=(0,255,0), thickness=-1)
                    else:
                        cv2.circle(frame, center=(305,15), radius=7, color=(0,0,255), thickness=-1)
                elif recording == True:
                    cv2.circle(frame, center=(305,15), radius=7, color=(0,0,255), thickness=-1)
                elif computing == True:
                    cv2.circle(frame, center=(305,15), radius=7, color=(255,0,0), thickness=-1)
                blink += 1
                if blink >= 30 and audioing == False:
                    blink_lock = True
                elif blink >= 90 and audioing == True:
                    blink_lock = True
            else:
                blink -= 1
                if blink <= 0:
                    blink_lock = False
    
    if audioing == True:
        if mode == "vda":
            z = vda_audio_mode
        elif mode == "vdm":
            z = vdm_audio_mode
            
        if z == "stereo":
            cv2.putText(frame, "right", (260, 120), font, font_scale, (255,255,255), 2, cv2.LINE_AA)
            cv2.putText(frame, "left", (60, 120), font, font_scale, (255,255,255), 2, cv2.LINE_AA)
            if c1 == 2:
                cv2.putText(frame, "right", (260, 120), font, font_scale, (0,255,0), 0, cv2.LINE_AA)
            elif c1 == 1:
                cv2.putText(frame, "right", (260, 120), font, font_scale, (0,255,255), 0, cv2.LINE_AA)
            elif c1 == 0:
                cv2.putText(frame, "right", (260, 120), font, font_scale, (0,0,255), 0, cv2.LINE_AA)
            if c2 == 2:
                cv2.putText(frame, "left", (60, 120), font, font_scale, (0,255,0), 0, cv2.LINE_AA)
            elif c2 == 1:
                cv2.putText(frame, "left", (60, 120), font, font_scale, (0,255,255), 0, cv2.LINE_AA)
            elif c2 == 0:
                cv2.putText(frame, "left", (60, 120), font, font_scale, (0,0,255), 0, cv2.LINE_AA)
            if channels == 1:
                cv2.putText(frame, "right", (260, 120), font, font_scale, (0,0,0), 0, cv2.LINE_AA)
            elif channels == 2:
                cv2.putText(frame, "left", (60, 120), font, font_scale, (0,0,0), 0, cv2.LINE_AA)
        
        elif z == "5.1":
            cv2.putText(frame, "sw", (60, 80), font, font_scale, (255,255,255), 2, cv2.LINE_AA)
            cv2.putText(frame, "ct", (260, 80), font, font_scale, (255,255,255), 2, cv2.LINE_AA)
            cv2.putText(frame, "fl", (60, 120), font, font_scale, (255,255,255), 2, cv2.LINE_AA)
            cv2.putText(frame, "fr", (260, 120), font, font_scale, (255,255,255), 2, cv2.LINE_AA)
            cv2.putText(frame, "rl", (60, 160), font, font_scale, (255,255,255), 2, cv2.LINE_AA)
            cv2.putText(frame, "rr", (260, 160), font, font_scale, (255,255,255), 2, cv2.LINE_AA)
            if c6 == 2:
                cv2.putText(frame, "sw", (60, 80), font, font_scale, (0,255,0), 0, cv2.LINE_AA)
            elif c6 == 1:
                cv2.putText(frame, "sw", (60, 80), font, font_scale, (0,255,255), 0, cv2.LINE_AA)
            elif c6 == 0:
                cv2.putText(frame, "sw", (60, 80), font, font_scale, (0,0,255), 0, cv2.LINE_AA)
            if c5 == 2:
                cv2.putText(frame, "ct", (260, 80), font, font_scale, (0,255,0), 0, cv2.LINE_AA)
            elif c5 == 1:
                cv2.putText(frame, "ct", (260, 80), font, font_scale, (0,255,255), 0, cv2.LINE_AA)
            elif c5 == 0:
                cv2.putText(frame, "ct", (260, 80), font, font_scale, (0,0,255), 0, cv2.LINE_AA)
            if c4 == 2:
                cv2.putText(frame, "fl", (60, 120), font, font_scale, (0,255,0), 0, cv2.LINE_AA)
            elif c4 == 1:
                cv2.putText(frame, "fl", (60, 120), font, font_scale, (0,255,255), 0, cv2.LINE_AA)
            elif c4 == 0:
                cv2.putText(frame, "fl", (60, 120), font, font_scale, (0,0,255), 0, cv2.LINE_AA)
            if c3 == 2:
                cv2.putText(frame, "fr", (260, 120), font, font_scale, (0,255,0), 0, cv2.LINE_AA)
            elif c3 == 1:
                cv2.putText(frame, "fr", (260, 120), font, font_scale, (0,255,255), 0, cv2.LINE_AA)
            elif c3 == 0:
                cv2.putText(frame, "fr", (260, 120), font, font_scale, (0,0,255), 0, cv2.LINE_AA)
            if c2 == 2:
                cv2.putText(frame, "rl", (60, 160), font, font_scale, (0,255,0), 0, cv2.LINE_AA)
            elif c2 == 1:
                cv2.putText(frame, "rl", (60, 160), font, font_scale, (0,255,255), 0, cv2.LINE_AA)
            elif c2 == 0:
                cv2.putText(frame, "rl", (60, 160), font, font_scale, (0,0,255), 0, cv2.LINE_AA)
            if c1 == 2:
                cv2.putText(frame, "rr", (260, 160), font, font_scale, (0,255,0), 0, cv2.LINE_AA)
            elif c1 == 1:
                cv2.putText(frame, "rr", (260, 160), font, font_scale, (0,255,255), 0, cv2.LINE_AA)
            elif c1 == 0:
                cv2.putText(frame, "rr", (260, 160), font, font_scale, (0,0,255), 0, cv2.LINE_AA)
            if channels == 6:
                cv2.putText(frame, "sw", (60, 80), font, font_scale, (0,0,0), 0, cv2.LINE_AA)
            elif channels == 5:
                cv2.putText(frame, "ct", (260, 80), font, font_scale, (0,0,0), 0, cv2.LINE_AA)
            elif channels == 4:
                cv2.putText(frame, "fl", (60, 120), font, font_scale, (0,0,0), 0, cv2.LINE_AA)
            elif channels == 3:
                cv2.putText(frame, "fr", (260, 120), font, font_scale, (0,0,0), 0, cv2.LINE_AA)
            elif channels == 2:
                cv2.putText(frame, "rl", (60, 160), font, font_scale, (0,0,0), 0, cv2.LINE_AA)
            elif channels == 1:
                cv2.putText(frame, "rr", (260, 160), font, font_scale, (0,0,0), 0, cv2.LINE_AA)
                
        elif z == "7.1":
            cv2.putText(frame, "sw", (60, 65), font, font_scale, (255,255,255), 2, cv2.LINE_AA)
            cv2.putText(frame, "ct", (260, 65), font, font_scale, (255,255,255), 2, cv2.LINE_AA)
            cv2.putText(frame, "fl", (60, 105), font, font_scale, (255,255,255), 2, cv2.LINE_AA)
            cv2.putText(frame, "fr", (260, 105), font, font_scale, (255,255,255), 2, cv2.LINE_AA)
            cv2.putText(frame, "sl", (60, 145), font, font_scale, (255,255,255), 2, cv2.LINE_AA)
            cv2.putText(frame, "sr", (260, 145), font, font_scale, (255,255,255), 2, cv2.LINE_AA)
            cv2.putText(frame, "rl", (60, 185), font, font_scale, (255,255,255), 2, cv2.LINE_AA)
            cv2.putText(frame, "rr", (260, 185), font, font_scale, (255,255,255), 2, cv2.LINE_AA)
            if c8 == 2:
                cv2.putText(frame, "sw", (60, 65), font, font_scale, (0,255,0), 0, cv2.LINE_AA)
            elif c8 == 1:
                cv2.putText(frame, "sw", (60, 65), font, font_scale, (0,255,255), 0, cv2.LINE_AA)
            elif c8 == 0:
                cv2.putText(frame, "sw", (60, 65), font, font_scale, (0,0,255), 0, cv2.LINE_AA)
            if c7 == 2:
                cv2.putText(frame, "ct", (260, 65), font, font_scale, (0,255,0), 0, cv2.LINE_AA)
            elif c7 == 1:
                cv2.putText(frame, "ct", (260, 65), font, font_scale, (0,255,255), 0, cv2.LINE_AA)
            elif c7 == 0:
                cv2.putText(frame, "ct", (260, 65), font, font_scale, (0,0,255), 0, cv2.LINE_AA)
            if c6 == 2:
                cv2.putText(frame, "fl", (60, 105), font, font_scale, (0,255,0), 0, cv2.LINE_AA)
            elif c6 == 1:
                cv2.putText(frame, "fl", (60, 105), font, font_scale, (0,255,255), 0, cv2.LINE_AA)
            elif c6 == 0:
                cv2.putText(frame, "fl", (60, 105), font, font_scale, (0,0,255), 0, cv2.LINE_AA)
            if c5 == 2:
                cv2.putText(frame, "fr", (260, 105), font, font_scale, (0,255,0), 0, cv2.LINE_AA)
            elif c5 == 1:
                cv2.putText(frame, "fr", (260, 105), font, font_scale, (0,255,255), 0, cv2.LINE_AA)
            elif c5 == 0:
                cv2.putText(frame, "fr", (260, 105), font, font_scale, (0,0,255), 0, cv2.LINE_AA)
            if c4 == 2:
                cv2.putText(frame, "sl", (60, 145), font, font_scale, (0,255,0), 0, cv2.LINE_AA)
            elif c4 == 1:
                cv2.putText(frame, "sl", (60, 145), font, font_scale, (0,255,255), 0, cv2.LINE_AA)
            elif c4 == 0:
                cv2.putText(frame, "sl", (60, 145), font, font_scale, (0,0,255), 0, cv2.LINE_AA)
            if c3 == 2:
                cv2.putText(frame, "sr", (260, 145), font, font_scale, (0,255,0), 0, cv2.LINE_AA)
            elif c3 == 1:
                cv2.putText(frame, "sr", (260, 145), font, font_scale, (0,255,255), 0, cv2.LINE_AA)
            elif c3 == 0:
                cv2.putText(frame, "sr", (260, 145), font, font_scale, (0,0,255), 0, cv2.LINE_AA)
            if c2 == 2:
                cv2.putText(frame, "rl", (60, 185), font, font_scale, (0,255,0), 0, cv2.LINE_AA)
            elif c2 == 1:
                cv2.putText(frame, "rl", (60, 185), font, font_scale, (0,255,255), 0, cv2.LINE_AA)
            elif c2 == 0:
                cv2.putText(frame, "rl", (60, 185), font, font_scale, (0,0,255), 0, cv2.LINE_AA)
            if c1 == 2:
                cv2.putText(frame, "rr", (260, 185), font, font_scale, (0,255,0), 0, cv2.LINE_AA)
            elif c1 == 1:
                cv2.putText(frame, "rr", (260, 185), font, font_scale, (0,255,255), 0, cv2.LINE_AA)
            elif c1 == 0:
                cv2.putText(frame, "rr", (260, 185), font, font_scale, (0,0,255), 0, cv2.LINE_AA)
            if channels == 8:
                cv2.putText(frame, "sw", (60, 65), font, font_scale, (0,0,0), 0, cv2.LINE_AA)
            elif channels == 7:
                cv2.putText(frame, "ct", (260, 65), font, font_scale, (0,0,0), 0, cv2.LINE_AA)    
            elif channels == 6:
                cv2.putText(frame, "fl", (60, 105), font, font_scale, (0,0,0), 0, cv2.LINE_AA)
            elif channels == 5:
                cv2.putText(frame, "fr", (260, 105), font, font_scale, (0,0,0), 0, cv2.LINE_AA)
            elif channels == 4:
                cv2.putText(frame, "sl", (60, 145), font, font_scale, (0,0,0), 0, cv2.LINE_AA)
            elif channels == 3:
                cv2.putText(frame, "sr", (260, 145), font, font_scale, (0,0,0), 0, cv2.LINE_AA)
            elif channels == 2:
                cv2.putText(frame, "rl", (60, 185), font, font_scale, (0,0,0), 0, cv2.LINE_AA)
            elif channels == 1:
                cv2.putText(frame, "rr", (260, 185), font, font_scale, (0,0,0), 0, cv2.LINE_AA)
                
        # it feels the experience of inf. clusterment keys should be re-thought!
        # sure it behaves differently than the rest but... inversed hold buttons for
        elif z == "inf.":
            if inf == -1:
                cv2.putText(frame, "exit", (160, 120), font, font_scale, (255,255,255), 2, cv2.LINE_AA)
                cv2.putText(frame, "exit", (160, 120), font, font_scale, (0,0,0), 0, cv2.LINE_AA)
            else:
                y = inf_data.get(str(inf))
                if y == None:
                    cv2.putText(frame, str(inf + 1), (160, 120), font, font_scale, (255,255,255), 2, cv2.LINE_AA)
                    cv2.putText(frame, str(inf + 1), (160, 120), font, font_scale, (0,0,0), 0, cv2.LINE_AA)
                elif inf_data[str(inf)] == 0:
                    cv2.putText(frame, str(inf + 1), (160, 120), font, font_scale, (255,255,255), 2, cv2.LINE_AA)
                    cv2.putText(frame, str(inf + 1), (160, 120), font, font_scale, (0,0,0), 0, cv2.LINE_AA)
                elif inf_data[str(inf)] == 1:
                    cv2.putText(frame, str(inf + 1), (160, 120), font, font_scale, (255,255,255), 2, cv2.LINE_AA)
                    cv2.putText(frame, str(inf + 1), (160, 120), font, font_scale, (0,255,255), 0, cv2.LINE_AA)
                elif inf_data[str(inf)] == 2:
                    cv2.putText(frame, str(inf + 1), (160, 120), font, font_scale, (255,255,255), 2, cv2.LINE_AA)
                    cv2.putText(frame, str(inf + 1), (160, 120), font, font_scale, (0,255,0), 0, cv2.LINE_AA)
            
    
    # from: https://forums.raspberrypi.com/viewtopic.php?t=369522
    cv2.imshow('dwlfc', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
