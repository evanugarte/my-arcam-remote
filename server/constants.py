import enum


class DeviceMetric(enum.Enum):
  MUTE = ("mute", lambda x: bool(int(x)))
  POWER = ("power", lambda x: bool(int(x)))
  VOLUME = ("volume", lambda x: int(x), lambda x: x >= 0 and x <= 99)
  SOURCE = ("source", lambda x: str(x))

  def __init__(self, designation, cast_to_correct_type, is_valid=lambda x: True):
    self.designation = designation
    self.cast_to_correct_type = cast_to_correct_type
    self.is_valid = is_valid
