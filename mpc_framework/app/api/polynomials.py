import random
import numpy as np

class Polynomials:

    prime = 2 ** 127 - 1
    prime = 47

    # bivariate: poly with two variable f(x,y)
    # symetric: f(x1, x2, ..) = f(y1, y2, ..)
    # f(X, Y) = 3*(x2*y2) + 92*(x+y) + 10

    def create_poly_and_shares(self, secret, degree, shares):
        if (degree > shares or degree < 1):
            raise ValueError('shares ', 5, ' must be lager than degree ', degree, ' and degree must be higher than one')
        poly = self.create_bivariate_symetric_poly(secret, degree)
        shares = np.array([self.create_share(poly, k) for k in range(0, shares)])
        return poly, shares

    def create_bivariate_symetric_poly(self, secret, degree):
        poly = np.zeros((degree + 1, degree + 1))
        for x in range(degree + 1):
            for y in range(x + 1):
                coef = random.SystemRandom().randint(1, self.prime)
                poly[x][y] = coef
                poly[y][x] = coef
        poly[0, 0] = secret
        return poly

    def create_share(self, poly, k):
        k_vector = [k ** x for x in range(poly.__len__())]
        share = np.sum((poly * k_vector) % self.prime, axis=1)
        return share

    def eval_bi_poly(self, poly, x, y):
        result = 0;
        for i in range(poly.__len__()):
            for j in range(poly.__len__()):
                coefficient = poly[i][j]
                result += coefficient * (x ** i) * (y ** j)
                result %= self.prime
        return result

    def lagrange_interpolate(self, shares):
        # H = sum(f(j)*product(m/(m-j)     AKA       h(X) = sum (h(i) * delta_i(X)
        if len(shares) < 2:
            raise ValueError("need at least two shares")
        sum = 0
        recombination_vector = []
        for i in range(1, len(shares) + 1):
            product = 1
            for j in range(1, len(shares) + 1):
                if (i != j):
                    product *= self.divmod(j, j - i, self.prime)
                    product %= self.prime
            recombination_vector.append(product)
            sum += shares[i - 1] * product
            sum %= self.prime
        return recombination_vector, sum

    def _extended_gcd(self, a, b):
        x = 0
        last_x = 1
        y = 1
        last_y = 0
        while b != 0:
            quot = a // b
            a, b = b, a % b
            x, last_x = last_x - quot * x, x
            y, last_y = last_y - quot * y, y
        return last_x, last_y

    def divmod(self, num, den, p):
        inv, _ = self._extended_gcd(den, p)
        res = num * inv
        return res

    def eval_poly(self, poly, x):
        result = 0
        power = 0
        for coefficient in poly:
            result += coefficient * (x ** power)
            result %= self.prime
            power += 1
        return result

    def consistency_test(self):
        poly, shares = self.create_poly_and_shares(secret=4, degree=2, shares=5)
        print("poly: \n", poly)
        print("shares: \n", shares)
        print(self.eval_poly(shares[3], 4))
        print(self.eval_poly(shares[4], 3))
        print(self.eval_poly(shares[1], 0))
        print(self.eval_poly(shares[0], 1))
        print(self.eval_poly(shares[2], 0))
        print(self.eval_poly(shares[0], 2))

    def addition(self, a, b):
        t = 2
        n = 4
        # input sharing
        poly_a, shares_a = self.create_poly_and_shares(a, degree=t, shares=n)
        poly_b, shares_b = self.create_poly_and_shares(b, degree=t, shares=n)
        shares_a_0 = shares_a[:, 0]
        shares_b_0 = shares_b[:, 0]
        # addition
        add_shares = [shares_a_0[x] + shares_b_0[x] for x in range(0, n)]
        # output reconstruction
        y = add_shares
        print("poly a\n", poly_a)
        print("shares a\n", shares_a)
        print("shares a 0\n", shares_a_0, "\n")

        print("poly b\n", poly_b)
        print("shares b\n", shares_b)
        print("shares b 0\n", shares_b_0, "\n")

        print("add shares\n", y[1:])
        print(self.lagrange_interpolate(y[1:])[1])






