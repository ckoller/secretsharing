import random
import numpy as np


prime = 2**127 - 1
# note that this is not secure, since computations are not done in a field

def create_shares(secret, degree, shares):
    if(degree > shares or degree < 1):
        raise ValueError('shares must be lager than degree and degree must be higher than one')
    poly = [random.SystemRandom().randint(1,150) for i in range(degree + 1)]
    poly[0] = secret
    shares = [eval_poly(poly, x) for x in range (1, shares + 1)]
    return poly, shares

def eval_poly(poly, x):
    result = 0
    power = 0
    for coefficient in poly:
        result += coefficient*(x**power)
        result %= prime
        power += 1
    return result

def _extended_gcd(a, b):
    x = 0
    last_x = 1
    y = 1
    last_y = 0
    while b != 0:
        quot = a // b
        a, b = b,  a%b
        x, last_x = last_x - quot * x, x
        y, last_y = last_y - quot * y, y
    return last_x, last_y

def divmod(num, den, p):
    inv, _ = _extended_gcd(den, p)
    res = num * inv
    return res

def lagrange_interpolate(shares):
    # H = sum(f(j)*product(m/(m-j)     AKA       h(X) = sum (h(i) * delta_i(X)
    if len(shares) < 2:
        raise ValueError("need at least two shares")
    sum = 0
    recombination_vector = []
    for i in range (1, len(shares) + 1):
        product = 1
        for j in range (1, len(shares) + 1):
            if(i != j):
                product *= divmod(j, j-i, prime)
                product %= prime
        recombination_vector.append(product)
        sum += shares[i-1] * product
        sum %= prime
    return recombination_vector, sum

def addition(a,b):
    t = 2
    n = 3
    #input sharing
    poly_a, shares_a = create_shares(a, degree=t, shares=n)
    poly_b, shares_b = create_shares(b, degree=t, shares=n)
    #addition
    add_shares = [shares_a[x] + shares_b[x] for x in range(0,n)]
    #output rec½onstruction
    y = add_shares
    print(lagrange_interpolate(y)[1])

def scalar_mult(a,x):
    t = 4
    n = 5
    #input sharing
    poly, shares = create_shares(x, degree=t, shares=n)
    #scalar mult
    mult = a*np.array(shares)
    #output reconstruction
    print(lagrange_interpolate(mult)[1])

def mult(a,b):
    t = 4
    n = 9
    #input sharing
    poly_a, shares_a = create_shares(a, degree=t, shares=n)
    poly_b, shares_b = create_shares(b, degree=t, shares=n)
    #computation-phase
    prod = [shares_a[x] * shares_b[x] for x in range(0,n)]
    #h=fa*fb, h(0)=ab, share [h(i], f.i]
    h_shares = [create_shares(prod[x], degree=t, shares=n)[1] for x in range(0,n)]      # create h(i) share
    dist_shares = [[h_shares[x][y] for x in range(0,n)] for y in range(0,n)]            # distribute h(i)
    rec = [lagrange_interpolate(dist_shares[x])[1] for x in range(0,t+1)]               # larange
    #output reconstruction
    _, res = lagrange_interpolate(rec)
    _, prod_res =lagrange_interpolate(prod)
    print(res)

addition(5, 10)
scalar_mult(3, 9)
mult(3,9)

mult(20, _extended_gcd(5, prime)[0])