# my-arcam-remote
A remote for Arcam products using Svelte, Python and the
 [arcam_fmj library](https://github.com/elupus/arcam_fmj/).

## Running the App
### Step 0: Getting Device IP Address
1. Ensure your arcam device is connected to your network via ethernet
 cable.
1. Obtain the device's IP address following the steps on
 [this document](https://www.arcam.co.uk/ugc/tor/SA10/User%20Manual/DISPLAY_SH295_EN-FR-DE-NL-ES-RU-IT-CN_Issue4_300120.pdf)
 on page 16 on the rightmost section.

### With Docker
1. Make sure docker-compose is installed.
1. Clone the project.
1. With the device IP from step 0, change the value in
 [docker-compose.yml:9](https://github.com/evanugarte/my-arcam-remote/blob/6070fedab54b93c9ff233b06c9a4c9d68c0ac92c/docker-compose.yml#L9)
 to the correct address.
1. From the `my-arcam-remote` directory run `docker-compose up`.
1. The website should be accessible at `localhost` after building.

### Without Docker
1. Ensure python and node are installed.
1. Clone the project.
1. Run the setup bash file with `chmod +x setup.sh && ./setup.sh`.
1. In the `website/` directory run `npm run build`.
1. Run the flask server from the topmost directory with:
```bash
HOST_IP=<DEVICE IP> FLASK_APP=server.py FLASK_ENV=development \
flask run --port 8080 --host 0.0.0.0
```
**Note:** substitute `<DEVICE IP>` with the IP address obtained in step 0.

The server should now be running and print `Running on <domain>`. Accessing
 the domain on a browser should show the website.
 
 
## Example Screenshot
The website has a simple UI for both the browser and the phone:

![Website](https://user-images.githubusercontent.com/36345325/130171453-d0aabb35-3e3e-46e3-9567-1ee3f0329c10.png)

