import random
import numpy as np

class Polynomials:

    prime = 47
    prime = 1069
    prime = 2 ** 127 - 1
    prime = 110503


    def create_poly_and_shares(self, secret, degree, shares):
        if (degree > shares or degree < 1):
            raise ValueError('shares must be lager than degree and degree must be higher than one')
        poly = [random.SystemRandom().randint(1, self.prime) for i in range(degree + 1)]
        poly[0] = secret
        shares = [self.eval_poly(poly, x) for x in range(1, shares + 1)]
        return poly, shares

    # bivariate: poly with two variable f(x,y)
    # symetric: f(x1, x2, ..) = f(y1, y2, ..)
    # f(X, Y) = 3*(x2*y2) + 92*(x+y) + 10
    def create_poly_and_shares_bi(self, secret, degree, shares):
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

    def mult_invers(self, number):
        return self._extended_gcd(number, self.prime)[0]