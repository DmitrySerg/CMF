# -*- coding: utf-8 -*-
"""
Created on Tue Mar 22 23:03:55 2016

@author: Dmitry Sergeyev
"""

#### This is the beginning of a long journey...

from math import log, exp
import scipy.stats
import sys


#### First of all I need a main class for options

#### Child classes inherit parent`s structure and variables

class Option:
    def __init__(self, Type, UnderlyingPrice, StrikePrice, TimeToExpiration, InterestRate, Volatility):
        self.Type = Type
        self.UnderlyingPrice = UnderlyingPrice
        self.StrikePrice = StrikePrice
        self.TimeToExpiration = TimeToExpiration
        self.InterestRate = InterestRate
        self.Volatility = Volatility

class BlackScholes(Option):
    def __init__(self, Type, UnderlyingPrice, StrikePrice, TimeToExpiration, InterestRate, Volatility, DividendYield):
        Option.__init__(self, Type, UnderlyingPrice, StrikePrice, TimeToExpiration, InterestRate, Volatility)
        self.DividendYield = DividendYield

    def Pricing(self):
        self.d1 = (log(self.UnderlyingPrice / self.StrikePrice) +
                   (self.InterestRate + self.Volatility ** 2 / 2) * self.TimeToExpiration) / (
                  self.Volatility * self.TimeToExpiration ** 0.5)
        self.d2 = self.d1 - self.Volatility * self.TimeToExpiration ** 0.5

        if self.Type == 'Call':
            self.Price = self.UnderlyingPrice * exp(-self.DividendYield * self.TimeToExpiration) * scipy.stats.norm(0,
                                                                                                                    1).cdf(
                self.d1) - self.StrikePrice * exp(-self.InterestRate * self.TimeToExpiration) * scipy.stats.norm(0,
                                                                                                                 1).cdf(
                self.d2)
        else:
            self.Price = -self.UnderlyingPrice * exp(-self.DividendYield * self.TimeToExpiration) * scipy.stats.norm(0,
                                                                                                                     1).cdf(
                -self.d1) + self.StrikePrice * exp(-self.InterestRate * self.TimeToExpiration) * scipy.stats.norm(0,
                                                                                                                  1).cdf(
                -self.d2)
        return self.Price

    def Greeks(self):
        if self.Type == 'Call':
            self.Delta = scipy.stats.norm(0, 1).cdf(self.d1)

            self.Theta = - (
            self.UnderlyingPrice * exp(-self.DividendYield * self.TimeToExpiration) * scipy.stats.norm(0, 1).pdf(
                self.d1) * self.Volatility) / (
                         2 * self.TimeToExpiration ** 0.5) - self.InterestRate * self.StrikePrice * exp(
                -self.InterestRate * self.TimeToExpiration) * scipy.stats.norm(0, 1).cdf(self.d2)

            self.Rho = self.StrikePrice * self.TimeToExpiration * exp(
                -self.InterestRate * self.TimeToExpiration) * scipy.stats.norm(0, 1).cdf(self.d2)
        else:
            self.Delta = scipy.stats.norm(0, 1).cdf(self.d1) - 1

            self.Theta = - (
            self.UnderlyingPrice * exp(-self.DividendYield * self.TimeToExpiration) * scipy.stats.norm(0, 1).pdf(
                self.d1) * self.Volatility) / (
                         2 * self.TimeToExpiration ** 0.5) + self.InterestRate * self.StrikePrice * exp(
                -self.InterestRate * self.TimeToExpiration) * scipy.stats.norm(0, 1).cdf(-self.d2)

            self.Rho = -self.StrikePrice * self.TimeToExpiration * exp(
                -self.InterestRate * self.TimeToExpiration) * scipy.stats.norm(0, 1).cdf(-self.d2)

        self.Gamma = (scipy.stats.norm(0, 1).pdf(self.d1) * exp(-self.DividendYield * self.TimeToExpiration)) / (
        self.UnderlyingPrice * self.Volatility * self.TimeToExpiration ** 0.5)
        self.Vega = self.UnderlyingPrice * exp(-self.DividendYield * self.TimeToExpiration) * (
        self.TimeToExpiration ** 0.5) * scipy.stats.norm(0, 1).pdf(self.d1)

