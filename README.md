# my-arcam-remote
A remote for Arcam products using Svelte, Python and the arcam_fmj library.

## Running the App
### Without Docker
1. Make sure python3 and node are installed before starting.
1. Ensure your arcam device is connected to your network via ethernet
 cable. Obtain the device's IP address following the steps on
 [this document](https://www.arcam.co.uk/ugc/tor/SA10/User%20Manual/DISPLAY_SH295_EN-FR-DE-NL-ES-RU-IT-CN_Issue4_300120.pdf)
 on page 16 on the rightmost section.

1. Run the setup bash file with `chmod +x setup.sh && ./setup.sh`
1. In the `website/` directory run `npm run build`
1. Run the flask server from the topmost directory with
```bash
HOST_IP=<DEVICE IP> FLASK_APP=server.py FLASK_ENV=development \
flask run --port 8080 --host 0.0.0.0
```
**Note:** substitute `<DEVICE IP>` with the IP address obtained in step 2.

The server should now be running and print `Running on <domain>`. Accessing
 the domain on a browser should show the website.

