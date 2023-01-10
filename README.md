# my-arcam-remote
A remote for Arcam products using Svelte, Python and the
 [arcam_fmj library](https://github.com/elupus/arcam_fmj/).

## Running the App
### Step 1: Obtain Device IP Address
1. Ensure your arcam device is connected to your network via ethernet
 cable.
1. Obtain the device's IP address following the steps on
 [this document](https://www.arcam.co.uk/ugc/tor/SA10/User%20Manual/DISPLAY_SH295_EN-FR-DE-NL-ES-RU-IT-CN_Issue4_300120.pdf)
 on page 16 on the rightmost section.

### Step 2: Create `.env` file with ARCAM_IP entry
create a `.env` file in the project directory with the contents below. Ensure
 the ip address matches the value you got from step 1.
```
ARCAM_IP=192.168.1.1
```

### Step 3: Run the application with docker-compose
1. Make sure docker-compose is installed.
1. From the `my-arcam-remote` directory run `docker-compose up`.
1. The website should be accessible at http://localhost after building. 
 
## Example Screenshot
The website has a simple UI for both the browser and the phone:

![Website](https://user-images.githubusercontent.com/36345325/211490821-420309f2-6e0c-471b-ad82-45ca5830eacc.png)

