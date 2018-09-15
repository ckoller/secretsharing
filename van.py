import random
import numpy as np

prime = 2**127 - 1
prime = 61

def create_shares(secret, degree, shares):
    if(degree > shares or degree < 1):
        raise ValueError('shares must be lager than degree and degree must be higher than one')
    poly = [random.SystemRandom().randint(1,prime) for i in range(degree + 1)]
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
    #output reconstruction
    y = add_shares
    print(shares_a)
    print(shares_b)
    print(y)
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
    print(prod_res)
    print(res)

#addition(5, 10)
#scalar_mult(3, 9)
#mult(3,9)
#mult(20, _extended_gcd(5, prime)[0])

def van(r, c):
    M = [ [(y ** x) for x in range(0, c) ] for y in range(1,r+1)]
    return M

def random_poly(degree):
    s = random.SystemRandom().randint(1,prime)
    poly = [random.SystemRandom().randint(1,prime) for i in range(degree + 1)]
    poly[0] = s
    return poly

def protocol_random(l):
    # step 1: t-sharing. Everyone does it
    s_poly = [random_poly(t) for x in range(0, n)]
    M = van(n,t+1)
    s_shares_t = [np.dot(M, s_poly[x]) % prime for x in range(0, n)]
    dist_shares = [[s_shares_t[x][y] for x in range(0,n)] for y in range(0,n)]
    # step 2: compute
    M_r = van(n,l)
    r = [np.dot(np.transpose(M_r), dist_shares[x]) % prime for x in range(0,n)]
    return r

def protocol_double_random(l):
    # step 1: t-sharing, 2t-sharing
    s_poly_t = [random_poly(t) for x in range(0, n)]
    s_poly_2t = [random_poly(2*t) for x in range(0, n)]
    M_t = van(n,t+1)
    M_2t = van(n,2*t+1)
    s_shares_t = [np.dot(M_t, s_poly_t[x]) % prime for x in range(0, n)]
    s_shares_2t = [np.dot(M_2t, s_poly_2t[x]) % prime for x in range(0, n)]
    dist_shares_t = [[s_shares_t[x][y] for x in range(0,n)] for y in range(0,n)]
    dist_shares_2t = [[s_shares_t[x][y] for x in range(0,n)] for y in range(0,n)]
    # step 2: compute
    M_r = van(n,l)
    r = [np.dot(np.transpose(M_r), dist_shares_t[x]) % prime for x in range(0,n)]
    R = [np.dot(np.transpose(M_r), dist_shares_2t[x]) % prime for x in range(0,n)]
    return r, R

def open(d, x):
    #1 get shares
    shares = [[x[i][j] for i in range(0,n)] for j in range(0,len(x[0]))]
    rec = [lagrange_interpolate(shares[x])[1] for x in range(0,len(x[0]))]               # larange
    return rec

def triples(l):
        r_2l = protocol_random(2*l)
        a = [r_2l[x][:len(r_2l[x])/2] for x in range(0, n)]
        b = [r_2l[x][len(r_2l[x])/2:] for x in range(0, n)]
        r, R = protocol_double_random(l)
        D = [[(a[x][y] * b[x][y] + R[x][y]) % prime for y in range(0,l)] for x in range(0,n)]
        D_open = open(2*t, D)
        c = [[(D_open[x] - r[y][x]) % prime for x in range(0,l)] for y in range(0,n)]
        return a, b, c


def mult_2(x_1,x_2):
    # preprocessing
    #Let i be the number of input gates in Circ, run Random(i) and associate
    #one t-sharing [rgid] to each (gid, inp, Pj ) inB Circ. Then send all shares of [rgid]
    #to Pj to let Pj compute rgid.
    r_input = protocol_random(2)
    r = open(t,r_input)


    print("r", r_input)
    print(r)
    a, b, c = triples(1)

    # evaluate input gate:
        # d_i = x + r
    d_1 = (x_1 + r[0]) % prime
    d_2 = (x_2 + r[1]) % prime
        # [x_i] = d - r
    input_evals = [[(d_1 - r_input[x][0]) % prime, (d_2-r_input[x][1]) % prime] for x in range(0,n)]
    # evaluate multiplication gate
        # [al] = [x1] * [a]
    alpha_share = [[(input_evals[x][0] + a[x][0]) % prime] for x in range(0,5)]
        # [be] = [x2] * [b]
    beta_share = [[(input_evals[x][1] + b[x][0]) % prime] for x in range(0,5)]

    alpha = open(2*t, alpha_share)[0]
    beta = open(2*t, beta_share)[0]

    # [x] = al*be - al*b - be*a + c
    x_share = [ [(alpha*beta - alpha*b[x][0] - beta*a[x][0] + c[x][0]) % prime] for x in range(0,n)]
    print(x_share)
    ##print(alpha_share)
    print(open(2,x_share))


n=5
t=(n-1)/2
l=n-t
print("n=", n, "t=", t, "l=", l)

mult_2(5,9)
