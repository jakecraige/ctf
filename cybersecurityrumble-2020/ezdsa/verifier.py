import socketserver
import ecdsa
import pyjokes
from flag import FLAG


key = open("pub.pem").read()
vk = ecdsa.VerifyingKey.from_pem(key) 


def valid_signature(msg, sig):
    try:
        vk.verify(sig, msg)
        return True
    except ecdsa.BadSignatureError:
        return False


class TCPHandler(socketserver.StreamRequestHandler):

    def handle(self):
        data = self.rfile.readline().strip()
        user, signature = data.split(b",")
        sig = bytes.fromhex(signature.decode())
        try:
            if valid_signature(user, sig):
                if user == b"admin":
                    self.wfile.write(b"Hello admin! Here is your flag: " + FLAG)
                else:
                    self.wfile.write(pyjokes.get_joke().encode())
            else:
                self.wfile.write(b"Invalid signature!")
        except Exception as ex:
            self.wfile.write(b"Something went wrong!")


if __name__ == '__main__':
    server = socketserver.ForkingTCPServer(("0.0.0.0", 10100), TCPHandler)
    server.serve_forever()

