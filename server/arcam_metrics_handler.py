from prometheus_client import Counter
from prometheus_client import Gauge
from prometheus_client import generate_latest
from prometheus_client import Histogram

from constants import DeviceMetric

class ArcamMetricsHandler:
  def initialize(self):
    self.health_check_latency_seconds = Histogram(
      'health_check_latency_seconds', 'Time spent processing health check'
    )
    self.network_latency_seconds = Histogram(
      'network_latency_seconds', 'Latency between REST API and Arcam amplifier'
    )
    self.write_request_count = Counter(
      'write_request_count',
      'Number of write requests sent to the Arcam amplifier',
    )
    self.network_errors = Counter(
      'network_errors',
      'Number of unsuccessful requests sent to the Arcam amplifier',
    )
    self.volume_state = Gauge(
      'volume_state',
      'Value of the Arcam amplifier\'s volume level',
    )
    self.mute_state = Gauge(
      'mute_state',
      'Value of the Arcam mute state, 0 for inavtive and 1 for active',
    )
    self.power_state = Gauge(
      'power_state',
      'Value of the Arcam power state, 0 for off and 1 for on',
    )

  def maybe_update_gauge_with_enum(self, metric_enum, value):
    maybe_result = {
      DeviceMetric.MUTE: self.mute_state,
      DeviceMetric.POWER: self.power_state,
      DeviceMetric.VOLUME: self.volume_state,
    }.get(metric_enum)

    # if the given enum doesn't contain an entry in the above map
    # do nothing. hence the "maybe" in this function's name
    if maybe_result is None:
      return
    # prometheus gauges only take integers as values so we cast
    # whatever we are given to an int
    maybe_result.set(int(value))

  def generate_latest(self):
    return generate_latest()