class Binomial(Option):

    def __init__(self, Type, AmerEur, UnderlyingPrice, StrikePrice, TimeToExpiration, InterestRate, Volatility, Steps, CostOfCarry):
        Option.__init__(self, Type, UnderlyingPrice, StrikePrice, TimeToExpiration, InterestRate, Volatility)
        self.AmerEur = AmerEur
        self.Steps = Steps
        self.CostOfCarry = CostOfCarry


    def Pricing(self):
        OptionValue = [0] * self.Steps
        ReturnValue = [0] * 4
        if self.Type == 'Call':
            z = 1
        else:
            z = -1

        dt = self.TimeToExpiration / self.Steps
        u = exp(self.Volatility * dt ** 0.5)
        d = 1 / u
        p = (exp(self.CostOfCarry * dt) - d) / (u - d)
        Df = exp(-self.InterestRate * dt)

        for i in range(0, self.Steps):
            OptionValue[i] = max(0, z * (self.UnderlyingPrice * (u ** i) * d ** (self.Steps - i) - self.StrikePrice))

        for j in range(self.Steps - 1, 0, -1):
            for i in range(0, j):
                if self.AmerEur == "European":
                    OptionValue[i] = (p * OptionValue[i + 1] + (1 - p) * OptionValue[i]) * Df
                else:
                    OptionValue[i] = max((z * (self.UnderlyingPrice * (u ** i) * d ** (j - i) - self.StrikePrice)),
                                         (p * OptionValue[i + 1] + (1 - p * OptionValue[i])) * Df)
            if j == 2:
                ReturnValue[2] = ((OptionValue[2] - OptionValue[1]) / (self.UnderlyingPrice * u ** 2 - self.UnderlyingPrice) - (
                OptionValue[1] - OptionValue[0]) / (self.UnderlyingPrice - self.UnderlyingPrice * d ** 2)) / (0.5 * (self.UnderlyingPrice * u ** 2 - self.UnderlyingPrice * d ** 2))
                ReturnValue[3] = OptionValue[1]
            elif j == 1:
                ReturnValue[1] = (OptionValue[1] - OptionValue[0]) / (self.UnderlyingPrice * u - self.UnderlyingPrice * d)

        ReturnValue[3] = (ReturnValue[3] - OptionValue[0]) / (2 * dt) / 365
        ReturnValue[0] = OptionValue[0]

        self.Price = ReturnValue[0]
        self.Delta = ReturnValue[1]
        self.Gamma = ReturnValue[2]
        self.Theta = ReturnValue[3]

    def Greeks(self):
        vol_1 = self.Volatility + 0.01
        vol_2 = self.Volatility - 0.01

        option_1 = Binomial(Type, AmerEur, Uprice, Sprice, TTE / 365, IntRate / 100, vol_1, NumberSteps, CostCar / 100)
        OptionValue = [0] * option_1.Steps
        ReturnValue = [0] * 4
        option_1.Pricing()

        price_1 = option_1.Price

        option_2 = Binomial(Type, AmerEur, Uprice, Sprice, TTE / 365, IntRate / 100, vol_2, NumberSteps, CostCar / 100)
        OptionValue = [0] * option_2.Steps
        ReturnValue = [0] * 4
        option_2.Pricing()
        price_2 = option_2.Price

        self.Vega = (price_1 - price_2) / 2 * self.Volatility

        # Rho calculation
        IntRate_1 = self.InterestRate + 0.01
        IntRate_2 = self.InterestRate - 0.01

        option_1 = Binomial(Type, AmerEur, Uprice, Sprice, TTE / 365, IntRate_1, Vol / 100, NumberSteps, CostCar / 100)
        OptionValue = [0] * option_1.Steps
        ReturnValue = [0] * 4
        option_1.Pricing()
        price_1 = option_1.Price

        option_2 = Binomial(Type, AmerEur, Uprice, Sprice, TTE / 365, IntRate_2, Vol / 100, NumberSteps, CostCar / 100)
        OptionValue = [0] * option_2.Steps
        ReturnValue = [0] * 4
        option_2.Pricing()
        price_2 = option_2.Price

        self.Rho = (price_1 - price_2) / 2 * self.InterestRate

