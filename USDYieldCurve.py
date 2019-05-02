# -*- coding: utf-8 -*-
"""
Created on Mon Apr  1 06:24:51 2019

@author: kl
"""
import os
import sys
import matplotlib.pyplot as plt
import numpy as np
import datetime
import time
import math
import calendar
from dateutil.relativedelta import relativedelta

class  USDYieldCurve():
    
    def __init__(self,*args):
        if len(args)!=4:
            print("Cannot build curve from given inputs")
            sys.exit(0)
        else:
                deporates=[]
                with open (args[0],'r') as f:
                    for line in f:
                        line=line.strip('\n')
                        deporates.append(list(map( str,line.split('\t'))))
                #print(deporates)
                
                futuresprices=[]
                with open (args[1],'r') as f:
                    for line in f:
                        line=line.strip('\n')
                        if line:
                            futuresprices.append(list(map( str,line.split('\t'))))
                #print(futuresprices)
                self.futures=futuresprices
                
                
                with open (args[2],'r') as f:
                    for row in f:
                        ymd = row.strip().split('-')
                        trade_date = datetime.date(int(ymd[0]),int(ymd[1]),int(ymd[2]))
                self.spot_date_0=trade_date+relativedelta(days=2)
                #print(trade_date)
                
                
                calendardate=[]
                with open (args[3],'r') as f:
                    for line in f:
                        line=line.strip('\n')
                        calendardate.append(list(map( str,line.split('\t'))))
                #print(calendardate)
                self.holiday_calendar=calendardate
                             
                
                deporatesdate=[]
                deporatesdate.append(self.spot_date_0)
                for i in range (0,len(deporates)):
                    a=deporates[i][0] 
                    if a[4]=='M':
                        deporatesdate.append(self.getBussinessDate(self.spot_date_0+relativedelta(months=int(a[3]))))
                    if a[4]=='D':
                        deporatesdate.append(self.getBussinessDate(self.spot_date_0+datetime.timedelta(int(a[3]))))
                    if a[4]=='W':
                        deporatesdate.append(self.getBussinessDate(self.spot_date_0+datetime.timedelta(7*int(a[3]))))
                self.deporates_date=deporatesdate 
                
                
    
                datefutures=[]
                dic={'H':3,'M':6,'U':9,'Z':12}
                for i in range (0,len(futuresprices)):
                    a=futuresprices[i][0]   
                    year=2010+int(a[3])
                    month=dic[a[2]]
                    if datetime.date(year, month, 1).weekday() == 3:
                        datefutures.append(calendar.Calendar(4).monthdatescalendar(year, month)[3][5])
                    else:
                        datefutures.append(calendar.Calendar(4).monthdatescalendar(year, month)[2][5])
                self.date_futures=datefutures
   
                df=[]
                dffutures=[]
                dfdepo=[]
                s=self.spot_date_0
                dfdepo.append([s,1])
                for n,li in enumerate(deporates):
                    dfdepo.append([deporatesdate[n+1],1/(1+float(li[1])*(deporatesdate[n+1]-s).days/36000)])
                
                for i in range (1,len(dfdepo)):
                    if (datefutures[0]-deporatesdate[i]).days<0 and (datefutures[0]-deporatesdate[i-1]).days>0:
                        dffutures.append([datefutures[0],math.exp(math.log(dfdepo[i-1][1])+
                                        ((datefutures[0]-deporatesdate[i-1]).days/(deporatesdate[i]-deporatesdate[i-1]).days)
                                        *(math.log(dfdepo[i][1])-math.log(dfdepo[i-1][1])))])
                        for m,ls in enumerate(futuresprices[:-1]):
                            dffutures.append([datefutures[m+1],dffutures[m][1]/(1+(100-float(ls[1]))*
                                            (datefutures[m+1]-datefutures[m]).days/100/360)])
               
                if not dffutures:                     
                    self.dffu=dffutures
                else:
                    self.dffu=dffutures
                    df=dfdepo+dffutures  
                    data=np.array(df)                         
                    data = data[data[:,0].argsort()]  
                    #print(data)
                    data=data.T
                    data_2= [round(i,9) for i in data[1]]
                    data_0=np.vstack((data[0],data_2)).T
                    print(data_0)
                    self.discount_factors=data.T
                
                
    def getBussinessDate(self,one_date):  #onedate is datetime.date,spot date
        spot_date=one_date
        while(one_date.weekday()==6 or one_date.weekday()==5 or [str(one_date)] in self.holiday_calendar):
            last_date=one_date
            one_date=one_date+datetime.timedelta(1)
            if one_date.day-last_date.day<0:
                spot_date=spot_date-datetime.timedelta(1)
                if spot_date.weekday()==6 or spot_date.weekday()==5 or [str(spot_date)] in self.holiday_calendar:
                    return spot_date-datetime.timedelta(1)
                else:
                    return spot_date
        return one_date
    
   
    
    
    def getDfToDate(self,d):                   #d is YYYY-MM-D, Computing discount factors from cash deposit rate,d is spot date not a trade date
        if not self.dffu:               # if the rates for cash LIBOR deposits are unavailable for the required maturities
            print("Insufficient LIBOR cash rate data.")
            sys.exit(0)    
    
        ymd0=d.strip().split('-')
        d=datetime.date(int(ymd0[0]), int(ymd0[1]), int(ymd0[2]))
    
        s=self.getBussinessDate( self.spot_date_0)
        dmax=s+relativedelta(months=36) 
        
        #print(d)
        if (d-s).days<0 or (d-dmax).days>0:                #compare time,d2=2M,d1=1M, get from "depoRates.txt"
            print("error massage:d is before spot date or d is after the last date for which the discount factor curve is defined.")
            sys.exit(0)
        else:  
            for i in range (1,len(self.discount_factors)):
                if (d-self.discount_factors[i][0]).days<0 and (d-self.discount_factors[i-1][0]).days>0:
                    df= math.exp(math.log(self.discount_factors[i-1][1])+
                                ((d-self.discount_factors[i-1][0]).days/(self.discount_factors[i][0]-self.discount_factors[i-1][0]).days)*
                                 (math.log(self.discount_factors[i][1])-math.log(self.discount_factors[i-1][1])))
                    df=round(df,9)
                    print(df)
                    return df    
                
    def getFwdRate(self,d_1,d_2): # two variables of dates to calculate forward rate
        if not self.dffu:               # if the rates for cash LIBOR deposits are unavailable for the required maturities
            print("Insufficient LIBOR cash rate data.")
            sys.exit(0)
       
        s=self.getBussinessDate( self.spot_date_0)
        dmax=s+relativedelta(months=36)# both of the input dates must also be less than approximately 3 years after the spot date.
        
        ymd1=d_1.strip().split('-')
        d1_date=datetime.date(int(ymd1[0]), int(ymd1[1]), int(ymd1[2]))
        
        ymd2=d_2.strip().split('-')
        d2_date=datetime.date(int(ymd2[0]), int(ymd2[1]), int(ymd2[2]))
        
       
        
        if (d1_date-s).days<0 or (d2_date-dmax).days>0:
            print("error massage:d1 is before spot date or d2 is after the last date for which the discount factor curve is defined.")
            sys.exit(0)
        elif  (d2_date-d1_date).days<0:
            print("error massage:d2 is before d1.")
            sys.exit(0)
        else:
            rf=360/(d2_date-d1_date).days*(self.getDfToDate(d_1)/self.getDfToDate(d_2)-1)
            return print('%.6f%%' % (rf* 100))