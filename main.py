'''
Purpose: This program is test libor yield curve functionality
Update:
Author: kl

'''

from USDYieldCurve import USDYieldCurve



def main():
    usdCurve=USDYieldCurve("depoRates.txt", "futuresPrices.txt", "tradeDate.txt", "holidayCalendar.txt")
    usdCurve.getDfToDate('2016-3-20')
    usdCurve.getFwdRate("2015-12-1", "2016-2-1")

if __name__ == '__main__':
    main()
