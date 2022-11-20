import asyncio
import threading
import time

from arcam_fmj.src.arcam.fmj import SA10SourceCodes
from arcam_fmj.src.arcam.fmj.client import Client
from arcam_fmj.src.arcam.fmj.client import ClientContext
from arcam_fmj.src.arcam.fmj.state import State

from constants import DeviceMetric

class ArcamStateHandler:
    # Amount of time to wait before sending debounced volume
    # requests to the amplifier. See set_volume for more context.
    DEBOUNCE_DELAY_SECONDS = 0.25

    def __init__(self, ip, port, zone=1):
        self.client = Client(ip, port)
        self.zone = zone

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
    
    def metric_to_function(self, metric):
        return {
            DeviceMetric.MUTE: self.set_mute,
            DeviceMetric.POWER: self.set_power,
            DeviceMetric.VOLUME: self.set_volume,
            DeviceMetric.SOURCE: self.set_source,
        }.get(metric)

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

    async def set_mute(self, value):
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

    async def set_power(self, value):
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
        success = True
        async with ClientContext(self.client):
            state = State(self.client, self.zone)
            await state.set_volume(value)
            await self.client.stop()

    async def set_volume(self, value):
        # debounce logic for adjusting Arcam volume
        def call_it():
            # conversion from a non async function to calling an async function
            # which is actually_do_volume
            asyncio.run(self.actually_do_volume(value))
        try:
            # when we receive a message, try replacing the timer
            # the first step is canceling the existing timer
            self.t.cancel()
        except(AttributeError):
            # we tried to cancel but a timer didn’t exist. Oh well, we
            # can still resume the normal program flow as the below section
            # creates a new timer for us no matter what
            pass
        # create a new timer to call the true updater function with
        # the most recent value we got. the most recent value is
        # the parameter to the function
        # 0.25 works reliably
        self.t = threading.Timer(self.DEBOUNCE_DELAY_SECONDS, call_it)
        # start the timer. Wait for any other takes to update
        # volume state before actually updating the amplifier.
        self.t.start()
        # lie to the user and say it was successful. mongodb is web scale.
        return {
            "success": True
        }

    async def set_source(self, source_as_str):
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
    
    async def set_metric(self, metric, value):
        function = self.metric_to_function(metric)
        if function is None:
            return {
                "success": success
            }
        return await function(value)
