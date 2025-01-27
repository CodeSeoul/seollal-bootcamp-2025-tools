import socket
import dns.resolver
import time
import ssl
from http.client import HTTPConnection, HTTPSConnection


print('demonstrating change')


def demonstrate_request_lifecycle():
    url = input("Enter the URL :) (e.g., https://www.example.com): ").strip()
    if not url.startswith("http://") and not url.startswith("https://"):
        print("Please enter a valid URL starting with 'http://' or 'https://'")
        return

    print(f"\nURL entered: {url}\n")

    # Step 1: DNS Lookup
    hostname = url.split("//")[-1].split("/")[0]
    print(f"Resolving DNS for: {hostname}")
    try:
        dns_start = time.time()
        answers = dns.resolver.resolve(hostname, 'A')
        ip_addresses = [answer.to_text() for answer in answers]
        dns_end = time.time()
        print(f"IP addresses resolved: {ip_addresses}")
        print(f"DNS lookup time: {dns_end - dns_start:.4f} seconds\n")
    except Exception as e:
        print(f"DNS resolution failed: {e}")
        return

    # Step 2: TCP Connection
    target_ip = ip_addresses[0]
    port = 443 if url.startswith("https://") else 80
    print(f"Establishing TCP connection to {target_ip}:{port}")
    try:
        tcp_start = time.time()
        sock = socket.create_connection((target_ip, port), timeout=5)
        tcp_end = time.time()
        print(f"TCP connection established.")
        print(f"TCP connection time: {tcp_end - tcp_start:.4f} seconds\n")
    except Exception as e:
        print(f"TCP connection failed: {e}")
        return

    # Step 3: TLS Handshake (if HTTPS)
    if port == 443:
        print("Starting TLS handshake...")
        try:
            tls_start = time.time()
            context = ssl.create_default_context()
            secure_sock = context.wrap_socket(sock, server_hostname=hostname)
            tls_end = time.time()
            print("TLS handshake completed.")
            print(f"TLS handshake time: {tls_end - tls_start:.4f} seconds\n")
        except Exception as e:
            print(f"TLS handshake failed: {e}")
            return
    else:
        secure_sock = sock

    # Step 4: HTTP Request
    path = "/" if "/" not in url.split(hostname)[-1] else url.split(hostname)[-1]
    print(f"Sending HTTP GET request to {url}")
    try:
        http_start = time.time()
        if port == 443:
            connection = HTTPSConnection(hostname, timeout=5, context=context)
        else:
            connection = HTTPConnection(hostname, timeout=5)

        connection.request("GET", path)
        response = connection.getresponse()
        http_end = time.time()
        print(f"HTTP response status: {response.status}")
        print(f"HTTP response reason: {response.reason}")
        print(f"HTTP request time: {http_end - http_start:.4f} seconds\n")
        print("Response headers:")
        for header, value in response.getheaders():
            print(f"{header}: {value}")
    except Exception as e:
        print(f"HTTP request failed: {e}")
        return
    finally:
        connection.close()


# Run the interactive script
demonstrate_request_lifecycle()
