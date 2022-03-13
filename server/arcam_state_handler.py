from arcam_fmj.src.arcam.fmj import SA10SourceCodes
from arcam_fmj.src.arcam.fmj.client import Client
from arcam_fmj.src.arcam.fmj.client import ClientContext
from arcam_fmj.src.arcam.fmj.state import State

class ArcamStateHandler:
    def __init__(self, ip, port, zone):
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

    async def handle_volume(self, value):
        success = True
        try:
            async with ClientContext(self.client):
                state = State(self.client, self.zone)
                await state.set_volume(value)
                await self.client.stop()
        except Exception:
            success = False
        finally:
            return {
                "success": success
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
