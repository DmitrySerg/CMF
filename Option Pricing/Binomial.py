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


while True:
    Type = input('Enter the option Type (Call/Put): ')
    AmerEur = input('Enter (American/European): ')
    Uprice = float(input('Enter the Underlying Price: '))
    Sprice = float(input('Enter the Strike Price: '))
    TTE = float(input('Enter Time to Expiration (in days): '))
    IntRate = float(input('Enter the Interest Rate (%): '))
    B = float(input('Enter b (%): '))
    Vol = float(input('Enter the Volatility (%): '))
    NumberSteps = int(input('Enter the time steps (n): '))
    
    option = Option(Type, AmerEur, Uprice, Sprice, TTE/365, IntRate/100, B/100, Vol/100, NumberSteps) 
    #option = Option('Call', 'European', 100, 105, 1, 0.02, 0.03, 0.3, 10)
    OptionValue = [0]*option.n
    ReturnValue = [0]*4
    option.price()
    
    
    # Vega calculation
    vol_1 = option.v + 0.01
    vol_2 = option.v - 0.01
    
    option_1 = Option(Type, AmerEur, Uprice, Sprice, TTE/365, IntRate/100, B/100, vol_1, NumberSteps)
    OptionValue = [0]*option_1.n
    ReturnValue = [0]*4
    option_1.price()
    price_1 = option_1.Price
     
    option_2 = Option(Type, AmerEur, Uprice, Sprice, TTE/365, IntRate/100, B/100, vol_2, NumberSteps)   
    OptionValue = [0]*option_2.n
    ReturnValue = [0]*4
    option_2.price()
    price_2 = option_2.Price
    
    vega = (price_1 - price_2) / 2 * option.v
    
    
    # Rho calculation
    IntRate_1 = option.r + 0.01
    IntRate_2 = option.r - 0.01    
    
    option_1 = Option(Type, AmerEur, Uprice, Sprice, TTE/365, IntRate_1, B/100, Vol/100, NumberSteps) 
    OptionValue = [0]*option_1.n
    ReturnValue = [0]*4
    option_1.price()
    price_1 = option_1.Price
    
    option_2 = Option(Type, AmerEur, Uprice, Sprice, TTE/365, IntRate_2, B/100, Vol/100, NumberSteps) 
    OptionValue = [0]*option_2.n
    ReturnValue = [0]*4
    option_2.price()
    price_2 = option_2.Price
    
    rho = (price_1 - price_2) / 2 * option.r
    
    print('================')
    print('Price: ', str(round(option.Price, 5)))
    print('Delta: ', str(round(option.Delta, 5)))
    print('Gamma: ', str(round(option.Gamma, 5)))
    print('Theta: ', str(round(option.Theta, 5)))
    print('Vega:  ', str(round(vega, 5)))
    print('Rho:   ', str(round(rho, 5)))
    print('================')
    next_one = input('Do you want more? (Yes/No): ')
    if next_one.lower() == 'yes':
        continue
    else:
        break
