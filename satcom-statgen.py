import pika
import json
import time
import random
import os
import sys

def generate_air_channel_stats():
    """Generates random statistics for a satellite air channel."""
    return {
        'timestamp': time.time(),
        'satellite_id': f'SAT-{random.randint(1000, 9999)}',
        'channel_id': f'CHAN-{random.randint(1, 12)}',
        'signal_to_noise_ratio': random.uniform(10, 30),
        'bit_error_rate': random.uniform(1e-7, 1e-5),
        'carrier_frequency': random.uniform(12.2, 12.7),
        'doppler_shift': random.uniform(-5, 5),
        'attenuation': random.uniform(0.5, 3.0),
        'link_margin': random.uniform(3, 10),
    }

def get_rabbitmq_connection():
    """Attempts to connect to RabbitMQ with retry logic."""
    rabbitmq_host = os.environ.get('RABBITMQ_HOST', 'rabbitmq')
    while True:
        try:
            print(f"[*] Attempting to connect to RabbitMQ at {rabbitmq_host}...")
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(host=rabbitmq_host, connection_attempts=3, retry_delay=5)
            )
            return connection
        except pika.exceptions.AMQPConnectionError:
            print("[!] RabbitMQ not available yet. Retrying in 5 seconds...")
            time.sleep(5)

if __name__ == '__main__':
    # Initial connection
    connection = get_rabbitmq_connection()
    channel = connection.channel()
    channel.queue_declare(queue='air_channel_stats')

    print("[*] Successfully connected. Starting telemetry generation...")

    try:
        while True:
            stats = generate_air_channel_stats()
            try:
                channel.basic_publish(
                    exchange='',
                    routing_key='air_channel_stats',
                    body=json.dumps(stats)
                )
                print(f" [x] Sent: {stats['satellite_id']} stats")
            except pika.exceptions.AMQPConnectionError:
                print("[!] Connection lost. Reconnecting...")
                connection = get_rabbitmq_connection()
                channel = connection.channel()
            
            time.sleep(random.randint(1, 5))
    except KeyboardInterrupt:
        print("Stopping...")
        connection.close()