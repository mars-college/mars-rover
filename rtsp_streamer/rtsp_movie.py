#!/usr/bin/env python

# via https://stackoverflow.com/questions/59858898/how-to-convert-a-video-on-disk-to-a-rtsp-stream

# after running this, stream should be accessible over rtsp://127.0.0.1:8554/stream1

import sys
import gi

gi.require_version('Gst', '1.0')
gi.require_version('GstRtspServer', '1.0')
from gi.repository import Gst, GstRtspServer, GObject, GLib

loop = GLib.MainLoop()
Gst.init(None)

class TestRtspMediaFactory(GstRtspServer.RTSPMediaFactory):
    def __init__(self):
        GstRtspServer.RTSPMediaFactory.__init__(self)

    def do_create_element(self, url):
        #set mp4 file path to filesrc's location property
        src_demux = "filesrc location=test.mp4 ! qtdemux name=demux"
        h264_transcode = "demux.video_0"
        #uncomment following line if video transcoding is necessary
        h264_transcode = "demux.video_0 ! decodebin ! queue ! x264enc"
        pipeline = "{0} {1} ! queue ! rtph264pay name=pay0 config-interval=1 pt=96".format(src_demux, h264_transcode)
        print ("Element created: " + pipeline)
        return Gst.parse_launch(pipeline)

class GstreamerRtspServer():
    def __init__(self):
        self.rtspServer = GstRtspServer.RTSPServer()
        factory = TestRtspMediaFactory()
        factory.set_shared(True)
        mountPoints = self.rtspServer.get_mount_points()
        mountPoints.add_factory("/stream1", factory)
        self.rtspServer.attach(None)

if __name__ == '__main__':
    s = GstreamerRtspServer()
    loop.run()