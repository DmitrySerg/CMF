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
        self.ExplFinDif = C[0][SGridPt]
        
#                   (AmerEur, CallPut, S, X, T, r, b, v, M)
option = DiffOption('American', 'Call', 100, 110, 0.5, 0.1, 0.1, 0.27, 30)
option.price()