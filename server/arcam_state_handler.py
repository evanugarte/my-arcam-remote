import asyncio
import threading

from arcam_fmj.src.arcam.fmj import SourceCodes, ApiModel
from arcam_fmj.src.arcam.fmj.client import Client
from arcam_fmj.src.arcam.fmj.client import ClientContext
from arcam_fmj.src.arcam.fmj.state import State

from constants import DeviceMetric
from logger import logger

class ArcamStateHandler:
    # Amount of time to wait before sending debounced volume
    # requests to the amplifier. See set_volume for more context.
    DEBOUNCE_DELAY_SECONDS = 0.25

    def __init__(self, ip, port, zone=1):
        self.client = Client(ip, port)
        self.zone = zone

    def source_to_str(self, source):
        return {
            1: "PHONO",
            2: "AUX",
            3: "PVR",
            4: "AV",
            5: "STB",
            6: "CD",
            7: "BD",
            8: "SAT",
        }.get(source)


    def str_to_source(self, source):
        return {
            "PHONO": SourceCodes.PHONO,
            "AUX": SourceCodes.AUX,
            "PVR": SourceCodes.PVR,
            "AV": SourceCodes.AV,
            "STB": SourceCodes.STB,
            "CD": SourceCodes.CD,
            "BD": SourceCodes.BD,
            "SAT": SourceCodes.SAT
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
                state = State(self.client, self.zone, api_model=ApiModel.APISA_SERIES)
                power = await state.get_power()
                mute = await state.get_mute()
                volume = await state.get_volume()
                source = self.source_to_str(
                        await state.get_source()
                    )
                await self.client.stop()
                return {
                    "success": True,
                    "power": power,
                    "mute": mute,
                    "volume": volume,
                    "source": source
                }
        except Exception:
            logger.exception("error getting device state for health check")
            return {
                "success": False,
            }

    async def set_mute(self, value):
        success = True
        try:
            async with ClientContext(self.client):
                state = State(self.client, self.zone, api_model=ApiModel.APISA_SERIES)
                await state.set_mute(value)
                await self.client.stop()
        except Exception:
            success = False
            logger.exception("error setting mute state")
        finally:
            return {
                "success": success
            }

    async def set_power(self, value):
        success = True
        try:
            async with ClientContext(self.client):
                state = State(self.client, self.zone, api_model=ApiModel.APISA_SERIES)
                await state.set_power(value)
                await self.client.stop()
        except Exception:
            logger.exception("error setting power state")
            success = False
        finally:
            return {
                "success": success
            }

    async def actually_do_volume(self, value):
        success = True
        try:
            async with ClientContext(self.client):
                state = State(self.client, self.zone, api_model=ApiModel.APISA_SERIES)
                await state.set_volume(value)
                await self.client.stop()
        except Exception:
            logger.exception("error setting volume level")

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
                state = State(self.client, self.zone, api_model=ApiModel.APISA_SERIES)
                await state.set_source(
                    self.str_to_source(source_as_str)
                )
                await self.client.stop()
        except Exception:
            success = False
            logger.exception("error setting source")
        finally:
            return {
                "success": success
            }
    
    async def set_metric(self, metric, value):
        function = self.metric_to_function(metric)
        if function is None:
            return {
                "success": False
            }
        return await function(value)
