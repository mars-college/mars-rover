# Telepresence Vision

These instructions show how to install all the software for the vision demo on a [fresh install of Jetson Nano Dev Kit](https://developer.nvidia.com/embedded/learn/get-started-jetson-nano-devkit), (after having flahsed `jetson-nano-jp45-sd-card-image.zip` onto the SD card).

First, install base libraries

    sudo apt update
    sudo add-apt-repository ppa:jonathonf/ffmpeg-4
    sudo apt upgrade
    sudo apt install -y libavdevice-dev libavfilter-dev libx264-dev libopus-dev libvpx-dev pkg-config libsrtp2-dev libffi6 libffi-dev libcairo2-dev python3-pip python3-dev ffmpeg
    pip3 install --upgrade pip
    
Install gstreamer:

    pip3 install git+https://www.github.com/jackersson/gstreamer-python.git@master#egg=gstreamer-python

Most needed packages should install fine from pip. We'll install `moderngl` (to get its dependencies) but in the next section we have to reinstall it from source after some dependency changes.

	pip3 install opencv-python numpy Pillow moderngl tornado --user 

Now uninstall moderngl, install glcontext from source (must be >=2.0, <3.0), then reinstall moderngl from source without dependencies.

    python3 -m pip uninstall moderngl
    python3 -m pip install https://github.com/moderngl/glcontext/archive/master.zip
    python3 -m pip install --no-deps -I https://github.com/moderngl/moderngl/archive/master.zip

Optional: install ngrok (if you plan to use it as the server tunnel)

    wget https://bin.equinox.io/a/nmkK3DkqZEB/ngrok-2.2.8-linux-arm64.zip
    unzip ngrok-2.2.8-linux-arm64.zip
    rm ngrok-2.2.8-linux-arm64.zip

Run! 

    python3 server.py 
    
The server should start running at https://localhost:8080.

If you get a segmentation fault, you may need to add the environmental variable `OPENBLAS_CORETYPE=ARMV8`, e.g.

    OPENBLAS_CORETYPE=ARMV8 python3 server.py

Occasionally, you may have to restart the camera service.

    systemctl restart nvargus-daemon

To forward over ngrok, in a separate terminal run:

    ./ngrok http https://localhost:8080
