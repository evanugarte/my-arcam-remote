<script>
  import { onMount } from "svelte";

  import Minus from "./icons/Minus.svelte";
  import Plus from "./icons/Plus.svelte";
  import Power from "./icons/Power.svelte";
  import SignIn from "./icons/SignIn.svelte";
  import Speaker from "./icons/Speaker.svelte";
  import SpeakerMute from "./icons/SpeakerMute.svelte";

  let data = {};
  let isOpen = false;
  let loading = false;
  let sources = ["PHONO", "AUX", "PVR", "AV", "STB", "CD", "BD", "SAT"];

  async function healthCheck() {
    loading = true;
    const url = new URL(
      `./api/health-check`, window.location.href
    );
    const res = await fetch(url.href);
    data = await res.json();
    loading = false;
  }

  onMount(async () => {
    await healthCheck();
  });

  async function sendRequestToArcam(endpoint, value) {
    const url = new URL(
      `./api/set/${endpoint}?value=${value}`, window.location.href
    );
    await fetch(url.href, { method: "POST" });
  }

  function handleModalClick(event, close=false) {
    if (close) {
      isOpen = false;
    }
    event.stopPropagation();
    event.preventDefault();
  }

  function handleKeyPress(event, clickCallback, desiredKey=null) {
    let desiredKeyPressed = event.keyCode === desiredKey;
    if (desiredKey === null) {
      // if there is no specified desired key, we trigger the callback
      // if the enter (13) or the space key (32) was pressed
      desiredKeyPressed = event.keyCode === 13 || event.keyCode === 32;
    }
    if (desiredKeyPressed) {
      clickCallback();
    }
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

  window.addEventListener(
    'keydown',
    (event) => handleKeyPress(event, () => handleModalClick(event, true), 27),
  )

  $: activeSource = data.source;

  const eventSourceUrl = new URL(
    `./api/listen`, window.location.href
  );
  let eventSource = new EventSource(eventSourceUrl.href);
  eventSource.onopen = () => {};
  eventSource.onmessage = (msg) => {
    try {
      const { data: serverMessage } = msg;
      const parsedMessage = JSON.parse(serverMessage);
      data = { ...data, ...parsedMessage };
    } catch (error) {
      console.error("unable to update amplifier:", e);
    }
  };
</script>

<main id="arcam-controller" class={loading ? "disabled" : ""}>
  <div class="container-yay">
    <div class="title">
      <span>Arcam Remote Control</span>
    </div>

      <div class="row">
        <div
          class="top-button"
          on:click={() => sendRequestToArcam("power", ~~!data.power)}
          on:keypress={
            (event) =>
              handleKeyPress(event, () => sendRequestToArcam("power", ~~!data.power))
          }
        >
          <Power
            fill={data.power === false ? 'green' : 'red'}
          />
          <span class="label">Power</span>
        </div>
        <div
          id="source"
          on:click={() => (isOpen = true)}
          on:keypress={
            (event) =>
              handleKeyPress(event, () => (isOpen = true))
          }
          class="top-button"
        >
          <SignIn />
          <span class="label">Source</span>
        </div>
      </div>

    <div class="row row-top-padded">
      <div
        class="mute padding-middle"
        on:click={() => sendRequestToArcam("mute", ~~!data.mute)}
        on:keypress={
          (event) =>
            handleKeyPress(event, () => sendRequestToArcam("mute", ~~!data.mute))
        }
      >
        <div class="grey-bg">
          {#if data.mute}
            <Speaker />
          {:else}
            <SpeakerMute />
          {/if}
        </div>
        <span class="label">{data.mute ? "Unmute" : "Mute"}</span>
      </div>
      <div
        class="volume padding-1rem grey-bg rounded-bg"
      >
        <div
          class="volume-wrapper"
          on:click={() => sendRequestToArcam("volume", data.volume + 1)}
          on:keypress={
            (event) =>
            handleKeyPress(event, () => sendRequestToArcam("volume", data.volume + 1))
          }
        >
          <Plus />
        </div>
        <span class="label padding-1rem">
          Volume {typeof data.volume === 'number' ? data.volume : ''}
        </span>
        <div
          class="volume-wrapper"
          on:click={() => sendRequestToArcam("volume", data.volume - 1)}
          on:keypress={
            (event) =>
              handleKeyPress(event, () => sendRequestToArcam("volume", data.volume - 1))
          }
        >
          <Minus/>
        </div>
      </div>
    </div>
  </div>
  <div
    class="modal"
    on:click={(event) => handleModalClick(event, true)}
    on:keypress={
      (event) =>
        handleKeyPress(event, () => handleModalClick(event, true))
    }
    style="display: {isOpen ? 'block' : 'none'};"
    >
    <div
      class="modal-content"
      on:click={(event) => handleModalClick(event)}
      on:keypress={
        (event) =>
          handleKeyPress(event, () => handleModalClick(event))
      }
      role="document"
    >
          <div class="btn-group">
            {#each sources as source}
              <button
                type="button"
                class="source-btn {activeSource ===
                source
                  ? 'active'
                  : ''}"
                on:click={() => sendRequestToArcam("source", source)}
                on:keypress={
                  (event) =>
                    handleKeyPress(event, () => sendRequestToArcam("source", source))
                }
              >
                {source}
              </button>
            {/each}
          </div>
    </div>
  </div>
</main>
