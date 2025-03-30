import socket
import sys
import time

def create_http_response():
    return '''HTTP/1.1 200 OK
Content-Type: text/html
Connection: close

<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Simple HTTP Server</title>
</head>
<body>
    <h1>Simple HTTP Server</h1>
    <p>If you can see this, the server is working!</p>
</body>
</html>'''.encode()

def run_server(port=3000):
    try:
        # Create a TCP/IP socket
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        # Allow reuse of the address
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        # Bind the socket to the port
        server_address = ('127.0.0.1', port)
        print(f"Starting server on {server_address}")
        try:
            server_socket.bind(server_address)
            print("Successfully bound to address")
        except socket.error as e:
            print(f"Failed to bind to address: {e}")
            sys.exit(1)
        
        # Listen for incoming connections
        server_socket.listen(1)
        print(f"Listening on port {port}...")
        
        while True:
            try:
                print("\nWaiting for a connection...")
                # Wait for a connection
                connection, client_address = server_socket.accept()
                print(f"Connection from {client_address}")
                
                # Receive the request
                request = connection.recv(1024)
                print(f"Received request: {request.decode()}")
                
                # Send the response
                response = create_http_response()
                connection.sendall(response)
                print("Sent response")
                
                # Clean up the connection
                connection.close()
                print("Connection closed")
                
            except KeyboardInterrupt:
                print("\nShutting down server...")
                break
            except Exception as e:
                print(f"Error handling connection: {e}")
                continue
                
    except socket.error as e:
        print(f"Socket error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)
    finally:
        print("Closing server socket...")
        server_socket.close()

if __name__ == '__main__':
    print("Starting HTTP server...")
    run_server() 