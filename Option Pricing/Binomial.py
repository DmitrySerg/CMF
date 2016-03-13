# -*- coding: utf-8 -*-
"""
Created on Thu Mar  3 18:58:20 2016

@author: Auditore
"""

from math import exp

class Option(object):
    def __init__(self, CallPut, AmerEur, S, X, T, r, b, v, n): 
        self.CallPut = CallPut
        self.AmerEur = AmerEur
        self.S = S
        self.X = X
        self.T = T   # option maturity
        self.r = r
        self.v = v   # constant volatility
        self.n = n   # time steps
        self.b = b        
        
    def price(self):
        if self.CallPut == 'Call':
            z = 1
        else:
            z = -1
        
        dt = self.T/self.n
        u = exp(self.v * dt ** 0.5)
        d = 1 / u
        p = (exp(self.b * dt) - d) / (u - d)
        Df = exp(-self.r * dt)
        
        for i in range(0, self.n):
            OptionValue[i] = max(0, z * (self.S * (u ** i) * d ** (self.n - i) - self.X))
            
        for j in range(self.n-1, 0, -1):
            for i in range(0, j):
                if self.AmerEur == "European":
                    OptionValue[i] = (p * OptionValue[i+1] + (1 - p) * OptionValue[i]) * Df
                else:
                    OptionValue[i] = max((z * (self.S * (u ** i) * d ** (j - i) - self.X)),
                                            (p * OptionValue[i+1] + (1-p * OptionValue[i])) * Df)
            if j == 2:
                ReturnValue[2] = ((OptionValue[2] - OptionValue[1]) / (self.S * u ** 2 - self.S) - (OptionValue[1] -OptionValue[0]) / (self.S - self.S * d ** 2)) / (0.5 * (self.S * u ** 2 - self.S * d ** 2))
                ReturnValue[3] = OptionValue[1]
            elif j == 1:
                ReturnValue[1] = (OptionValue[1] - OptionValue[0])/ (self.S * u - self.S * d)
        
        ReturnValue[3] = (ReturnValue[3] - OptionValue[0]) / (2 * dt) / 365
        ReturnValue[0] = OptionValue[0]

        self.Price = ReturnValue[0]
        self.Delta = ReturnValue[1]
        self.Gamma = ReturnValue[2]
        self.Theta = ReturnValue[3]

#               (CallPut, AmerEur, S, X, T, r, b, v, n)
option = Option('Call', 'European', 100, 105, 1, 0.02, 0.03, 0.3, 10)
OptionValue = [0]*option.n
ReturnValue = [0]*4
option.price()

print('================')
print('Price: ', str(round(option.Price, 5)))
print('Delta: ', str(round(option.Delta, 5)))
print('Gamma: ', str(round(option.Gamma, 5)))
print('Theta: ', str(round(option.Theta, 5)))
print('================')
