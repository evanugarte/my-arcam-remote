<script>
  import { onMount } from 'svelte';
  import Modal from "sv-bootstrap-modal";

  let data = {};
  let isOpen = false;
  let sources = [
    "PHONO",
    "AUX",
    "PVR",
    "AV",
    "STB",
    "CD",
    "BD",
    "SAT"
  ];

  async function healthCheck() {
    const res = await fetch(`./api/health-check`);
    data = await res.json();
  }

  onMount(async () => {
    await healthCheck();
  });

  async function handleVolume(modifier) {
    const newVolume = data.volume + modifier;
    if (newVolume >= 0 && newVolume <= 99) {
      await fetch(`./api/volume?value=${newVolume}`, {method: 'POST'});
    }
  }

  async function handleMute() {
    const numericalInverse = ~~!data.mute
    await fetch(`./api/mute?value=${numericalInverse}`, {method: 'POST'});
  }

  async function handlePower() {
    const numericalInverse = ~~!data.power
    await fetch(`./api/power?value=${numericalInverse}`, {method: 'POST'});
  }

  async function handleSource(source) {
    await fetch(`./api/source?value=${source}`, {method: 'POST'});
  }

  let tabInactive;

  window.onfocus = async function () { 
    if (tabInactive) {
      tabInactive = false;
      await healthCheck();
    }
  }; 

  window.onblur = function () { 
    tabInactive = true; 
  }; 

  $: activeSource = data.source;

  let eventSource = new EventSource(
        "./api/listen",
    );
    eventSource.onopen = () => {}
    eventSource.onmessage = (msg) => {
      try {
        const { data: serverMessage } = msg;        
        const parsedMessage = JSON.parse(serverMessage);
        data = {...data, ...parsedMessage};
      } catch (error) {
        console.error("unable to update amplifier:", e);
      }
    }
</script>

<style>
  @import url("https://cdn.jsdelivr.net/npm/bootstrap@5.0.0-beta3/dist/css/bootstrap.min.css");
  @import url("https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.3/css/all.min.css");
</style>

<main id="arcam-controller">
  <div class="container-yay">
    <div class="mx-auto mt-2">
        <span>Arcam Remote Control</span>
    </div>

    <div class="d-flex flex-row justify-content-center">
        <div class="menu-grid">
            <div class="d-flex flex-column align-items-center" on:click={handlePower}>
                <i class="fas fa-power-off active" style="color: {data.power === false ? 'green' : 'red'};"></i>
                <span class="label">Power</span>
            </div>
            <div id="source" on:click={() => (isOpen = true)} class="d-flex flex-column align-items-center">
              <i class="fas fa-sign-in-alt"></i>
              <span class="label">Source</span>
            </div>
        </div>
    </div>

    <div class="d-flex flex-row mt-4 justify-content-center px-2">
        <div class="flex-column align-items-center mt-2 px-4 mute" on:click={handleMute}>
            <div class="grey-bg justify-content-center align-self-baseline">
                <i class="fas {data.mute ? "fa-volume-up" : "fa-volume-mute"} p-3 control-icon "></i>
            </div>
            <span class="label">{data.mute ? "Unmute" : "Mute"}</span>
        </div>
        <div class="d-flex flex-column rounded-bg py-3 px-4 justify-content-center align-items-center volume">
            <i class="fas fa-plus py-3 control-icon" on:click={() => handleVolume(1)}></i>
            <span class="label py-3">Volume {data.volume ? data.volume : ''}</span>
            <i class="fas fa-minus py-3 control-icon" on:click={() => handleVolume(-1)}></i>
        </div>
    </div>
  </div>
  <Modal bind:open={isOpen}>
    <div class="modal-dialog" role="document">
      <div class="modal-content">
        <div class="modal-body">
          <div class="btn-group mr-2 source-group" role="group" aria-label="First group">
            {#each sources as source}
              <button
                type="button"
                class="btn btn-outline-secondary source-btn {activeSource === source ? 'active' : ''}"
                on:click={() => handleSource(source)}
              >
                {source}
              </button>
            {/each}
          </div>
        </div>
      </div>
    </div>
  </Modal>
</main>
