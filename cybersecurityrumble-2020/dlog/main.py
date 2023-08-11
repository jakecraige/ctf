import os


class AffinePoint:

    def __init__(self, curve, x, y):
        self.curve = curve
        self.x = x
        self.y = y

    def __add__(self, other):
        return self.curve.add(self, other)

    def __iadd__(self, other):
        return self.__add__(other)

    def __rmul__(self, scalar):
        return self.curve.mul(self, scalar)

    def __str__(self):
        return "Point({},{}) on {}".format(self.x, self.y, self.curve)

    def copy(self):
        return AffinePoint(self.curve, self.x, self.y)

    def __eq__(self, other):
        if not isinstance(other, AffinePoint):
            raise ValueError("Can't compare Point to {}".format(type(other)))
        return self.curve == other.curve and self.x == other.x and self.y == other.y


class EllipticCurve:

    def __init__(self, a, b, p):
        """
        Define curve by short weierstrass form y**2 = x**3 + ax + b mod p
        """
        self.a = a
        self.b = b
        self.mod = p
        self.poif = AffinePoint(self, "infinity", "infinity")

    def inv_val(self, val):
        """
        Get the inverse of a given field element in the curve's prime field.
        """
        return pow(val, self.mod - 2, self.mod)


    def invert(self, point):
        """
        Invert a point.
        """
        return AffinePoint(self, point.x, (-1 * point.y) % self.mod)

    def mul(self, point, scalar):
        """
        Do scalar multiplication Q = dP using double and add.
        """
        return self.double_and_add(point, scalar)

    def double_and_add(self, point, scalar):
        """
        Do scalar multiplication Q = dP using double and add.
        As here: https://en.wikipedia.org/wiki/Elliptic_curve_point_multiplication#Double-and-add
        """
        if scalar < 1:
            raise ValueError("Scalar must be >= 1")
        result = None
        tmp = point.copy()

        while scalar:
            if scalar & 1:
                if result is None:
                    result = tmp
                else:
                    result = self.add(result, tmp)
            scalar >>= 1
            tmp = self.add(tmp, tmp)

        return result

    def add(self, P, Q):
        """
        Sum of the points P and Q.
        Rules: https://en.wikipedia.org/wiki/Elliptic_curve_point_multiplication
        """
        # Cases with POIF
        if P == self.poif:
            result = Q
        elif Q == self.poif:
            result = P
        elif Q == self.invert(P):
            result = self.poif
        else:  # without POIF
            if P == Q:
                slope = (3 * P.x ** 2 + self.a) * self.inv_val(2 * P.y)
            else:
                slope = (Q.y - P.y) * self.inv_val(Q.x - P.x)
            x = (slope ** 2 - P.x - Q.x) % self.mod
            y = (slope * (P.x - x) - P.y) % self.mod
            result = AffinePoint(self, x, y)

        return result

    def __str__(self):
        return "y^2 = x^3 + {}x + {} mod {}".format(self.a, self.b, self.mod)


a = 0
b = 7
p = 0xfffffffffffffffffffffffffffffffffffffffffffffffffffffffefffffc2f

secp256k1 = EllipticCurve(a, b, p)

print("gif point to nom nom:")
x = input("x: ")
y = input("y: ")

if len(x) > 78 or len(y) > 78:
    print("values too large!")
    exit(0)

G = AffinePoint(
        secp256k1,
        int(x), int(y)
)

secret = int.from_bytes(os.urandom(32), "big")
#  secret = int.from_bytes(b"1337", "big")

print("Have curve point: ")
print(secret * G)

user_secret = int(input("now gif secret: "))

if secret == user_secret:
    print("Congratzzzzz!")
    print(open("/opt/flag.txt").read())
else:
    print("Nein!")
