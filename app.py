import random
from prometheus_client import start_http_server, Gauge, Counter
import time

# Create Gauge metrics
custom_metric = Gauge('custom_metric', 'Description of custom metric')
other_metric = Gauge('other_metric', 'Description of other metric')

# Create a Counter metric
counter_metric = Counter('counter_metric', 'Description of counter metric')

if __name__ == '__main__':
    # Start an HTTP server to expose metrics
    start_http_server(8010)  # Expose metrics on port 8010

    while True:
        # Simulate random data for the custom metric
        random_value = random.randint(1, 100)  # Generate a random value between 1 and 100
        custom_metric.set(random_value)  # Set the value of the custom metric to the random value

        # Simulate random data for another metric
        other_random_value = random.randint(50, 150)  # Generate another random value
        other_metric.set(other_random_value)  # Set the value of the other metric to the random value

        # Increment the counter metric
        counter_metric.inc()

        time.sleep(5)  # Update the metrics every 5 seconds