#!/bin/bash
if [ ! -d "./Deep-Live-Cam" ]; then
    git clone git@github.com:tuananh1406/Deep-Live-Cam.git
fi

if [ ! -f "./Deep-Live-Cam/models/GFPGANv1.4.pt" ]; then
    wget -P ./Deep-Live-Cam/models/ https://huggingface.co/hacksider/deep-live-cam/resolve/main/GFPGANv1.4.pth
fi
if [ ! -f "./Deep-Live-Cam/models/inswapper_128_fp16.onnx" ]; then
    wget -P ./Deep-Live-Cam/models/ https://huggingface.co/hacksider/deep-live-cam/resolve/main/inswapper_128_fp16.onnx
fi
