from prometheus_client import Histogram
from prometheus_client import Counter
from prometheus_client import Gauge

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
