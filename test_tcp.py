import socket
import sys

def run_server(port=8000):
    try:
        # Create a TCP/IP socket
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        # Bind the socket to the port
        server_address = ('127.0.0.1', port)
        print(f"Starting server on {server_address}")
        server_socket.bind(server_address)
        
        # Listen for incoming connections
        server_socket.listen(1)
        print("Waiting for a connection...")
        
        while True:
            try:
                # Wait for a connection
                connection, client_address = server_socket.accept()
                print(f"Connection from {client_address}")
                
                # Send a simple response
                response = "Hello! Server is working!\n"
                connection.sendall(response.encode())
                
                # Clean up the connection
                connection.close()
                
            except KeyboardInterrupt:
                print("\nShutting down server...")
                break
                
    except socket.error as e:
        print(f"Error: {e}")
        sys.exit(1)
    finally:
        server_socket.close()

if __name__ == '__main__':
    run_server() 