class Trinomial(Option):
    def __init__(self, Type, AmerEur, UnderlyingPrice, StrikePrice, TimeToExpiration, InterestRate, Volatility, Steps,
                 CostOfCarry):
        Option.__init__(self, Type, UnderlyingPrice, StrikePrice, TimeToExpiration, InterestRate, Volatility)
        self.AmerEur = AmerEur
        self.Steps = Steps
        self.CostOfCarry = CostOfCarry



    def Pricing(self):
        OptionValue = [0] * (2 * self.Steps + 1)
        ReturnValue = [0] * 4
        if self.Type == 'Call':
            z = 1
        else:
            z = -1

        dt = self.TimeToExpiration / self.Steps
        u = exp(self.Volatility * ((2 * dt) ** 0.5))
        d = exp(-self.Volatility * ((2 * dt) ** 0.5))
        pu = ((exp(self.CostOfCarry * dt / 2) - exp(-self.Volatility * ((dt / 2) ** 0.5))) / (
        exp(self.Volatility * ((dt / 2) ** 0.5)) - exp(-self.Volatility * ((dt / 2) ** 0.5)))) ** 2
        pd = ((exp(self.Volatility * ((dt / 2) ** 0.5)) - exp(self.CostOfCarry * dt / 2)) / (
        exp(self.Volatility * ((dt / 2) ** 0.5)) - exp(-self.Volatility * ((dt / 2) ** 0.5)))) ** 2
        pm = 1 - pu - pd
        Df = exp(-self.InterestRate * dt)

        for i in range(0, 2 * self.Steps):
            OptionValue[i] = max(0, z * (self.UnderlyingPrice * (u ** max(i - self.Steps, 0)) * (d ** max(self.Steps - i, 0)) - self.StrikePrice))
            # print(OptionValue)
        for j in range(self.Steps - 1, 0, -1):
            for i in range(0, j * 2):
                OptionValue[i] = (pu * OptionValue[i + 2] + pm * OptionValue[i + 1] + pd * OptionValue[i]) * Df

                if self.AmerEur == "American":
                    OptionValue[i] = max(z * (self.UnderlyingPrice * (u ** max(i - j, 0)) * (d ** max(j - i, 0)) - self.StrikePrice),
                                         OptionValue[i])

            if j == 1:
                ReturnValue[1] = (OptionValue[2] - OptionValue[0]) / (self.UnderlyingPrice * u - self.UnderlyingPrice * d)
                ReturnValue[2] = ((OptionValue[2] - OptionValue[1]) / (self.UnderlyingPrice * u - self.UnderlyingPrice) - (
                OptionValue[1] - OptionValue[0]) / (self.UnderlyingPrice - self.UnderlyingPrice * d)) / (0.5 * (self.UnderlyingPrice * u - self.UnderlyingPrice * d))
                ReturnValue[3] = OptionValue[1]

        ReturnValue[3] = (ReturnValue[3] - OptionValue[0]) / dt / 365
        ReturnValue[0] = OptionValue[0]

        self.Price = ReturnValue[0]
        self.Delta = ReturnValue[1]
        self.Gamma = ReturnValue[2]
        self.Theta = ReturnValue[3]

    def Greeks(self):


        # Vega calculation
        vol_1 = self.Volatility + 0.01
        vol_2 = self.Volatility - 0.01

        option_1 = Trinomial(Type, AmerEur, Uprice, Sprice, TTE / 365, IntRate / 100, vol_1, NumberSteps, CostCar / 100)
        OptionValue = [0] * (2 * option_1.Steps + 1)
        ReturnValue = [0] * 4
        option_1.Pricing()
        price_1 = option_1.Price

        option_2 = Trinomial(Type, AmerEur, Uprice, Sprice, TTE / 365, IntRate / 100, vol_2, NumberSteps, CostCar / 100)
        OptionValue = [0] * (2 * option_2.Steps + 1)
        ReturnValue = [0] * 4
        option_2.Pricing()
        price_2 = option_2.Price

        self.Vega = (price_1 - price_2) / 2 * self.Volatility

        # Rho calculation
        IntRate_1 = self.InterestRate + 0.01
        IntRate_2 = self.InterestRate - 0.01

        option_1 = Trinomial(Type, AmerEur, Uprice, Sprice, TTE / 365, IntRate_1, Vol / 100, NumberSteps, CostCar / 100)
        OptionValue = [0] * (2 * option_1.Steps + 1)
        ReturnValue = [0] * 4
        option_1.Pricing()
        price_1 = option_1.Price

        option_2 = Trinomial(Type, AmerEur, Uprice, Sprice, TTE / 365, IntRate_2, Vol / 100, NumberSteps, CostCar / 100)
        OptionValue = [0] * (2 * option_2.Steps + 1)
        ReturnValue = [0] * 4
        option_2.Pricing()
        price_2 = option_2.Price

        self.Rho = (price_1 - price_2) / 2 * self.InterestRate

