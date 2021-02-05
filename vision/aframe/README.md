# Telepresence Vision

These instructions show how to install all the software for the vision demo on a [fresh install of Jetson Nano Dev Kit](https://developer.nvidia.com/embedded/learn/get-started-jetson-nano-devkit), (after having flahsed `jetson-nano-jp45-sd-card-image.zip` onto the SD card).

First, install base libraries

    sudo apt update
    sudo add-apt-repository ppa:jonathonf/ffmpeg-4
    sudo apt upgrade
    sudo apt install -y libavdevice-dev libavfilter-dev libx264-dev libopus-dev libvpx-dev pkg-config libsrtp2-dev libffi6 libffi-dev python3-pip ffmpeg
    pip3 install --upgrade pip

Most needed packages should install fine from pip. We'll install `moderngl` (to get its dependencies) but in the next section we have to reinstall it from source after some dependency changes.

	python3 -m pip install --user aiohttp aiortc av opencv-python numpy Pillow moderngl


Now uninstall moderngl, install glcontext from source (must be >=2.0, <3.0), then reinstall moderngl from source without dependencies.

    python3 -m pip uninstall moderngl
    python3 -m pip install https://github.com/moderngl/glcontext/archive/master.zip
    python3 -m pip install --no-deps -I https://github.com/moderngl/moderngl/archive/master.zip


If `av` (PyAV) is not working right, try to instead install it from source.

    export PKG_CONFIG_PATH=/usr/lib/aarch64-linux-gnu/pkgconfig
    git clone https://github.com/PyAV-Org/PyAV
    cd PyAV
    python3 -m pip install --upgrade -r tests/requirements.txt
    ./scripts/build-deps
    make

Optional: install ngrok (if you plan to use it as the server tunnel)

    wget https://bin.equinox.io/a/nmkK3DkqZEB/ngrok-2.2.8-linux-arm64.zip
    unzip ngrok-2.2.8-linux-arm64.zip
    rm ngrok-2.2.8-linux-arm64.zip

Next step, get a TLS certificate and key, e.g. `test_cert.pem` and `test_key.pem`. Then run: 

    python3 server.py --camera_id <index-of-360-camera> --cert-file <cert-file> --key-file <key-file>
    
e.g.

    python3 server.py --camera_id 0 --cert-file test_cert.pem --key-file test_key.pem 
    
The server should start runnin at https://localhost:8080.

Note: If you get errors like "libavcodec.so.58 not found", make sure `LD_LIBRARY_PATH` has the folder with the av/ffmpeg binaries. You can find it using `find ~ -name "libavcodec.so.58"`. If it's in e.g. `/home/marsrover/PyAV/vendor/build/ffmpeg-4.2/lib/`, then:

    export LD_LIBRARY_PATH=/home/marsrover/PyAV/vendor/build/ffmpeg-4.2/lib/:$LD_LIBRARY_PATH

Once it is running, in a separate terminal, you can optionally forward it using ngrok.

    ./ngrok http https://localhost:8080


