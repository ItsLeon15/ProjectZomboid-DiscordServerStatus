import socket
import struct


class RCONClient:
    SERVERDATA_AUTH = 3
    SERVERDATA_AUTH_RESPONSE = 2
    SERVERDATA_EXECCOMMAND = 2
    SERVERDATA_RESPONSE_VALUE = 0

    def __init__(self, host, port, password, timeout=5):
        self.host = host
        self.port = port
        self.password = password
        self.timeout = timeout
        self.socket = None
        self.request_id = 0

    def connect(self):
        """Establish a connection to the RCON server."""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(self.timeout)
            self.socket.connect((self.host, self.port))
            print(f"Connected to RCON server at {self.host}:{self.port}")
            self._authenticate()
        except Exception as e:
            self.disconnect()
            raise Exception(f"Failed to connect to RCON server: {e}")

    def disconnect(self):
        """Close the connection to the RCON server."""
        if self.socket:
            self.socket.close()
            self.socket = None

    def _authenticate(self):
        """Authenticate with the RCON server using the provided password."""
        auth_response = self._send_packet(self.SERVERDATA_AUTH, self.password)
        print(f"AUTH RESPONSE: {auth_response}")

        if auth_response.type == self.SERVERDATA_RESPONSE_VALUE and auth_response.request_id == self.request_id:
            print("Unexpected response type, but request ID matches. Assuming success.")
        elif auth_response.type != self.SERVERDATA_AUTH_RESPONSE or auth_response.request_id == -1:
            raise Exception("Authentication failed.")
        print("RCON authentication successful.")

    def send_command(self, command):
        """Send a command to the RCON server and return the response."""
        try:
            response = self._send_packet(self.SERVERDATA_EXECCOMMAND, command)
            return response.body
        except Exception as e:
            raise Exception(f"Failed to execute command '{command}': {e}")

    def _send_packet(self, cmd_type, body):
        """Send a packet to the RCON server and return the response."""
        self.request_id += 1
        packet = self._create_packet(self.request_id, cmd_type, body)
        self.socket.sendall(packet)
        print(f"Sent packet (type={cmd_type}): {packet.hex()}")
        return self._read_response()

    def _create_packet(self, request_id, cmd_type, body):
        """Create an RCON packet."""
        body_bytes = body.encode('utf-8')
        packet_size = 4 + 4 + len(body_bytes) + 2
        return struct.pack('<iii', packet_size, request_id, cmd_type) + body_bytes + b'\x00\x00'

    def _read_response(self):
        """Read the response packet(s) from the server."""
        try:
            size_data = self.socket.recv(4)
            if not size_data:
                raise Exception("No data received from the server.")
            packet_size = struct.unpack('<i', size_data)[0]
            packet_data = self.socket.recv(packet_size)
            print(f"Raw response packet (initial): {packet_data.hex()}")

            request_id, response_type = struct.unpack('<ii', packet_data[:8])
            body = packet_data[8:-2].decode('utf-8')
            total_data = body
            while True:
                self.socket.settimeout(0.5)
                try:
                    more_data = self.socket.recv(4096)
                    if not more_data:
                        break
                    print(f"Raw additional packet: {more_data.hex()}")
                    total_data += more_data.decode('utf-8')
                except socket.timeout:
                    break

            return RCONResponse(request_id, response_type, total_data)
        except Exception as e:
            raise Exception(f"Failed to read response: {e}")


class RCONResponse:
    def __init__(self, request_id, response_type, body):
        self.request_id = request_id
        self.type = response_type
        self.body = body

    def __repr__(self):
        return f"RCONResponse(request_id={self.request_id}, type={self.type}, body={self.body})"