class Explicit(Option):
    def __init__(self, Type, AmerEur, UnderlyingPrice, StrikePrice, TimeToExpiration, InterestRate, Volatility, Steps,
                 CostOfCarry):
        Option.__init__(self, Type, UnderlyingPrice, StrikePrice, TimeToExpiration, InterestRate, Volatility)
        self.AmerEur = AmerEur
        self.Steps = Steps
        self.CostOfCarry = CostOfCarry

    def Pricing(self):
        if self.Type == 'Call':
            z = 1
        else:
            z = -1

        dS = self.UnderlyingPrice / self.Steps
        M = int(self.StrikePrice / dS) * 2
        St = [0] * (M + 1)

        SGridPt = int(self.UnderlyingPrice / dS)
        dt = dS ** 2 / ((self.Volatility ** 2) * 4 * (self.StrikePrice ** 2))
        N = int(self.TimeToExpiration / dt) + 1

        C = [[0] * (M + 2)] * (N + 1)
        dt = self.TimeToExpiration / N
        Df = 1 / (1 + self.InterestRate * dt)

        for i in range(0, M):
            St[i] = i * dS
            C[N][i] = max(0, z * (St[i] - self.StrikePrice))

        for j in range(N - 1, 0, -1):
            for i in range(1, M - 1):
                pu = 0.5 * (self.Volatility ** 2 * i ** 2 + self.CostOfCarry * i) * dt
                pm = 1 - self.Volatility ** 2 * i ** 2 * dt
                pd = 0.5 * (self.Volatility ** 2 * i ** 2 - self.CostOfCarry * i) * dt
                C[j][i] = Df * (pu * C[j + 1][i + 1] + pm * C[j + 1][i] + pd * C[j + 1][i - 1])

            if self.AmerEur == "American":
                C[j][i] = max(z * (St[i] - self.StrikePrice), C[j][i])
            if z == 1:
                C[j][0] = 0
                C[j][M] = St[i] - self.StrikePrice
            else:
                C[j][0] = self.StrikePrice
                C[j][M] = 0
        self.Price = C[0][SGridPt]

    def Greeks(self):
        # Delta calculation
        S_1 = self.UnderlyingPrice + 0.01
        S_2 = self.UnderlyingPrice - 0.01

        option_1 = Explicit(Type, AmerEur, S_1, Sprice, TTE / 365, IntRate / 100, Vol / 100, NumberSteps, CostCar / 100)
        option_1.Pricing()
        price_1 = option_1.Price
        option_2 = Explicit(AmerEur, Type, S_2, Sprice, TTE / 365, IntRate / 100, Vol / 100, NumberSteps, CostCar / 100)
        option_2.Pricing()
        price_2 = option_2.Price

        self.Delta = (price_1 - price_2) / 2 * self.UnderlyingPrice

        # Gamma calculation
        S_1 = self.UnderlyingPrice + 0.02
        S_2 = self.UnderlyingPrice

        option_1 = Explicit(AmerEur, Type, S_1, Sprice, TTE / 365, IntRate / 100, Vol / 100, NumberSteps, CostCar / 100)
        option_1.Pricing()
        price_1 = option_1.Price
        option_2 = Explicit(AmerEur, Type, S_2, Sprice, TTE / 365, IntRate / 100, Vol / 100, NumberSteps, CostCar / 100)
        option_2.Pricing()
        price_2 = option_2.Price

        Delta_1 = (price_1 - price_2) / 2 * self.UnderlyingPrice

        S_1 = self.UnderlyingPrice
        S_2 = self.UnderlyingPrice - 0.02

        option_1 = Explicit(AmerEur, Type, S_1, Sprice, TTE / 365, IntRate / 100, Vol / 100, NumberSteps, CostCar / 100)
        option_1.Pricing()
        price_1 = option_1.Price
        option_2 = Explicit(AmerEur, Type, S_2, Sprice, TTE / 365, IntRate / 100, Vol / 100, NumberSteps, CostCar / 100)
        option_2.Pricing()
        price_2 = option_2.Price

        Delta_2 = (price_1 - price_2) / 2 * self.UnderlyingPrice

        self.Gamma = (Delta_1 - Delta_2) / 2 * self.UnderlyingPrice

        # Theta calculation
        T_1 = self.TimeToExpiration + 0.01
        T_2 = self.TimeToExpiration - 0.01

        option_1 = Explicit(AmerEur, Type, Uprice, Sprice, T_1, IntRate / 100,  Vol / 100, NumberSteps, CostCar / 100)
        option_1.Pricing()
        price_1 = option_1.Price
        option_2 = Explicit(AmerEur, Type, Uprice, Sprice, T_2, IntRate / 100, Vol / 100, NumberSteps, CostCar / 100)
        option_2.Pricing()
        price_2 = option_2.Price

        self.Theta = (price_1 - price_2) / 2 * self.TimeToExpiration

        # Vega calculation
        vol_1 = self.Volatility + 0.01
        vol_2 = self.Volatility - 0.01

        option_1 = Explicit(AmerEur, Type, Uprice, Sprice, TTE / 365, IntRate / 100, vol_1, NumberSteps, CostCar / 100)
        option_1.Pricing()
        price_1 = option_1.Price
        option_2 = Explicit(AmerEur, Type, Uprice, Sprice, TTE / 365, IntRate / 100, vol_2, NumberSteps, CostCar / 100)
        option_2.Pricing()
        price_2 = option_2.Price

        self.Vega = (price_1 - price_2) / 2 * self.Volatility

        # Rho calculation
        IntRate_1 = self.InterestRate + 0.01
        IntRate_2 = self.InterestRate - 0.01

        option_1 = Explicit(Type, AmerEur, Uprice, Sprice, TTE / 365, IntRate_1, Vol / 100, NumberSteps, CostCar / 100)
        option_1.Pricing()
        price_1 = option_1.Price
        option_2 = Explicit(Type, AmerEur, Uprice, Sprice, TTE / 365, IntRate_2, Vol / 100, NumberSteps, CostCar / 100)
        option_2.Pricing()
        price_2 = option_2.Price

        self.Rho = (price_1 - price_2) / 2 * self.InterestRate



