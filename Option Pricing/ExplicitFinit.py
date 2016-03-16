# -*- coding: utf-8 -*-
"""
Created on Tue Mar  8 19:19:04 2016

@author: Auditore
"""

class DiffOption(object):
    def __init__(self, AmerEur, CallPut, S, X, T, r, b, v, M):
        self.AmerEur = AmerEur
        self.CallPut = CallPut
        self.S = S
        self.X = X
        self.T = T
        self.r = r
        self.b = b
        self.v = v
        self.M = M        
        
    def price(self):
        if self.CallPut == 'Call':
            z = 1
        else:
            z = -1
        
        dS = self.S/self.M
        M = int(self.X / dS) * 2
        St = [0] * (M+1)
        
        SGridPt = int(self.S / dS)
        dt = dS ** 2 / ((self.v ** 2) * 4 * (self.X ** 2))
        N = int(self.T / dt) + 1
        
        C = [[0] * (M+2)] * (N + 1)
        dt = self.T / N
        Df = 1 / (1 + self.r * dt)
        
        for i in range(0, M):
            St[i] = i * dS
            C[N][i] = max(0, z * (St[i] - self.X))
            
        for j in range(N-1, 0, -1):
            for i in range(1, M-1):
                pu = 0.5 * (self.v ** 2 * i ** 2 + self.b * i) * dt
                pm = 1 - self.v ** 2 * i ** 2 * dt
                pd = 0.5 * (self.v ** 2 * i ** 2 - self.b * i) * dt
                C[j][i] = Df * (pu * C[j + 1][i + 1] + pm * C[j + 1][i] + pd * C[j + 1][i - 1])
                
            if self.AmerEur == "American":
                C[j][i] = max(z * (St[i] - self.X), C[j][i])
            if z == 1:
                C[j][0] = 0
                C[j][M] = St[i] - self.X
            else:
                C[j][0] = self.X
                C[j][M] = 0
        self.Price = C[0][SGridPt]

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
            
            
    option = DiffOption(AmerEur, Type, Uprice, Sprice, TTE/365, IntRate/100, B/100, Vol/100, NumberSteps) 
    #option = DiffOption('American', 'Call', 100, 110, 0.5, 0.1, 0.1, 0.27, 30)
    option.price()
    
    
    
    # Delta calculation
    S_1 = option.S + 0.01
    S_2 = option.S - 0.01
    
    option_1 = DiffOption(AmerEur, Type, S_1, Sprice, TTE/365, IntRate/100, B/100, Vol/100, NumberSteps) 
    option_1.price()
    price_1 = option_1.Price
    option_2 = DiffOption(AmerEur, Type, S_2, Sprice, TTE/365, IntRate/100, B/100, Vol/100, NumberSteps)   
    option_2.price()
    price_2 = option_2.Price
    
    Delta = (price_1 - price_2) / 2 * option.S    
    



    # Gamma calculation
    S_1 = option.S + 0.02
    S_2 = option.S 
    
    option_1 = DiffOption(AmerEur, Type, S_1, Sprice, TTE/365, IntRate/100, B/100, Vol/100, NumberSteps) 
    option_1.price()
    price_1 = option_1.Price
    option_2 = DiffOption(AmerEur, Type, S_2, Sprice, TTE/365, IntRate/100, B/100, Vol/100, NumberSteps)   
    option_2.price()
    price_2 = option_2.Price
    
    Delta_1 = (price_1 - price_2) / 2 * option.S  
    
    S_1 = option.S 
    S_2 = option.S - 0.02
    
    option_1 = DiffOption(AmerEur, Type, S_1, Sprice, TTE/365, IntRate/100, B/100, Vol/100, NumberSteps) 
    option_1.price()
    price_1 = option_1.Price
    option_2 = DiffOption(AmerEur, Type, S_2, Sprice, TTE/365, IntRate/100, B/100, Vol/100, NumberSteps)   
    option_2.price()
    price_2 = option_2.Price
    
    Delta_2 = (price_1 - price_2) / 2 * option.S 
    
    Gamma = (Delta_1-Delta_2) / 2 * option.S

    
    # Theta calculation
    T_1 = option.T + 0.01
    T_2 = option.T - 0.01
    
    option_1 = DiffOption(AmerEur, Type, Uprice, Sprice, T_1, IntRate/100, B/100, Vol/100, NumberSteps) 
    option_1.price()
    price_1 = option_1.Price
    option_2 = DiffOption(AmerEur, Type, Uprice, Sprice, T_2, IntRate/100, B/100, Vol/100, NumberSteps) 
    option_2.price()
    price_2 = option_2.Price
    
    Theta = (price_1 - price_2) / 2 * option.T

    # Vega calculation
    vol_1 = option.v + 0.01
    vol_2 = option.v - 0.01
    
    option_1 = DiffOption(AmerEur, Type, Uprice, Sprice, TTE/365, IntRate/100, B/100, vol_1, NumberSteps)
    option_1.price()
    price_1 = option_1.Price
    option_2 = DiffOption(AmerEur, Type, Uprice, Sprice, TTE/365, IntRate/100, B/100, vol_2, NumberSteps)   
    option_2.price()
    price_2 = option_2.Price
    
    vega = (price_1 - price_2) / 2 * option.v    

    
    
    # Rho calculation
    IntRate_1 = option.r + 0.01
    IntRate_2 = option.r - 0.01    
    
    option_1 = DiffOption(Type, AmerEur, Uprice, Sprice, TTE/365, IntRate_1, B/100, Vol/100, NumberSteps) 
    option_1.price()
    price_1 = option_1.Price
    option_2 = DiffOption(Type, AmerEur, Uprice, Sprice, TTE/365, IntRate_2, B/100, Vol/100, NumberSteps) 
    option_2.price()
    price_2 = option_2.Price
    
    rho = (price_1 - price_2) / 2 * option.r
    

    
    print('')    
    print('================')
    print('Price: ', str(round(option.Price, 5)))
    print('Delta: ', str(round(Delta, 5)))
    print('Gamma: ', str(round(Gamma, 5)))
    print('Theta: ', str(round(Theta, 5)))
    print('Vega:  ', str(round(vega, 5)))
    print('Rho:   ', str(round(rho, 5)))
    print('================')
    print('')
    
    next_one = input('Do you want more? (Yes/No): ')
    if next_one.lower() == 'yes':
        continue
    else:
        break