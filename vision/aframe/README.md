Vision demo
=============




Install base libraries

    sudo apt install libavdevice-dev libavfilter-dev libx264-dev libopus-dev libvpx-dev pkg-config libsrtp2-dev ffmpeg
    sudo -H pip3 install --upgrade pip
    export PKG_CONFIG_PATH=/usr/lib/aarch64-linux-gnu/pkgconfig

Now installing python packages. `PyAV` needs to be installed from source.

    git clone https://github.com/PyAV-Org/PyAV
    cd PyAV
    python3 -m pip install --upgrade -r tests/requirements.txt
    ./scripts/build-deps
    make

Most other packages should install fine from pip. We'll install `moderngl` (to get its dependencies) but in the next section we have to reinstall it from source after some dependency changes. First...

    python3 -m pip3 install --user aiohttp aiortc opencv-python numpy Pillow moderngl

Uninstall moderngl, install glcontext from source (must be >=2.0, <3.0), then reinstall moderngl from source without dependencies.

    pip3 uninstall moderngl
    pip3 install https://github.com/moderngl/glcontext/archive/master.zip
    pip3 install --no-deps -I https://github.com/moderngl/moderngl/archive/master.zip

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