'''
#### Creating the option object

user_model = input("Which model to use?: ")

Type = input('Enter the option Type (Call/Put): ')
AmerEur = input('Enter (American/European): ')
Uprice = float(input('Enter the Underlying Price: '))
Sprice = float(input('Enter the Strike Price: '))
TTE = float(input('Enter Time to Expiration (in days): '))
IntRate = float(input('Enter the Interest Rate (%): '))
Vol = float(input('Enter the Volatility (%): '))
if user_model == "bs":
    DivYiel = float(input('Enter the Dividend Yield (%): '))
else:
    CostCar = float(input('Enter Cost of Carry (%): '))
    NumberSteps = int(input('Enter the time steps (n): '))


#### Here we create option object after choosing the model

def which_model(model):
    if model == "bs":
        option = BlackScholes(Type, Uprice, Sprice, TTE / 365, IntRate / 100, Vol / 100, DivYiel / 100)
    elif model == "binom":
        option = Binomial(Type, AmerEur, Uprice, Sprice, TTE / 365, IntRate / 100, Vol / 100, NumberSteps, CostCar / 100)
    elif model == "trinom":
        option = Trinomial(Type, AmerEur, Uprice, Sprice, TTE / 365, IntRate / 100, Vol / 100, NumberSteps, CostCar / 100)
    else:
        option = Explicit(Type, AmerEur, Uprice, Sprice, TTE / 365, IntRate / 100, Vol / 100, NumberSteps, CostCar / 100)
    return option


option = which_model(user_model)
option.Pricing()
option.Greeks()

print('')
print('================')
print('Price: ', str(round(option.Price, 5)))
print('Delta: ', str(round(option.Delta, 5)))
print('Gamma: ', str(round(option.Gamma, 5)))
print('Theta: ', str(round(option.Theta, 5)))
print('Vega:  ', str(round(option.Vega, 5)))
print('Rho:   ', str(round(option.Rho, 5)))
print('================')
print('')
'''






#########################################
#####     Application (kind of)     #####
#########################################



from tkinter import *

