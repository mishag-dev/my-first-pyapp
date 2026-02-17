import pika
import os
import json
import time

# Configuration from Environment
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")
QUEUE_NAME = "air_channel_stats"

def process_telemetry(ch, method, properties, body):
    try:
        # Parse the JSON message
        data = json.loads(body)
        
        # Format a nice output
        print("-" * 40)
        print(f"📡 SATELLITE REPORT: {data.get('satellite_id')}")
        print(f"   SNR:      {data.get('signal_noice_ratio') or data.get('snr_db'):.2f} dB")
        print(f"   Doppler:  {data.get('doppler_shift'):.2f} Hz")
        print(f"   Freq:     {data.get('carrier_frequency'):.2f} MHz")
        print(f"   Status:   PROCESSING SUCCESS")
        
        # Acknowledge the message (removes it from RabbitMQ)
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        print(f" [!] Error processing message: {e}")

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