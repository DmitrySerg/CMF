# -*- coding: utf-8 -*-
"""
Created on Thu Mar  3 14:57:27 2016

@author: Auditore
"""
from math import log, exp
import scipy.stats

class DividendOption():
    def __init__(self, Type, 
                 UnderlyingPrice,
                 StrikePrice,
                 TimeToExpiration,
                 InterestRate,
                 Volatility,
                 DividendYield):
        self.Type = Type
        self.UnderlyingPrice = UnderlyingPrice
        self.StrikePrice = StrikePrice
        self.TimeToExpiration = TimeToExpiration
        self.InterestRate = InterestRate
        self.Volatility = Volatility
        self.DividendYield = DividendYield
    
    def Pricing(self):
        self.d1 = (log(self.UnderlyingPrice/self.StrikePrice) + 
                  (self.InterestRate+self.Volatility ** 2/2) * self.TimeToExpiration)/(self.Volatility * self.TimeToExpiration ** 0.5)
        self.d2 = self.d1 - self.Volatility * self.TimeToExpiration ** 0.5

        if self.Type == 'Call':
            self.Price = self.UnderlyingPrice * exp(-self.DividendYield*self.TimeToExpiration) * scipy.stats.norm(0, 1).cdf(self.d1) - self.StrikePrice * exp(-self.InterestRate * self.TimeToExpiration) * scipy.stats.norm(0, 1).cdf(self.d2)
        else:
            self.Price = -self.UnderlyingPrice * exp(-self.DividendYield*self.TimeToExpiration)* scipy.stats.norm(0, 1).cdf(-self.d1) + self.StrikePrice * exp(-self.InterestRate * self.TimeToExpiration) * scipy.stats.norm(0, 1).cdf(-self.d2)
        return self.Price    
    
    def Greeks(self):
        if self.Type == 'Call':
            self.Delta = scipy.stats.norm(0, 1).cdf(self.d1)
            
            self.Theta = - (self.UnderlyingPrice * exp(-self.DividendYield * self.TimeToExpiration) * scipy.stats.norm(0, 1).pdf(self.d1) * self.Volatility) / (2 * self.TimeToExpiration ** 0.5) - self.InterestRate * self.StrikePrice * exp(-self.InterestRate * self.TimeToExpiration) * scipy.stats.norm(0, 1).cdf(self.d2)
        
            self.Rho = self.StrikePrice * self.TimeToExpiration * exp(-self.InterestRate * self.TimeToExpiration) * scipy.stats.norm(0, 1).cdf(self.d2)
        else:
            self.Delta = scipy.stats.norm(0, 1).cdf(self.d1) - 1
            
            self.Theta = - (self.UnderlyingPrice * exp(-self.DividendYield * self.TimeToExpiration) * scipy.stats.norm(0, 1).pdf(self.d1) * self.Volatility) / (2 * self.TimeToExpiration ** 0.5) + self.InterestRate * self.StrikePrice * exp(-self.InterestRate * self.TimeToExpiration) * scipy.stats.norm(0, 1).cdf(-self.d2)
            
            self.Rho = -self.StrikePrice * self.TimeToExpiration * exp(-self.InterestRate * self.TimeToExpiration) * scipy.stats.norm(0, 1).cdf(-self.d2)
            
        self.Gamma = (scipy.stats.norm(0, 1).pdf(self.d1) * exp(-self.DividendYield * self.TimeToExpiration)) / (self.UnderlyingPrice * self.Volatility * self.TimeToExpiration ** 0.5)
        self.Vega = self.UnderlyingPrice * exp(-self.DividendYield * self.TimeToExpiration) * (self.TimeToExpiration ** 0.5) * scipy.stats.norm(0, 1).pdf(self.d1)
        
        # Cash Greeks
        self.CashDelta = self.Delta * self.UnderlyingPrice
        self.CashGamma = self.Gamma * self.UnderlyingPrice ** 2 / 100
        self.CashTheta = self.Theta / 365
        self.CashVega = self.Vega / 100
        self.CashRho = self.Rho / 100
        
# Time to input some data
while True:
    Type = input('Enter the option Type (Call/Put): ')
    Uprice = float(input('Enter the Underlying Price: '))
    Sprice = float(input('Enter the Strike Price: '))
    TTE = float(input('Enter Time to Expiration (in days): '))
    IntRate = float(input('Enter the Interest Rate (%): '))
    Vol = float(input('Enter the Volatility (%): '))
    Div = float(input('Enter the Dividend Yield (%): '))
    
    # Creating the option object
    option = DividendOption(Type, Uprice, Sprice, TTE/365, IntRate/100, Vol/100, Div/100) 
    option.Pricing()
    option.Greeks()
    
    print('================')
    print('Price: ', str(round(option.Price, 5)))
    print('Delta: ', str(round(option.Delta, 5)))
    print('Gamma: ', str(round(option.Gamma, 5)))
    print('Theta: ', str(round(option.Theta, 5)))
    print('Vega:  ', str(round(option.Vega, 5)))
    print('Rho:   ', str(round(option.Rho, 5)))
    print(' ')
    print('Delta (Cash): ', str(round(option.CashDelta, 5)))
    print('Gamma (1%): ', str(round(option.CashGamma, 5)))
    print('Theta (1 day): ', str(round(option.Theta, 5)))
    print('Vega (1% vol shift): ', str(round(option.CashVega, 5)))
    print('Rho (1% rate shift): ', str(round(option.CashRho, 5)))
    print('================')
    
    next_one = input('Do you want more? (Yes/No): ')
    if next_one.lower() == 'yes':
        continue
    else:
        break