user_model = ''
Type = ''
AmerEur = ''

Uprice = 0
Sprice = 0
TTE = 0
IntRate = 0
Vol = 0
DivYiel = 0
CostCar = 0
NumberSteps = 0


#### This function returns the model user chose in RadioButtons (user_model)
def get_selected():
    global user_model
    user_model = user_choice.get()
    #print(user_model)
    entries_to_show()
    return user_model


root = Tk()
root.minsize(width=750, height=500)
user_choice = StringVar()
Label(root, text="Choose a model:").grid(row=1, column=0, sticky=W)
choice1 = Radiobutton(root, text="Black-Scholes", variable=user_choice, command=get_selected, value='bs')
choice2 = Radiobutton(root, text="Binomial        ", variable=user_choice, command=get_selected, value='binom')
choice3 = Radiobutton(root, text="Trinomial       ", variable=user_choice, command=get_selected, value='trinom')
choice4 = Radiobutton(root, text="Explicit           ", variable=user_choice, command=get_selected, value='explicit')
choice1.grid(row=1, column=1, sticky=W)
choice2.grid(row=2, column=1, sticky=W)
choice3.grid(row=3, column=1, sticky=W)
choice4.grid(row=4, column=1, sticky=W)


def get_Type():
    global Type
    Type = Type_option.get()
    #print(Type)
    return Type


Type_option = StringVar()
Label(root, text="Choose option type:").grid(row=6, column=0, sticky=W)
choiceCall = Radiobutton(root, text="Call", variable=Type_option, command=get_Type, value="Call")
choicePut = Radiobutton(root, text="Put ", variable=Type_option, command=get_Type, value="Put")
choiceCall.grid(row=6, column=1, sticky=W)
choicePut.grid(row=7, column=1, sticky=W)


def get_AmerEur():
    global AmerEur
    AmerEur = AmerEur_option.get()
    #print(AmerEur)
    return AmerEur


AmerEur_option = StringVar()
Label(root, text="Choose option:").grid(row=9, column=0, sticky=W)
choiceCall = Radiobutton(root, text="American", variable=AmerEur_option, command=get_AmerEur, value="American")
choicePut = Radiobutton(root, text="European", variable=AmerEur_option, command=get_AmerEur, value="European")
choiceCall.grid(row=9, column=1, sticky=W)
choicePut.grid(row=10, column=1, sticky=W)


#### Now I want to make input fields. I really want. Like, desperately

## Underlying Price
def get_Uprice(event):
    global Uprice
    Uprice = float(entry_Uprice.get())
    #print(Uprice)
    return Uprice


Label(root, text="Enter the Underlying Price: ").grid(row=11, column=0, sticky=W)
entry_Uprice = Entry(root)
entry_Uprice.bind("<Return>", get_Uprice)
entry_Uprice.grid(row=11, column=1, sticky=W)


## Strike Price
def get_Sprice(event):
    global Sprice
    Sprice = float(entry_Sprice.get())
    #print(Sprice)
    return Sprice


Label(root, text="Enter the Strike Price: ").grid(row=12, column=0, sticky=W)
entry_Sprice = Entry(root)
entry_Sprice.bind("<Return>", get_Sprice)
entry_Sprice.grid(row=12, column=1, sticky=W)


## Time to Expiration
def get_TTE(event):
    global TTE
    TTE = float(entry_TTE.get())
    #print(TTE)
    return TTE


Label(root, text="Enter the Time to Expiration (in days): ").grid(row=13, column=0, sticky=W)
entry_TTE = Entry(root)
entry_TTE.bind("<Return>", get_TTE)
entry_TTE.grid(row=13, column=1, sticky=W)


## Interest Rate
def get_IntRate(event):
    global IntRate
    IntRate = float(entry_IntRate.get())
    #print(IntRate)
    return IntRate


Label(root, text="Enter the Interest Rate (%): ").grid(row=14, column=0, sticky=W)
entry_IntRate = Entry(root)
entry_IntRate.bind("<Return>", get_IntRate)
entry_IntRate.grid(row=14, column=1, sticky=W)


## Volatility
def get_Vol(event):
    global Vol
    Vol = float(entry_Vol.get())
    #print(Vol)
    return Vol


Label(root, text="Enter the Volatility (%): ").grid(row=15, column=0, sticky=W)
entry_Vol = Entry(root)
entry_Vol.bind("<Return>", get_Vol)
entry_Vol.grid(row=15, column=1, sticky=W)


