import pika
import time
import json
import random
import os  # Required to read environment variables

# --- Configuration ---
# These now pull from your ConfigMap via the Deployment YAML
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")
DELAY_MIN = float(os.getenv("DELAY_MIN", 1.0))
max_delay_env = os.getenv("DELAY_MAX", 5.0)
DELAY_MAX = float(max_delay_env)

def get_rabbitmq_connection():
    while True:
        try:
            print(f"[*] Attempting to connect to RabbitMQ at {RABBITMQ_HOST}...")
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(host=RABBITMQ_HOST)
            )
            return connection
        except pika.exceptions.AMQPConnectionError:
            print("[!] Connection failed. Retrying in 5 seconds...")
            time.sleep(5)

def generate_satellite_stats():
    connection = get_rabbitmq_connection()
    channel = connection.channel()

    # Ensure the queue exists
    channel.queue_declare(queue='air_channel_stats')

    print(f"[*] Successfully connected. Logic: Random delay between {DELAY_MIN}s and {DELAY_MAX}s.")
    print("[*] Starting telemetry generation. Press Ctrl+C to exit.")

    try:
        while True:
            # Generate fake satellite telemetry
            data = {
                "satellite_id": f"SAT-{random.randint(1000, 9999)}",
                "snr_db": round(random.uniform(5.0, 25.0), 2),
                "doppler_shift_hz": random.randint(-5000, 5000),
                "timestamp": time.time()
            }

            # Send to RabbitMQ
            message = json.dumps(data)
            channel.basic_publish(
                exchange='',
                routing_key='air_channel_stats',
                body=message
            )
            
            print(f" [x] Sent: {data['satellite_id']} | SNR: {data['snr_db']} dB")

            # Use the values from the ConfigMap
            sleep_time = random.uniform(DELAY_MIN, DELAY_MAX)
            time.sleep(sleep_time)

    except KeyboardInterrupt:
        print("\n[!] Stopping generator...")
        connection.close()

if __name__ == "__main__":
    generate_satellite_stats()