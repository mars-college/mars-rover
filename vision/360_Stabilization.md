# Make the 360 video stop shaking!

## Approaches

* realtime software stabilization (software)
* gimbal stabilazation (hardware)
* realtime remapping using accelerometer and gyroscope data (hybrid hardware-software)

## realtime software stabilization (software)

An approach that uses some form of realtime video tracking/camera solving and remapping/warping to achieve a stable image.

* [https://github.com/AdamSpannbauer/python_video_stab](https://github.com/AdamSpannbauer/python_video_stab)
* [https://github.com/georgmartius/vid.stab](https://github.com/georgmartius/vid.stab)
* [https://github.com/abhiTronix/vidgear](https://github.com/abhiTronix/vidgear)
	* from: [https://stackoverflow.com/questions/51970072/real-time-video-stabilization-opencv](https://stackoverflow.com/questions/51970072/real-time-video-stabilization-opencv)

### Pros

* no hardware necessary 
* free as in $0 (open-source FTW!)

### Cons

* introduces latency to video stream (processing overhead)

## gimbal stabilazation (hardware)

A mechanism that uses a gyro stabilized 3-axis motorized  system to smooth camera movement.

* [http://www.threesixtycameras.com/best-gimbals-for-360-cameras-stabilize-your-360-video/](http://www.threesixtycameras.com/best-gimbals-for-360-cameras-stabilize-your-360-video/)

### Pros

* possibly resolves gyro shakiness
* great for indoors, but why would you need one indoors anyways?

### Cons

* expensive $100+ for a decent gimbal
* may not resolve x/y/z accel shakiness
* have to find one that can hacked for control
* not suited for dusty, outdoor environments
* most are meant for hands to hold, not mounted on a rover.
* might require hacking the physical object

## realtime remapping using accelerometer and gyroscope data (hybrid hardware-software)

This is theoretical, but maybe something exists. The full software approach which basically has two components: analyze (produce motion vectors), deform-rotate (apply vectors to correct shakiness). Theoretically we should be able to replace the analysis with accelerometer and gyroscope data.

* [https://github.com/careyer/Insta360-Air-remap](https://github.com/careyer/Insta360-Air-remap)
* [https://engineering.fb.com/2016/08/31/ai-research/360-video-stabilization-a-new-algorithm-for-smoother-360-video-viewing/](https://engineering.fb.com/2016/08/31/ai-research/360-video-stabilization-a-new-algorithm-for-smoother-360-video-viewing/)
* [johanneskopf.de/publications/omnistab/360_video_stabilization.pdf]()

