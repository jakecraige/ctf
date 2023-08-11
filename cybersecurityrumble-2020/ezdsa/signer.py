import socketserver
import random
import ecdsa


key = open("secp256k1-key.pem").read()
sk = ecdsa.SigningKey.from_pem(key)


def sony_rand(n):
    return random.getrandbits(8*n).to_bytes(n, "big")


def sign(data):
    if data == b"admin":
        raise ValueError("Not Permitted!")
    signature = sk.sign(data, entropy=sony_rand)
    return signature


class TCPHandler(socketserver.StreamRequestHandler):

    def handle(self):
        data = self.rfile.readline().strip()
        try:
            signature = sign(data).hex()
            self.wfile.write(b"Your token: " + data + b"," + signature.encode())
        except ValueError as ex:
            self.wfile.write(b"Invalid string submitted: " + str(ex).encode())


if __name__ == '__main__':
    server = socketserver.ForkingTCPServer(("0.0.0.0", 10101), TCPHandler)
    server.serve_forever()