def entries_to_show():
    if user_choice.get() == "bs":
        ## Dividend Yield
        def get_DivYiel(event):
            global DivYiel
            DivYiel = float(entry_DivYiel.get())
            #print(DivYiel)
            return DivYiel

        Label(root, text="Enter the Dividend Yield (%): ").grid(row=16, column=0, sticky=W)
        entry_DivYiel = Entry(root)
        entry_DivYiel.bind("<Return>", get_DivYiel)
        entry_DivYiel.grid(row=16, column=1, sticky=W)

        # hiding (if present) former widgets
        Label(root, text=" " * 36).grid(row=17, column=1, sticky=W)

    else:
        ## Cost of carry
        def get_CostCar(event):
            global CostCar
            CostCar = float(entry_CostCar.get())
            #print(CostCar)
            return CostCar

        Label(root, text="Enter the Cost of Carry (%): ").grid(row=16, column=0, sticky=W)
        entry_CostCar = Entry(root)
        entry_CostCar.bind("<Return>", get_CostCar)
        entry_CostCar.grid(row=16, column=1, sticky=W)

        ## Number of Steps
        def get_NumberSteps(event):
            global NumberSteps
            NumberSteps = int(entry_NumberSteps.get())
            #print(NumberSteps)
            return NumberSteps

        Label(root, text="Enter the Number of Steps (n): ").grid(row=17, column=0, sticky=W)
        entry_NumberSteps = Entry(root)
        entry_NumberSteps.bind("<Return>", get_NumberSteps)
        entry_NumberSteps.grid(row=17, column=1, sticky=W)


def which_model(model):
    if model == "bs":
        option = BlackScholes(Type, Uprice, Sprice, TTE / 365, IntRate / 100, Vol / 100, DivYiel / 100)
    elif model == "binom":
        option = Binomial(Type, AmerEur, Uprice, Sprice, TTE / 365, IntRate / 100, Vol / 100, NumberSteps,
                          CostCar / 100)
    elif model == "trinom":
        option = Trinomial(Type, AmerEur, Uprice, Sprice, TTE / 365, IntRate / 100, Vol / 100, NumberSteps,
                           CostCar / 100)
    else:
        option = Explicit(Type, AmerEur, Uprice, Sprice, TTE / 365, IntRate / 100, Vol / 100, NumberSteps,
                          CostCar / 100)
    return option


class calculate():
    def __init__(self):
        self.option = which_model(user_model)
        self.option.Pricing()
        self.option.Greeks()
        outputWindow.delete('1.0', END)
        outputWindow.insert(END, 'Price: ' + str(round(self.option.Price, 5)) + '\n')
        outputWindow.insert(END, 'Delta: ' + str(round(self.option.Delta, 5)) + '\n')
        outputWindow.insert(END, 'Gamma: ' + str(round(self.option.Gamma, 5)) + '\n')
        outputWindow.insert(END, 'Theta: ' + str(round(self.option.Theta, 5)) + '\n')
        outputWindow.insert(END, 'Vega:  ' + str(round(self.option.Vega, 5)) + '\n')
        outputWindow.insert(END, 'Rho:   ' + str(round(self.option.Rho, 5)) + '\n')
        '''
        print('')
        print('================')
        print('Price: ', str(round(self.option.Price, 5)))
        print('Delta: ', str(round(self.option.Delta, 5)))
        print('Gamma: ', str(round(self.option.Gamma, 5)))
        print('Theta: ', str(round(self.option.Theta, 5)))
        print('Vega:  ', str(round(self.option.Vega, 5)))
        print('Rho:   ', str(round(self.option.Rho, 5)))
        print('================')
        print('')
        '''

outputLabel = Label(root,text="Output Window")
outputLabel.place(x=500,y=5)
#create the output window
outputWindow = Text(root)
outputWindow.config(relief=SUNKEN, bg='white',width=20,height=6)
outputWindow.place(x=500,y=30)


Button(root, text="Calculate", command=calculate, width=25).grid(row=20, column=0, sticky=W)

Button(root, text='Quit', command=root.destroy, width=25).grid(row=20, column=10, sticky=E, pady=4)
root.mainloop()

#########################################
####         END OF THE APP          ####
#########################################
