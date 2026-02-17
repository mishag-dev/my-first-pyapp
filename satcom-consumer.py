import pika
import os
import json
import time

# Configuration from Environment
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")
QUEUE_NAME = "air_channel_stats"

def process_telemetry(ch, method, properties, body):
    try:
        data = json.loads(body)
        
        # Helper to safely get a float or return 0.0
        def safe_float(key, alt_key=None):
            val = data.get(key) or data.get(alt_key)
            try:
                return float(val) if val is not None else 0.0
            except (ValueError, TypeError):
                return 0.0

        snr = safe_float('snr_db', 'signal_noice_ratio')
        doppler = safe_float('doppler_shift_hz', 'doppler_shift')
        freq = safe_float('carrier_frequency')

        print("-" * 40)
        print(f"📡 SATELLITE REPORT: {data.get('satellite_id', 'UNKNOWN')}")
        print(f"   SNR:      {snr:.2f} dB")
        print(f"   Doppler:  {doppler:.2f} Hz")
        print(f"   Status:   SUCCESS")
        
        ch.basic_ack(delivery_tag=method.delivery_tag)
        
    except Exception as e:
        # If it fails, we still ACK it to remove the "bad" message from the queue
        # otherwise it will loop forever!
        print(f" [!] Permanent failure on message: {e}")
        ch.basic_ack(delivery_tag=method.delivery_tag)

def start_consumer():
    print(f"[*] Connecting to {RABBITMQ_HOST}...")
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
    channel = connection.channel()

    # Ensure the queue exists
    channel.queue_declare(queue=QUEUE_NAME)

    # Tell RabbitMQ not to give more than 1 message to a worker at a time
    channel.basic_qos(prefetch_count=1)
    
    channel.basic_consume(queue=QUEUE_NAME, on_message_callback=process_telemetry)

    print(f"[*] Waiting for satellite data on '{QUEUE_NAME}'. To exit press CTRL+C")
    channel.start_consuming()

if __name__ == "__main__":
    start_consumer()