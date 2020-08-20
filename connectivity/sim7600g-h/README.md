# Setup the Waveshare SIM7600G for Jetson Nano

A few other developers on the NVIDIA forum were seeking instructions for setting up the SIM7600G-H Hat for their Jetson Nano based projects.

The guide and related files that were original put together for this project has been split out into its own repo where it will be maintained separately:

[https://github.com/phillipdavidstearns/simcom_wwan-setup](https://github.com/phillipdavidstearns/simcom_wwan-setup)

## Modifications

If using [Wireguard VPN](https://github.com/brahman-ai/mars-rover/blob/master/connectivity/wireguard/README.md) as setup in the guides for this project, it will be necessary to modify the `simcom_wwan@.service` file to include:


```
[Install]
WantedBy=multi-user.target, wg-quick@wg0.service
```