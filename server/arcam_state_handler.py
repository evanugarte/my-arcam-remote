import asyncio
import threading
import time

from arcam_fmj.src.arcam.fmj import SA10SourceCodes
from arcam_fmj.src.arcam.fmj.client import Client
from arcam_fmj.src.arcam.fmj.client import ClientContext
from arcam_fmj.src.arcam.fmj.state import State

class ArcamStateHandler:
    # Amount of time to wait before sending debounced volume
    # requests to the amplifier. See handle_volume for more context.
    DEBOUNCE_DELAY_SECONDS = 0.5

    def __init__(self, ip, port, zone):
        self.client = Client(ip, port)
        self.zone = zone
        self.volume_value = None

    def source_to_str(self, source):
        return {
            SA10SourceCodes.PHONO: "PHONO",
            SA10SourceCodes.AUX: "AUX",
            SA10SourceCodes.PVR: "PVR",
            SA10SourceCodes.AV: "AV",
            SA10SourceCodes.STB: "STB",
            SA10SourceCodes.CD: "CD",
            SA10SourceCodes.BD: "BD",
            SA10SourceCodes.SAT: "SAT"
        }.get(source)


    def str_to_source(self, source):
        return {
            "PHONO": SA10SourceCodes.PHONO,
            "AUX": SA10SourceCodes.AUX,
            "PVR": SA10SourceCodes.PVR,
            "AV": SA10SourceCodes.AV,
            "STB": SA10SourceCodes.STB,
            "CD": SA10SourceCodes.CD,
            "BD": SA10SourceCodes.BD,
            "SAT": SA10SourceCodes.SAT
        }.get(source)

    async def health_check(self):
        try:
            async with ClientContext(self.client):
                state = State(self.client, self.zone)
                power = await state.get_power(use_state=False),
                mute = await state.get_mute(use_state=False),
                volume = await state.get_volume(use_state=False),
                source = self.source_to_str(
                        await state.get_source(use_state=False)
                    )
                await self.client.stop()
                return {
                    "success": True,
                    "power": power[0],
                    "mute": mute[0],
                    "volume": volume[0],
                    "source": source
                }
        except Exception:
            return {
                "success": False,
            }

    async def handle_mute(self, value):
        success = True
        try:
            async with ClientContext(self.client):
                state = State(self.client, self.zone)
                await state.set_mute(value, use_rc5=False)
                await self.client.stop()
        except Exception:
            success = False
        finally:
            return {
                "success": success
            }

    async def handle_power(self, value):
        success = True
        try:
            async with ClientContext(self.client):
                state = State(self.client, self.zone)
                await state.set_power(value, use_rc5=False)
                await self.client.stop()
        except Exception:
            success = False
        finally:
            return {
                "success": success
            }

    async def actually_do_volume(self, value):
        async with ClientContext(self.client):
            state = State(self.client, self.zone)
            await state.set_volume(value)
            await self.client.stop()

    async def handle_volume(self, value_from_client):
        # debounce logic for adjusting Arcam volume
        def call_it(volume=None):
            print("call_it called with", self.volume_value, volume, flush=True)
            # conversion from a non async function to calling an async function
            # which is actually_do_volume
            if volume:
                value_to_write = volume
            else:
                value_to_write = self.volume_value
            print("finally writing::::", value_to_write, flush=True)
            if value_to_write:
                asyncio.run(self.actually_do_volume(value_to_write))
            self.t = None
        try:
            # when we receive a message, try replacing the timer
            # the first step is canceling the existing timer
            if self.t.is_alive:
                self.volume_value = value_from_client
        except(AttributeError):
            await self.actually_do_volume(value_from_client)
            self.volume_value = None
            # we tried to cancel but a timer didn’t exist. Oh well, we
            # can still resume the normal program flow as the below section
            # creates a new timer for us no matter what
            self.t = threading.Timer(self.DEBOUNCE_DELAY_SECONDS, call_it)
            # start the timer. Wait for any other takes to update
            # volume state before actually updating the amplifier.
            self.t.start()
        # create a new timer to call the true updater function with
        # the most recent value we got. the most recent value is
        # the parameter to the function
        # 0.25 works reliably

        # laz:
        # I’d consider an alternative: send the first request you get,
        # then set a timer for 500ms or something and aggregate all changes
        # for that window. if anything is set in the window, send the
        # final value and set another timer.
        # lie to the user and say it was successful. mongodb is web scale.
        return {
            "success": True
        }

    async def handle_source(self, source_as_str):
        success = True
        try:
            async with ClientContext(self.client):
                state = State(self.client, self.zone)
                await state.set_source(
                    self.str_to_source(source_as_str),
                    use_rc5=False
                )
                await self.client.stop()
        except Exception:
            success = False
        finally:
            return {
                "success": success
            }
