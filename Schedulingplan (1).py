#!/usr/bin/python
# -*- coding: UTF-8 -*-
import re
import os
import tempfile
import datetime,time,copy,json,urllib2,collections,os,sys,math

class Properties:
    def __init__(self,file_name):
        self.file_name=file_name
        self.properties={}
        try:
            fopen=open(self.file_name,'r')
            for line in fopen:
                line=line.strip()
                if line.find('=') > 0 and not line.startswith('#'):
                    strs=line.split('=')
                    self.properties[strs[0].strip()]=strs[1].strip()
        except Exception as e:
            raise e
        else:
            fopen.close()

    def has_key(self, key):
        return key in self.properties

    def get(self, key, default_value=''):
        if key in self.properties:
            return self.properties[key]
        return default_value

    def put(self, key, value):
        self.properties[key] = value
        replace_property(self.file_name, key + '=.*', key + '=' + value, True)

    def parse(file_name):
        return Properties(file_name)

    def replace_property(file_name, from_regex, to_str, append_on_not_exists=True):
        tmpfile = tempfile.TemporaryFile()

        if os.path.exists(file_name):
            r_open = open(file_name, 'r')
            pattern = re.compile(r'' + from_regex)
            found = None
            for line in r_open:
                if pattern.search(line) and not line.strip().startswith('#'):
                    found = True
                    line = re.sub(from_regex, to_str, line)
                tmpfile.write(line)
            if not found and append_on_not_exists:
                tmpfile.write('\n' + to_str)
            r_open.close()
            tmpfile.seek(0)

            content = tmpfile.read()

            if os.path.exists(file_name):
                os.remove(file_name)

            w_open = open(file_name, 'w')
            w_open.write(content)
            w_open.close()
            tmpfile.close()
        else:
            print("file %s not found" % file_name)

def CheckMaterials(Materials):
    if 'NoKeyCapacity' not in Materials:
        Materials['NoKeyCapacity']=0
    if 'owner' not in Materials:
        Materials={}
        Materials['error']=900
        return Materials
    if 'path' not in Materials:
        Materials={}
        Materials['error']=901
        return Materials
    if 'equipment' in Materials:
        for i in range(len(Materials['equipment'])):
            equipmentmaterial=Materials['equipment'][i]
            if 'equipmentId' not in equipmentmaterial:
                Materials={}
                Materials['error']=902
                return Materials
    if 'worker' in Materials:
        for i in range(len(Materials['worker'])):
            workermaterial=Materials['worker'][i]
            if 'workerId' not in workermaterial:
                Materials={}
                Materials['error']=903
                return Materials
    if 'workCenter' in Materials:
        for i in range(len(Materials['workCenter'])):
            workcentermaterial=Materials['workCenter'][i]
            if 'workCenterId' not in workcentermaterial:
                Materials={}
                Materials['error']=904
                return Materials
    return Materials

def CheckSales_Order(Sales_Order):
    for i in range(len(Sales_Order['saleOrder'])):
        saleorder=Sales_Order['saleOrder'][i]

        if 'saleOrderId' not in saleorder: 
            Sales_Order={}
            Sales_Order['error']=800
            return Sales_Order

        if 'saleOrderLineId' not in saleorder: 
            Sales_Order={}
            Sales_Order['error']=801
            Sales_Order['saleOrderId']=saleorder['saleOrderId']
            return Sales_Order

        if 'quantity' not in saleorder: 
            Sales_Order={}
            Sales_Order['error']=802
            Sales_Order['saleOrderId']=saleorder['saleOrderId']
            Sales_Order['saleOrderLineId']=saleorder['saleOrderLineId']
            return Sales_Order

        if 'materialId' not in saleorder:
            Sales_Order={}
            Sales_Order['error']=803
            Sales_Order['saleOrderId']=saleorder['saleOrderId']
            Sales_Order['saleOrderLineId']=saleorder['saleOrderLineId']
            return Sales_Order

        if 'priority' not in saleorder:
            Sales_Order={}
            Sales_Order['error']=804
            Sales_Order['saleOrderId']=saleorder['saleOrderId']
            Sales_Order['saleOrderLineId']=saleorder['saleOrderLineId']
            return Sales_Order
        Sales_Order['saleOrder'][i]=copy.deepcopy(saleorder)
    return Sales_Order

def CheckBOM(BOM):
    bom=BOM['technologyFlow']
    Materialsid=[]
    contnum=0
    for i in range(len(bom)):
        if 'technologyId' not in bom[i]:
            BOM={}
            BOM['error']=702
            return BOM
        if 'materialId' not in bom[i]:
            BOM={}
            BOM['error']=700
            BOM['technologyId']=bom[i]['technologyId']
            return BOM
        if 'operation' not in bom[i]:
            BOM={}
            BOM['technologyId']=bom[i]['technologyId']
            BOM['error']=701
            return BOM
        if 'operation' in bom[i]:
            for j in range(len(bom[i]['operation'])):
                if 'operationId' not in bom[i]['operation'][j]:
                    BOM={}
                    BOM['error']=703
                    BOM['technologyId']=bom[i]['technologyId']
                    return BOM
                if 'workerIds' not in bom[i]['operation'][j]:
                    bom[i]['operation'][j]['workerIds']=[]
                if 'workTime' not in bom[i]['operation'][j]:
                    bom[i]['operation'][j]['workTime']=0.0
                if 'material' not in bom[i]['operation'][j]:
                    bom[i]['operation'][j]['material']=[]
                if 'material' in bom[i]['operation'][j]:
                    for z in range(len(bom[i]['operation'][j]['material'])):
                        if bom[i]['operation'][j]['material'][z]['materialId'] not in Materialsid:
                            Materialsid.append(bom[i]['operation'][j]['material'][z]['materialId'])
                        else:
                            bom[i]['operation'][j]['material'][z]['materialId']=copy.deepcopy(str(bom[i]['operation'][j]['material'][z]['materialId'])+'#'+str(contnum))
                            Materialsid.append(bom[i]['operation'][j]['material'][z]['materialId'])
                            contnum+=1
                        if 'consumptionRate' not in bom[i]['operation'][j]['material'][z]:
                            bom[i]['operation'][j]['material'][z]['consumptionRate']=0.0
                        if 'materialQuantity' not in bom[i]['operation'][j]['material'][z]:
                            bom[i]['operation'][j]['material'][z]['materialQuantity']=1.0
                        if 'materialId' not in bom[i]['operation'][j]['material'][z]:
                            BOM={}
                            BOM['operationId']=bom[i]['operation'][j]['operationId']
                            BOM['technologyId']=bom[i]['technologyId']
                            BOM['error']=704
                            return BOM
                        if 'materialType' not in bom[i]['operation'][j]['material'][z]:
                            BOM={}
                            BOM['operationId']=bom[i]['operation'][j]['operationId']
                            BOM['technologyId']=bom[i]['technologyId']
                            BOM['materialId']=bom[i]['operation'][j]['material'][z]['materialId']
                            BOM['error']=705
                            return BOM
                if 'workCenterId' not in bom[i]['operation'][j]:
                    BOM={}
                    BOM['technologyId']=bom[i]['technologyId']
                    BOM['operationId']=bom[i]['operation'][j]['operationId']
                    BOM['error']=706
                    return BOM
                if 'scrapRate' not in bom[i]['operation'][j]:
                    bom[i]['operation'][j]['scrapRate']=0.0
                if 'equipmentIds' not in bom[i]['operation'][j]:
                    bom[i]['operation'][j]['equipmentIds']=[]
                if 'keyCapability' not in bom[i]['operation'][j]:
                    BOM={}
                    BOM['technologyId']=bom[i]['technologyId']
                    BOM['operationId']=bom[i]['operation'][j]['operationId']
                    BOM['error']=707
                    return BOM
    BOM['technologyFlow']=copy.deepcopy(bom)
    return BOM

def CheckProduction_Calendar(Production_Calendar):
    productioncalendar=Production_Calendar['productionResource']
    for i in range(len(productioncalendar)):
        if 'equipmentId' not in productioncalendar[i] and 'workerId' not in productioncalendar[i]:
            Production_Calendar={}
            Production_Calendar['error']=600
            return Production_Calendar
        else:
            for j in range(len(productioncalendar[i]['unavailableTime'])):
                if 'beginTime' not in productioncalendar[i]['unavailableTime'][j] or 'endTime' not in productioncalendar[i]['unavailableTime'][j]:
                    if 'equipmentId' in productioncalendar[i]:
                        equipmentid=productioncalendar[i]['equipmentId']
                        Production_Calendar={}
                        Production_Calendar['equipmentId']=equipmentid
                        Production_Calendar['error']=601
                        return Production_Calendar
                    elif 'workerId' in productioncalendar[i]:
                        workerid=productioncalendar[i]['workerId']
                        Production_Calendar={}
                        Production_Calendar['workerId']=workerid
                        Production_Calendar['error']=602
                        return Production_Calendar
    return Production_Calendar



def timeStamp(timeNum):
    timeStamp=float(timeNum/1000)
    timeArray=time.localtime(timeStamp)
    otherStyleTime=time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
    return otherStyleTime

def date_timechrchuo(dt):
    timeArray=time.strptime(dt,"%Y-%m-%d %H:%M:%S")
    timestamp=int(time.mktime(timeArray)*1000)
    return timestamp

def timetosecond(self):
    T=int(self[:2])*3600+int(self[3:5])*60+int(self[6:])
    return T

def datesub(Jobstartdate,Jobfinishdate):
    d1=datetime.datetime.strptime(Jobfinishdate,'%Y-%m-%d %H:%M:%S')
    d2=datetime.datetime.strptime(Jobstartdate,'%Y-%m-%d %H:%M:%S')
    delta=d1-d2
    return delta.days

def dateaddtime(date,second):
    date=str(datetime.datetime.strptime(date,'%H:%M:%S')+datetime.timedelta(seconds=second))
    return date

def dateadddays(date,day):
    date=str(datetime.datetime.strptime(date,'%Y-%m-%d %H:%M:%S')+datetime.timedelta(days=day))
    return date

def datesubdays(date,day):
    date=str(datetime.datetime.strptime(date,'%Y-%m-%d %H:%M:%S')-datetime.timedelta(days=day))
    return date

def datecompare(date1,date2):
    tim1=time.mktime(time.strptime(date1,'%Y-%m-%d %H:%M:%S'))
    tim2=time.mktime(time.strptime(date2,'%Y-%m-%d %H:%M:%S'))
    if tim1>=tim2:
        date='true'
    else:
        date='false'
    return date

def timecompare(date1,date2):
    tim1=int(date1[:2])*3600+int(date1[3:5])*60+int(date1[6:])
    tim2=int(date2[:2])*3600+int(date2[3:5])*60+int(date2[6:])
    if tim1>=tim2:
        date='true'
    else:
        date='false'
    return date

def inttotime(l):
    for i in range(len(l)):
        t1=l[i]//3600
        t2=(l[i]%3600)//60
        t3=(l[i]%3600)%60
        t1='0'+str(t1) if t1<10 else str(t1)
        t2='0'+str(t2) if t2<10 else str(t2)
        t3='0'+str(t3) if t3<10 else str(t3)
        l[i]=t1+':'+t2+':'+t3
    return l

def insertcount(inserttime):
    U=[]
    for i in range(len(inserttime)):
        if 'available' not in  inserttime[i]:
            inserttime[i]['available']='0'
        if inserttime[i]['available']=='0':
            if 'begin' in inserttime[i]:
                sd=inserttime[i]['begin']
            elif 'beginTime' in inserttime[i]:
                sd=inserttime[i]['beginTime']
            if 'end' in inserttime[i]:
                ed=inserttime[i]['end']
            elif 'endTime' in inserttime[i]:
                ed=inserttime[i]['endTime']
            if ed[11:]=='23:59:00':
                ed=ed[:11]+'24:00:00'
            if datecompare(sd[:10]+' 00:00:00',ed[:10]+' 00:00:00')=='false':
                sdate=sd[:10]
                d={}
                d['beginTime']=sd
                d['endTime']=sd[:10]+' 24:00:00'
                d['available']='0'
                U.append(d)
                t=sd[:10]
                t=dateadddays(t+' 00:00:00',1)[:10]
                stopN=0
                while t!=ed[:10]:
                    d={}
                    d['beginTime']=t+' 00:00:00'
                    d['endTime']=t+' 24:00:00'
                    d['available']='0'
                    U.append(d)
                    t=dateadddays(t+' 00:00:00',1)[:10]
                if ed!=t+' 00:00:00':
                    d={}
                    d['beginTime']=t+' 00:00:00'
                    d['endTime']=ed
                    d['available']='0'
                    U.append(d)
            elif sd[:10]==ed[:10]:
                d={}
                d['beginTime']=sd
                d['endTime']=ed
                d['available']='0'
                U.append(d)
    return U

def Time_Occupation(k,r):
    if k[0]!=k[1]:
        for z in range(len(r)-1):
            if r[z+1]>k[0]>r[z] and z%2!=0:
                t1=r[:z+1]+[k[0]]
            elif r[z+1]>=k[0]>=r[z] and z%2==0:
                t1=r[:z+1]
            if r[z+1]>k[1]>r[z] and z%2!=0:
                t2=[k[1]]+r[z+1:]
                r=t1+t2
                break
            elif r[z+1]>=k[1]>=r[z] and z%2==0:
                t2=r[z+1:]
                r=t1+t2
                break
        if r==[0,86400]:
            r='None'
    return r

def Time_Crossing(l1):
    l2=[]
    if len(l1)>1:
        for i in range(len(l1)):
            l22=[]
            for j in range(len(l1[i])):
                k=l1[i][j]
                l22.append(int(k[0:2])*3600+int(k[3:5])*60+int(k[6:]))
            l2.append([0]+l22+[86400])
        r=[0,0,86400,86400]
        l3=l2
        if len(l3)>1:
            for i in range(len(l3)):
                for j in range(len(l3[i])-1):
                    if j%2==0:
                        k=[l3[i][j],l3[i][j+1]]
                        if k[0]!=k[1]:
                            r=Time_Occupation(k,r)
        L=[r[0]]
        for i in range(1,len(r)):
            if L!=[]:
                if r[i]==L[-1]:
                    del L[-1]
                else:
                    L.append(r[i])
            else:
                L.append(r[i])

        R=[]
        for i in range(len(L)):
            R.append(dateaddtime('00:00:00',L[i]))
        L=[]
        for i in range(len(R)-1):
            if i%2!=0:
                L.append([R[i][11:],R[i+1][11:]])
    else:
        Tlist=l1[0]
        L=[]
        for i in range(1,len(Tlist)):
            if i%2!=0:
                L.append([Tlist[i-1],Tlist[i]])
    return L

def inserttime(l1,l2,date1,date2,starttime):
    sst=copy.deepcopy(starttime)
    ll1=copy.deepcopy(l1)
    ll2=[0 for i in range(len(l2))]
    for i in range(len(l1)):
        ll1[i]=int(l1[i][:2])*3600+int(l1[i][3:5])*60+int(l1[i][6:])
    for i in range(len(l2)):
        ll2[i]=int(l2[i][:2])*3600+int(l2[i][3:5])*60+int(l2[i][6:])
    ll2=[0]+ll2+[86400]
    km=0
    starttime=int(starttime[:2])*3600+int(starttime[3:5])*60+int(starttime[6:])
    if date1==date2:
        if ll1[0]<=starttime<ll1[1]:
            ll1=[starttime,ll1[1]]
            km=1
        elif ll1[0]>=starttime:
            km=1
        elif ll1[1]<starttime:
            km=0
    else:
        km=1
    if km==1:
        ll2=Time_Occupation(ll1,ll2)
        if len(ll2)<=2:
            ll2='None'
        elif len(ll2)>2 and ll2!='None':
            ll2=inttotime(ll2)
        if ll2!='None':
            ll2=ll2[1:-1]
    else:
        ll2=l2
    starttime=copy.deepcopy(sst)
    return ll2

def BOM_Correction(BOM):
    bom=BOM['technologyFlow']
    L=[]
    for i in range(len(bom)):
        lastmaterial=bom[i]['materialId']
        twolevelprocess=bom[i]['operation']
        techId=bom[i]['technologyId']
        sorttwolevelprocess=[]
        thisprocessId=[]
        thisinputmaterial=[]
        thisoutputmaterial=[]
        nextprocessId=[]
        idsort=[]
        iddict={}
        for j in range(len(twolevelprocess)):
            if twolevelprocess[j]['operationId'] not in iddict:
                iddict[twolevelprocess[j]['operationId']]=twolevelprocess[j]
            idsort.append(j)
            if 'nextOperationId' in twolevelprocess[j]:
                nextprocessId.append(twolevelprocess[j]['nextOperationId'])
            else:
                nextprocessId.append('None')
            if 'operationId' in twolevelprocess[j]:
                thisprocessId.append(twolevelprocess[j]['operationId'])
        lastid='None'
        id_=[]
        ThisProcessId=copy.deepcopy(thisprocessId)
        NextProcessId=copy.deepcopy(nextprocessId)
        if 'None' not in NextProcessId:
            for j in range(len(NextProcessId)):
                if NextProcessId[j] not in ThisProcessId:
                    BOM={}
                    BOM['error']=102
                    BOM['technologyId']=int(bom[i]['technologyId'])
                    BOM['operationId']=int(ThisProcessId[j])
                    return BOM
            BOM={}
            BOM['error']=105
            BOM['technologyId']=int(bom[i]['technologyId'])
            return BOM
        
        else:
            p_=[nextprocessId.index('None')]
        for j in range(len(ThisProcessId)):
            t_=[]
            for k in range(len(p_)):
                id_.append(idsort[p_[k]])
                if ThisProcessId[p_[k]] in NextProcessId:
                    for z in range(len( NextProcessId)):
                        if NextProcessId[z]==ThisProcessId[p_[k]]:
                            q_=z
                            t_.append(q_)
            p_=t_
                                   
        if j!=len(ThisProcessId)-1:
            BOM={}
            BOM['error']=105
            BOM['technologyId']=int(bom[i]['technologyId'])
            return BOM
        id_.reverse()
        Twolevelprocess=[]
        for j in range(len(id_)):
            Twolevelprocess.append(twolevelprocess[id_[j]])

        for j in range(len(Twolevelprocess)):
            l={}
            l['materialId']=str(lastmaterial)+'-'+str(j)
            l['operation']=[Twolevelprocess[j]]
            l['technologyId']=techId
            if j!=len(Twolevelprocess)-1:
                r={}
                r['consumptionRate']=0.0
                r['materialType']='manufacture_material'
                r['materialId']=l['materialId']
                r['materialQuantity']=1.0
                Twolevelprocess[j+1]['material'].append(r)
            else:
                l['materialId']=lastmaterial
            L.append(l)
    BOM['technologyFlow']=L
    return BOM

def Analysis_Production_Calendar(Materials,Production_Calendar,NowTime,urlpath):
    TimeCalendarList={}
    for i in range(len(Production_Calendar['productionResource'])):
        if 'equipmentId' in Production_Calendar['productionResource'][i]:
            Production_Calendar['productionResource'][i]['equipmentId']=str(Production_Calendar['productionResource'][i]['equipmentId'])
        if 'workerId' in Production_Calendar['productionResource'][i]:
            Production_Calendar['productionResource'][i]['workerId']=str(Production_Calendar['productionResource'][i]['workerId'])
    if 'equipment' in Materials:
        for i in range(len(Materials['equipment'])):
            if 'workCenterId' in Materials['equipment'][i]:
                Materials['equipment'][i]['workCenterId']=str(Materials['equipment'][i]['workCenterId'])
            if 'equipmentId' in Materials['equipment'][i]:
                Materials['equipment'][i]['equipmentId']=str(Materials['equipment'][i]['equipmentId'])
    if 'worker' in Materials:
        for i in range(len(Materials['worker'])):
            if 'workCenterId' in Materials['worker'][i]:
                Materials['worker'][i]['workCenterId']=str(Materials['worker'][i]['workCenterId'])
            if 'workerId' in Materials['worker'][i]:
                Materials['worker'][i]['workerId']=str(Materials['worker'][i]['workerId'])
    if 'workCenter' in Materials:
        for i in range(len(Materials['workCenter'])):
            if 'calendarModelId' not in Materials['workCenter'][i]:
                Materials['workCenter'][i]['calendarModelId']='None'
            if 'workCenterId' in Materials['workCenter'][i]:
                Materials['workCenter'][i]['workCenterId']=str(Materials['workCenter'][i]['workCenterId'])

    lastdate_time=0
    if  Production_Calendar['productionResource']!=[]:
        for i in range(len(Production_Calendar['productionResource'])):
            sf=Production_Calendar['productionResource'][i]['unavailableTime']
            for j in range(len(sf)):
                if sf[j]['endTime']>lastdate_time:
                    lastdate_time=sf[j]['endTime']
                sf[j]['beginTime']=timeStamp(sf[j]['beginTime'])
                sf[j]['endTime']=timeStamp(sf[j]['endTime'])
                if sf[j]['endTime'][11:]=='00:00:00':
                    sf[j]['endTime']=datesubdays(sf[j]['endTime'],1)[:10]+' 24:00:00'
    if lastdate_time==0:
        lastdate_time=NowTime
    else:
        lastdate_time=timeStamp(lastdate_time)
    if datecompare(lastdate_time[:10]+' 00:00:00',NowTime[:10]+' 00:00:00')=='true':
        daysnum=datesub(NowTime[:10]+' 00:00:00',lastdate_time[:10]+' 00:00:00')+1
        if daysnum<500:
            daysnum=500
    else:
        daysnum=500
    pdate=NowTime[:10]
    time_=['00:00:00','24:00:00']
    dateline=[pdate]
    timeline=[time_]
    for i in range(daysnum):
        pdate=dateadddays(pdate+' 00:00:00',1)[:10]
        dateline.append(pdate)
        timeline.append(time_)
    for i in range(len(timeline[0])):
        if i%2!=0:
            if timecompare(NowTime[11:],timeline[0][i])=='false' and timecompare(NowTime[11:],timeline[0][i-1])=='true':
                timeline[0]=[NowTime[11:]]+timeline[0][i:]
    Machine_Employee_Tool_Calendar={}
    JobCenter={}
    if 'equipment' in Materials:
        for i in range(len(Materials['equipment'])):
            if 'workCenterId' in Materials['equipment'][i]:
                centerid=Materials['equipment'][i]['workCenterId']
            else:
                Materials['equipment'][i]['workCenterId']='99999'
                centerid=Materials['equipment'][i]['workCenterId']
            equipname=Materials['equipment'][i]['equipmentId']
            if centerid not in JobCenter:
                JobCenter[centerid]=[[equipname],[],'None']
            else:
                JobCenter[centerid][0].append(equipname)

    if 'worker' in Materials:
        for i in range(len(Materials['worker'])):
            if 'workCenterId' not in Materials['worker'][i]:
                Materials['worker'][i]['workCenterId']='99999'
            centerid=Materials['worker'][i]['workCenterId']
            workername=Materials['worker'][i]['workerId']
            if centerid not in JobCenter:
                JobCenter[centerid]=[[],[workername],'None']
            else:
                JobCenter[centerid][1].append(workername)
    if 'workCenter' in Materials:
        for i in range(len(Materials['workCenter'])):
            if 'calendarModelId' in Materials['workCenter'][i]:
                if Materials['workCenter'][i]['workCenterId'] in JobCenter:
                    JobCenter[Materials['workCenter'][i]['workCenterId']][2]=Materials['workCenter'][i]['calendarModelId']
                else:
                    JobCenter[Materials['workCenter'][i]['workCenterId']]=[[],[],Materials['workCenter'][i]['calendarModelId']]
            else:
                if Materials['workCenter'][i]['workCenterId'] in JobCenter:
                    JobCenter[Materials['workCenter'][i]['workCenterId']][2]='None'
                else:
                    JobCenter[Materials['workCenter'][i]['workCenterId']]=[[],[],'None']
    
    if 'worker' in Materials:
        for i in range(len(Materials['worker'])):
            if 'calendarModelId' not in Materials['worker'][i]:
                if 'workCenterId' in Materials['worker'][i]:
                    id1=Materials['worker'][i]['workCenterId']
                    if id1 in JobCenter:
                        Materials['worker'][i]['calendarModelId']=JobCenter[id1][2]
                    else:
                        Materials['worker'][i]['calendarModelId']='None'
                else:
                    Materials['worker'][i]['calendarModelId']='None'

    if 'equipment' in Materials:
        for i in range(len(Materials['equipment'])):
            if 'calendarModelId' not in Materials['equipment'][i]:
                if 'workCenterId' in Materials['equipment'][i]:
                    id1=Materials['equipment'][i]['workCenterId']
                    if id1 in JobCenter:
                        Materials['equipment'][i]['calendarModelId']=JobCenter[id1][2]
                    else:
                        Materials['equipment'][i]['calendarModelId']='None'
                else:
                    Materials['equipment'][i]['calendarModelId']='None'
                
    Rtime=copy.deepcopy(timeline)
    for key in Materials:
        if key=='equipment':
            for i in range(len(Materials['equipment'])):
                id=copy.deepcopy(Materials['equipment'][i]['equipmentId'])
                timeline=copy.deepcopy(Rtime)
                if id not in Machine_Employee_Tool_Calendar:
                    Machine_Employee_Tool_Calendar[id]=[dateline,timeline,[],Materials['equipment'][i]['calendarModelId'],0,0,0]
                    if 'workCenterId' in Materials['equipment'][i]:
                        Machine_Employee_Tool_Calendar[id][4]=Materials['equipment'][i]['workCenterId']
                    else:
                        Machine_Employee_Tool_Calendar[id][4]='99999'
                    Kpi=0
                    if Machine_Employee_Tool_Calendar[id][3]!='None':
                        if Machine_Employee_Tool_Calendar[id][3] not in TimeCalendarList:
                            payload={"cmd": "wis-basic/calendar/parseCalendarModelWithOwner","parameters": {"entity": {"calendarModelId": Machine_Employee_Tool_Calendar[id][3],"begin": str(Machine_Employee_Tool_Calendar[id][0][0]+' 00:00:00'),"end": str(Machine_Employee_Tool_Calendar[id][0][-1]+' 00:00:00'),"owner":Materials['owner']}}}
                            payload=json.dumps(payload)
                            res=urllib2.Request(urlpath, data=payload)
                            res=urllib2.urlopen(res)
                            res=res.read()
                            T_=json.loads(res)
                            if 'statusCode' in T_ and T_['statusCode']!=200:
                                Kpi=1
                            else:
                                TimeCalendarList[Machine_Employee_Tool_Calendar[id][3]]=T_
                        else:
                            T_=TimeCalendarList[Machine_Employee_Tool_Calendar[id][3]]
                        if Kpi==0:
                            NewTimeList=T_['response']['result']
                            if NewTimeList!=None:
                                NewTimeList=insertcount(NewTimeList)
                                for z in range(len(NewTimeList)):
                                    sd=NewTimeList[z]['beginTime']
                                    ed=NewTimeList[z]['endTime']
                                    date_insert=sd[:10]
                                    r=copy.deepcopy(Machine_Employee_Tool_Calendar[id][1][Machine_Employee_Tool_Calendar[id][0].index(date_insert)])
                                    k=[sd[11:],ed[11:]]
                                    if r==k:
                                        Machine_Employee_Tool_Calendar[id][1][Machine_Employee_Tool_Calendar[id][0].index(date_insert)]='None'
                                    else:
                                        if r!='None':
                                            for z in range(len(r)):
                                                r[z]=int(r[z][:2])*3600+int(r[z][3:5])*60+int(r[z][6:])
                                            for z in range(len(k)):
                                                k[z]=int(k[z][:2])*3600+int(k[z][3:5])*60+int(k[z][6:])
                                            r=[0]+r+[86400]
                                            k=Time_Occupation(k,r)
                                            if k!='None':
                                                k=k[1:-1]
                                                l_time=Machine_Employee_Tool_Calendar[id][1]
                                                point_=Machine_Employee_Tool_Calendar[id][0].index(date_insert)
                                                l_time[point_]=copy.deepcopy(inttotime(k))
                                                Machine_Employee_Tool_Calendar[id][1]=copy.deepcopy(l_time)
                                            else:
                                                Machine_Employee_Tool_Calendar[id][1][Machine_Employee_Tool_Calendar[id][0].index(date_insert)]='None'
                            else:
                                Machine_Employee_Tool_Calendar[id][1]=copy.deepcopy(timeline)
                        else:
                            Machine_Employee_Tool_Calendar[id][1]=copy.deepcopy(timeline)
                    else:
                        Machine_Employee_Tool_Calendar[id][1]=copy.deepcopy(timeline)
                    if Machine_Employee_Tool_Calendar[id][1][0]!='None':
                        if timecompare(NowTime[11:],Machine_Employee_Tool_Calendar[id][1][0][-1])=='true':
                            Machine_Employee_Tool_Calendar[id][1]=['None']+Machine_Employee_Tool_Calendar[id][1][1:]
                        elif timecompare(NowTime[11:],Machine_Employee_Tool_Calendar[id][1][0][0])=='true' and timecompare(NowTime[11:],Machine_Employee_Tool_Calendar[id][1][0][-1])=='false':
                            for z in range(1,len(Machine_Employee_Tool_Calendar[id][1][0])):
                                if timecompare(NowTime[11:],Machine_Employee_Tool_Calendar[id][1][0][z])=='false' and timecompare(NowTime[11:],Machine_Employee_Tool_Calendar[id][1][0][z-1])=='true':
                                    if z%2!=0:
                                        Machine_Employee_Tool_Calendar[id][1]=copy.deepcopy([[NowTime[11:]]+Machine_Employee_Tool_Calendar[id][1][0][z:]]+Machine_Employee_Tool_Calendar[id][1][1:])
                                        break
                                    else:
                                        Machine_Employee_Tool_Calendar[id][1]=copy.deepcopy([Machine_Employee_Tool_Calendar[id][1][0][z:]]+Machine_Employee_Tool_Calendar[id][1][1:])
                                        break
        
        if key=='worker':
            for i in range(len(Materials['worker'])):
                id=Materials['worker'][i]['workerId']
                timeline=copy.deepcopy(Rtime)
                if id not in Machine_Employee_Tool_Calendar:
                    Machine_Employee_Tool_Calendar[id]=[dateline,timeline,[],Materials['worker'][i]['calendarModelId'],0,0,0]
                    if 'workCenterId' in Materials['worker'][i]:
                            Machine_Employee_Tool_Calendar[id][4]=Materials['worker'][i]['workCenterId']
                    else:
                        Machine_Employee_Tool_Calendar[id][4]='99999'
                    Kpi=0
                    if Machine_Employee_Tool_Calendar[id][3]!='None':
                        if Machine_Employee_Tool_Calendar[id][3] not in TimeCalendarList:
                            payload={"cmd": "wis-basic/calendar/parseCalendarModelWithOwner","parameters": {"entity": {"calendarModelId": Machine_Employee_Tool_Calendar[id][3],"begin": str(Machine_Employee_Tool_Calendar[id][0][0]+' 00:00:00'),"end": str(Machine_Employee_Tool_Calendar[id][0][-1]+' 00:00:00'),"owner":Materials['owner']}}}
                            payload=json.dumps(payload)
                            res=urllib2.Request(urlpath, data=payload)
                            res=urllib2.urlopen(res)
                            res=res.read()
                            T_=json.loads(res)
                            if 'statusCode' in T_ and T_['statusCode']!=200:
                                Kpi=1
                            else:
                                TimeCalendarList[Machine_Employee_Tool_Calendar[id][3]]=T_
                        else:
                            T_=TimeCalendarList[Machine_Employee_Tool_Calendar[id][3]]
                        if Kpi==0:
                            NewTimeList=T_['response']['result']
                            if NewTimeList!=None:
                                NewTimeList=insertcount(NewTimeList)
                                for z in range(len(NewTimeList)):
                                    sd=NewTimeList[z]['beginTime']
                                    ed=NewTimeList[z]['endTime']
                                    date_insert=sd[:10]
                                    r=copy.deepcopy(Machine_Employee_Tool_Calendar[id][1][Machine_Employee_Tool_Calendar[id][0].index(date_insert)])
                                    k=[sd[11:],ed[11:]]
                                    if r==k:
                                        Machine_Employee_Tool_Calendar[id][1][Machine_Employee_Tool_Calendar[id][0].index(date_insert)]='None'
                                    else:
                                        if r!='None':
                                            for z in range(len(r)):
                                                r[z]=int(r[z][:2])*3600+int(r[z][3:5])*60+int(r[z][6:])
                                            for z in range(len(k)):
                                                k[z]=int(k[z][:2])*3600+int(k[z][3:5])*60+int(k[z][6:])
                                            r=[0]+r+[86400]
                                            k=Time_Occupation(k,r)
                                            if k!='None':
                                                k=k[1:-1]
                                                l_time=Machine_Employee_Tool_Calendar[id][1]
                                                point_=Machine_Employee_Tool_Calendar[id][0].index(date_insert)
                                                l_time[point_]=copy.deepcopy(inttotime(k))
                                                Machine_Employee_Tool_Calendar[id][1]=copy.deepcopy(l_time)
                                            else:
                                                Machine_Employee_Tool_Calendar[id][1][Machine_Employee_Tool_Calendar[id][0].index(date_insert)]='None'
                            else:
                                Machine_Employee_Tool_Calendar[id][1]=timeline
                        else:
                            Machine_Employee_Tool_Calendar[id][1]=timeline
                    else:
                        Machine_Employee_Tool_Calendar[id][1]=timeline
                    if Machine_Employee_Tool_Calendar[id][1][0]!='None':
                        if timecompare(NowTime[11:],Machine_Employee_Tool_Calendar[id][1][0][-1])=='true':
                            Machine_Employee_Tool_Calendar[id][1]=['None']+Machine_Employee_Tool_Calendar[id][1:]
                        elif timecompare(NowTime[11:],Machine_Employee_Tool_Calendar[id][1][0][0])=='true' and timecompare(NowTime[11:],Machine_Employee_Tool_Calendar[id][1][0][-1])=='false':
                            for z in range(1,len(Machine_Employee_Tool_Calendar[id][1][0])):
                                if timecompare(NowTime[11:],Machine_Employee_Tool_Calendar[id][1][0][z])=='false' and timecompare(NowTime[11:],Machine_Employee_Tool_Calendar[id][1][0][z-1])=='true':
                                    if z%2!=0:
                                        Machine_Employee_Tool_Calendar[id][1]=copy.deepcopy([[NowTime[11:]]+Machine_Employee_Tool_Calendar[id][1][0][z:]]+Machine_Employee_Tool_Calendar[id][1][1:])
                                        break
                                    else:
                                        Machine_Employee_Tool_Calendar[id][1]=copy.deepcopy([Machine_Employee_Tool_Calendar[id][1][0][z:]]+Machine_Employee_Tool_Calendar[id][1][1:])
                                        break

    if Production_Calendar['productionResource']!=[]:
        for i in range(len(Production_Calendar['productionResource'])):
            insertinformation=Production_Calendar['productionResource'][i]
            insertinformation['unavailableTime']=insertcount(insertinformation['unavailableTime'])
            if 'equipmentId' in insertinformation:
                if insertinformation['equipmentId'] in Machine_Employee_Tool_Calendar:
                    insertinformation['unavailableTime']=insertcount(insertinformation['unavailableTime'])
                    for j in range(len(insertinformation['unavailableTime'])):
                        st=insertinformation['unavailableTime'][j]['beginTime']
                        et=insertinformation['unavailableTime'][j]['endTime']
                        r=[st,et]
                        if insertinformation['unavailableTime'][j]['beginTime'][:10] in Machine_Employee_Tool_Calendar[insertinformation['equipmentId']][0]:
                            timedur=copy.deepcopy(Machine_Employee_Tool_Calendar[insertinformation['equipmentId']][1][Machine_Employee_Tool_Calendar[insertinformation['equipmentId']][0].index(insertinformation['unavailableTime'][j]['beginTime'][:10])])
                            if timedur!='None':
                                for z in range(len(timedur)):
                                    timedur[z]=int(timedur[z][:2])*3600+int(timedur[z][3:5])*60+int(int(timedur[z][6:]))
                                l_time=timedur
                                r[0]=int(r[0][11:][:2])*3600+int(r[0][11:][3:5])*60+int(r[0][11:][6:])
                                r[1]=int(r[1][11:][:2])*3600+int(r[1][11:][3:5])*60+int(r[1][11:][6:])
                                l_time=[0]+l_time+[86400]
                                km=Time_Occupation(r,l_time)
                            else:
                                km=timedur
                            if km!='None':
                                km=inttotime(km)
                                km=km[1:-1]
                            q=copy.deepcopy(Machine_Employee_Tool_Calendar[insertinformation['equipmentId']][0].index(insertinformation['unavailableTime'][j]['beginTime'][:10]))
                            l=copy.deepcopy(Machine_Employee_Tool_Calendar[insertinformation['equipmentId']][1])
                            l[q]=copy.deepcopy(km)
                            Machine_Employee_Tool_Calendar[insertinformation['equipmentId']][1]=l

            if 'workerId' in insertinformation:
                if insertinformation['workerId'] in Machine_Employee_Tool_Calendar:
                    insertinformation['unavailableTime']=insertcount(insertinformation['unavailableTime'])
                    for j in range(len(insertinformation['unavailableTime'])):
                        st=insertinformation['unavailableTime'][j]['beginTime']
                        et=insertinformation['unavailableTime'][j]['endTime']
                        r=[st,et]
                        if insertinformation['unavailableTime'][j]['beginTime'][:10] in Machine_Employee_Tool_Calendar[insertinformation['workerId']][0]:
                            timedur=copy.deepcopy(Machine_Employee_Tool_Calendar[insertinformation['workerId']][1][Machine_Employee_Tool_Calendar[insertinformation['workerId']][0].index(insertinformation['unavailableTime'][j]['beginTime'][:10])])
                            if timedur!='None':
                                for z in range(len(timedur)):
                                    timedur[z]=int(timedur[z][:2])*3600+int(timedur[z][3:5])*60+int(int(timedur[z][6:]))
                                l_time=timedur
                                r[0]=int(r[0][11:][:2])*3600+int(r[0][11:][3:5])*60+int(r[0][11:][6:])
                                r[1]=int(r[1][11:][:2])*3600+int(r[1][11:][3:5])*60+int(r[1][11:][6:])
                                l_time=[0]+l_time+[86400]
                                km=Time_Occupation(r,l_time)
                            else:
                                km=timedur
                            if km!='None':
                                km=inttotime(km)
                                km=km[1:-1]
                            q=copy.deepcopy(Machine_Employee_Tool_Calendar[insertinformation['workerId']][0].index(insertinformation['unavailableTime'][j]['beginTime'][:10]))
                            l=copy.deepcopy(Machine_Employee_Tool_Calendar[insertinformation['workerId']][1])
                            l[q]=copy.deepcopy(km)
                            Machine_Employee_Tool_Calendar[insertinformation['workerId']][1]=l
    L=[Machine_Employee_Tool_Calendar,JobCenter]
    return L

def Analysis_BOM(BOM,JobCenter):
    BOM=BOM_Correction(BOM)
    if 'error' in BOM:
        return BOM
    for i in range(len(BOM['technologyFlow'])):
        BOM['technologyFlow'][i]['materialId']=str(BOM['technologyFlow'][i]['materialId'])
        BOM['technologyFlow'][i]['technologyId']=str(BOM['technologyFlow'][i]['technologyId'])
        for j in range(len(BOM['technologyFlow'][i]['operation'])):
            if 'workCenterId' in BOM['technologyFlow'][i]['operation'][j]:
                   BOM['technologyFlow'][i]['operation'][j]['workCenterId']=str(BOM['technologyFlow'][i]['operation'][j]['workCenterId'])
            if 'material' in BOM['technologyFlow'][i]['operation'][j]:
                if BOM['technologyFlow'][i]['operation'][j]['material']!=[]:
                    for z in range(len(BOM['technologyFlow'][i]['operation'][j]['material'])):
                        if 'materialId' in BOM['technologyFlow'][i]['operation'][j]['material'][z]:
                            BOM['technologyFlow'][i]['operation'][j]['material'][z]['materialId']=str(BOM['technologyFlow'][i]['operation'][j]['material'][z]['materialId'])
                        if 'operationId' in BOM['technologyFlow'][i]['operation'][j]['material'][z]:
                            BOM['technologyFlow'][i]['operation'][j]['material'][z]['operationId']=str(BOM['technologyFlow'][i]['operation'][j]['material'][z]['operationId'])
                        if 'materialQuantity' in BOM['technologyFlow'][i]['operation'][j]['material'][z]:
                            BOM['technologyFlow'][i]['operation'][j]['material'][z]['materialQuantity']=str(BOM['technologyFlow'][i]['operation'][j]['material'][z]['materialQuantity'])
                else:
                    BOM['technologyFlow'][i]['operation'][j]['material'].append({"consumptionRate":0,"materialType":"purchase_material","materialId":"0","materialQuantity":"0"})

    production={}
    for i in range(len(BOM['technologyFlow'])):
        materialname_=BOM['technologyFlow'][i]['materialId']
        if materialname_ not in production:
            production[materialname_]=['None']
        operation_=BOM['technologyFlow'][i]['operation']
        for j in range(len(operation_)):
            u=[]
            equiplist=[]
            if 'equipmentId' not in operation_[j]:
                if str(operation_[j]['workCenterId']) not in JobCenter:
                    BOM={}
                    BOM['error']=103
                    BOM['workCenterId']=int(operation_[j]['workCenterId'])
                    return BOM
                else:
                    operation_[j]['equipmentId']=JobCenter[str(operation_[j]['workCenterId'])][0]
            for k in range(len(operation_[j]['equipmentId'])):
                equiplist.append(operation_[j]['equipmentId'][k])
            u.append(equiplist)
            workerlist=[]
            if 'workerId' not in operation_[j]:
                if str(operation_[j]['workCenterId']) not in JobCenter:
                    BOM={}
                    BOM['error']=103
                    BOM['workCenterId']=int(operation_[j]['workCenterId'])
                    return BOM
                else:
                    operation_[j]['workerId']=JobCenter[str(operation_[j]['workCenterId'])][1]
            for k in range(len(operation_[j]['workerId'])):
                workerlist.append(operation_[j]['workerId'][k])
            u.append(workerlist)
            u.append(int(operation_[j]['prepareTime']))
            u.append(int(operation_[j]['workTime']))
            u.append(int(operation_[j]['minQuantity']))
            u.append(int(operation_[j]['transferQuantity']))
            u.append(operation_[j]['material'])
            production[materialname_]+=u
            production[materialname_].append(BOM['technologyFlow'][i]['technologyId'])
            production[materialname_].append(BOM['technologyFlow'][i]['operation'][0]['operationId'])
            production[materialname_].append(operation_[j]['keyCapability'])
            production[materialname_].append(operation_[j]['scrapRate'])
            production[materialname_].append(operation_[j]['workCenterId'])
    return production

def calculatenum(T,N,num,scraprate,consumptionrate):
    materialsnum = {N:round(num*(1+scraprate[0]/100),6)}
    netmaterialsnum={N:num}
    netnum=[]
    for i in range(len(T)):
        T_={}
        netnumlist={}
        if '=' in T[i]:
            t1=T[i][:T[i].index('=')]
            if '&' in t1:
                t2=t1[:t1.index('&')]
            NUM=materialsnum[t2]
            NETNUM=netmaterialsnum[t2]
            t1=T[i][T[i].index('=')+1:]
            j=0
            while '+' in t1:
                t2=t1[:t1.index('+')]
                if '*' in t2:
                    P=float(t2[:t2.index('*')])
                    name=t2[t2.index('*')+1:]
                else:
                    P=1.0
                    name=t2
                if name not in materialsnum:
                    if i!=len(T)-1:
                        materialsnum[name]=round(NUM*P*(1+consumptionrate[i][j]/100)*(1+scraprate[i+1]/100),6)
                        T_[name]=round(NETNUM*P,6)
                        netmaterialsnum[name]=round(NETNUM*P,6)
                        if name not in netnumlist:
                            netnumlist[name]=netmaterialsnum[name]
                        else:
                            netnumlist[name]+=netmaterialsnum[name]
                    else:
                        materialsnum[name]=round(NUM*P*(1+consumptionrate[i][j]/100),6)
                        T_[name]=round(NETNUM*P,6)
                        netmaterialsnum[name]=round(NETNUM*P,6)
                        if name not in netnumlist:
                            netnumlist[name]=netmaterialsnum[name]
                        else:
                            netnumlist[name]+=netmaterialsnum[name]
                else:
                    if i!=len(T)-1:
                        materialsnum[name]=round((materialsnum[name]+NUM*(1+scraprate[i+1]/100)*P*(1+consumptionrate[i][j]/100)),6)
                        T_[name]=round((netmaterialsnum[name]+NETNUM*P),6)
                        netmaterialsnum[name]=round((netmaterialsnum[name]+NETNUM*P),6)
                        if name not in netnumlist:
                            netnumlist[name]=netmaterialsnum[name]
                        else:
                            netnumlist[name]+=netmaterialsnum[name]
                    else:
                        materialsnum[name]=round((materialsnum[name]+NUM*P*(1+consumptionrate[i][j]/100)),6)
                        T_[name]=round((netmaterialsnum[name]+NETNUM*P),6)
                        netmaterialsnum[name]=round((netmaterialsnum[name]+NETNUM*P),6)
                        if name not in netnumlist:
                            netnumlist[name]=netmaterialsnum[name]
                        else:
                            netnumlist[name]+=netmaterialsnum[name]
                j+=1
                t1=t1[t1.index('+')+1:]
            t2=t1
            if '*' in t2:
                P=float(t2[:t2.index('*')])
                name=t2[t2.index('*')+1:]
            else:
                P=1.0
                name=t2
            if name not in materialsnum:
                if i!=len(T)-1:
                    materialsnum[name]=round(NUM*P*(1+consumptionrate[i][j]/100)*(1+scraprate[i+1]/100),6)
                    T_[name]=round(NETNUM*P,6)
                    netmaterialsnum[name]=round(NETNUM*P,6)
                    if name not in netnumlist:
                        netnumlist[name]=netmaterialsnum[name]
                    else:
                        netnumlist[name]+=netmaterialsnum[name]
                else:
                    materialsnum[name]=round(NUM*P*(1+consumptionrate[i][j]/100),6)
                    T_[name]=round(NETNUM*P,6)
                    netmaterialsnum[name]=round(NETNUM*P,6)
                    if name not in netnumlist:
                        netnumlist[name]=netmaterialsnum[name]
                    else:
                        netnumlist[name]+=netmaterialsnum[name]
            else:
                if i!=len(T)-1:
                    materialsnum[name]=round((materialsnum[name]+NUM*(1+scraprate[i+1]/100)*P*(1+consumptionrate[i][j]/100)),6)
                    T_[name]=round((netmaterialsnum[name]+NETNUM*P),6)
                    netmaterialsnum[name]=round((netmaterialsnum[name]+NETNUM*P),6)
                    if name not in netnumlist:
                        netnumlist[name]=netmaterialsnum[name]
                    else:
                        netnumlist[name]+=netmaterialsnum[name]
                else:
                    materialsnum[name]=round((materialsnum[name]+NUM*P*(1+consumptionrate[i][j]/100)),6)
                    T_[name]=round((netmaterialsnum[name]+NETNUM*P),6)
                    netmaterialsnum[name]=round((netmaterialsnum[name]+NETNUM*P),6)
                    if name not in netnumlist:
                        netnumlist[name]=netmaterialsnum[name]
                    else:
                        netnumlist[name]+=netmaterialsnum[name]
        netnum.append(netnumlist)
    num=[]            
    for i in range(len(T)):
        t1=T[i][:T[i].index('=')]
        if '&' in t1:
            t2=t1[:t1.index('&')]
        else:
            t2=t1
        num.append(materialsnum[t2])
    NUM=[]
    NUM=[num,netnum]
    return NUM


def Analysis_Sales_Order(Sales_Order,production,Materials,OUTPUT,urlpath):
    Order={}
    prioritylist=[]
    Keylist=[]
    for i in range(len(Sales_Order['saleOrder'])):
        if Sales_Order['saleOrder'][i]['quantity']==0:
            Sales_Order['saleOrder'][i]=[]
    S={'saleOrder':[]}
    for i in range(len(Sales_Order['saleOrder'])):
        if Sales_Order['saleOrder'][i]!=[]:
            S['saleOrder'].append(Sales_Order['saleOrder'][i])
    Sales_Order=copy.deepcopy(S)

    if Sales_Order['saleOrder']==[]:
        Order={'error':0}
        return Order
    for i in range(len(Sales_Order['saleOrder'])):
        ordername_=str(Sales_Order['saleOrder'][i]['saleOrderId'])+'-'+str(Sales_Order['saleOrder'][i]['saleOrderLineId'])
        Keylist.append(ordername_)
        if ordername_ not in Order:
            Order[ordername_]=[[] for j in range(18)]
        Order[ordername_][0]=str(Sales_Order['saleOrder'][i]['materialId'])
        Processfunction=[]
        l=[Order[ordername_][0]]
        ConsumptionRate_=[]
        time_start=time.time()
        while l!=[]:
            for j in range(len(l)):
                if l[j] in production:
                    materiallist=production[l[j]][7]
                    Bom_=l[j]+'&'+production[l[j]][8]+'='
                    consumptionRate_=[]
                    for z in range(len(materiallist)):
                        if 'materialQuantity' not in materiallist[z]:
                            materiallist[z]['materialQuantity']='1'
                        Bom_+=materiallist[z]['materialQuantity']+'*'+materiallist[z]['materialId']+'+'
                        ki=materiallist[z]['materialQuantity']
                        kd=materiallist[z]['materialId']
                        consumptionRate_.append(materiallist[z]['consumptionRate'])
                        if materiallist[z]['materialType']=='manufacture_material':
                            l.append(materiallist[z]['materialId'])
                    ConsumptionRate_.append( consumptionRate_)
                    Bom_=Bom_[:-1]
                    Processfunction.append(Bom_)
                    del l[j]
                    break
                else:
                    del l[j]
                    break
        Order[ordername_][1]=Processfunction
        processnum=[]
        for j in range(len(Processfunction)):
            processnum.append('process'+str(len(Processfunction)-j))
        Order[ordername_][2]=processnum
        process_material={}
        for j in range(len(Processfunction)):
            information_=production[Processfunction[j][:Processfunction[j].index('&')]]
            Order[ordername_][3].append(information_[1])
            Order[ordername_][4].append(information_[2])
            Order[ordername_][5].append(information_[3])
            Order[ordername_][6].append(information_[5])
            Order[ordername_][7].append(information_[4])
            Order[ordername_][8].append(information_[6])
            Order[ordername_][12].append(information_[9])
            Order[ordername_][13].append(information_[10])
            Order[ordername_][14].append(information_[11])
            Order[ordername_][15].append(information_[12])
            Order[ordername_][16]=ConsumptionRate_
        NUM=calculatenum(Order[ordername_][1],Order[ordername_][0],Sales_Order['saleOrder'][i]['quantity'],Order[ordername_][14],Order[ordername_][16])
        Order[ordername_][17]=NUM[1]
        Order[ordername_][9]=NUM[0]
        Order[ordername_][11]=str(Sales_Order['saleOrder'][i]['priority'])
        prioritylist.append(Sales_Order['saleOrder'][i]['priority'])
    orderlist=collections.OrderedDict()
    orderlist2=[]
    time_start=time.time()
    while prioritylist!=[]:
        time_end=time.time()
        if time_end-time_start>600:
            Order={}
            Order['error']=106
            Order['saleOrder']=Sales_Order['saleOrder'][i]
            Order['saleOrderLineId']=Sales_Order['saleOrder'][i]['saleOrderLineId']
            return Order
        orderlist2.append(Keylist[prioritylist.index(max(prioritylist))])
        del Keylist[prioritylist.index(max(prioritylist))]
        del prioritylist[prioritylist.index(max(prioritylist))]
    for i in range(len(orderlist2)):
        orderlist[orderlist2[i]]=Order[orderlist2[i]]
    Order=orderlist
    return Order

def Input_Parameter_Analysis(Production_Calendar,BOM,Sales_Order,Materials,NowTime,urlpath,OUTPUT):
    L=Analysis_Production_Calendar(Materials,Production_Calendar,NowTime,urlpath)
    Machine_Employee_Tool_Calendar=L[0]
    JobCenter=L[1]
    production=Analysis_BOM(BOM,JobCenter)
    if 'error' in production:
        return production
    Order=Analysis_Sales_Order(Sales_Order,production,Materials,OUTPUT,urlpath)
    if 'error' in Order:
        L=Order
        return L
    else:
        L=[Order,Machine_Employee_Tool_Calendar,JobCenter]
    return L

def calculateplan(Production_Calendar,BOM,Sales_Order,Materials,NowTime,OUTPUT,urlpath):
    AddTimeCalendarList={}
    NoKeyCapacity=Materials['NoKeyCapacity']
    L=Input_Parameter_Analysis(Production_Calendar,BOM,Sales_Order,Materials,NowTime,urlpath,OUTPUT)
    if 'error' in L:
        OUTPUT=L
        return OUTPUT
    Order=L[0]
    Machine_Employee_Tool_Calendar=L[1]
    JobCenter=L[2]
    U=[]
    schedulingprocesscont=0
    for key in Order:
        payload={"cmd":"wis-production/scheduling/getSchedulingById","parameters":{"id":Materials['schedulingId'],"owner":Materials['owner']}}
        payload=json.dumps(payload)
        res=urllib2.Request(urlpath,data=payload)
        res=urllib2.urlopen(res)
        res=res.read()
        T_=json.loads(res)
        if 'response' in T_ and 'result' in T_['response'] and type(T_['response']['result'])=='dict' and 'statusDict' in T_['response']['result'] and T_['response']['result']['statusDict']=='stop':
            OUTPUT={}
            OUTPUT['error']=0
            return OUTPUT
        l=Order[key]
        Num=l[9]
        bominput=[]
        bomoutput=[]
        processname=[]
        for i in range(len(l[1])):
            zz=l[16][i]
            num=Num[i]
            m=l[1][i]
            m1=m[m.index('=')+1:]
            m2=m[:m.index('=')]
            z=0
            t1=[]
            if '+' not in m1:
                if '*' in m1:
                    x=m1[m1.index('*')+1:]
                    y=m1[:m1.index('*')]
                else:
                    x=m1
                    y='1'
                t1.append([x,y,zz[0]])
            else:
                for j in range(len(m1)):
                    if m1[j]=='+':
                        if '*' in m1[z:j]:
                            x=m1[z:j][m1[z:j].index('*')+1:]
                            y=m1[z:j][0:m1[z:j].index('*')]
                            if y=='':
                                y='1'
                        else:
                            x=m1[z:j]
                            y='1'
                        t1.append([x,y,zz[0]])
                        zz=zz[1:]          
                        z=j+1
                
                if '*' in m1[z:]:
                    x=m1[z:][m1[z:].index('*')+1:]
                    y=m1[z:][:m1[z:].index('*')]
                    if y=='':
                        y='1'
                else:
                    x=m1[z:]
                    y='1'
                t1.append([x,y,zz[0]])
                zz=zz[1:]
            bominput.append([t1,l[2][i]])
            t2=[]
            temid=m2[m2.index('&')+1:]
            m2=m2[:m2.index('&')]
            if '+' not in m2:
                if '*' in m2:
                    x=m2[m2.index('*')+1:]
                    y=m2[:m2.index('*')]
                else:
                    x=m2
                    y='1'
                t2.append([x,y])
            else:
                for j in range(len(m2)):
                    if m2[j]=='+':
                        if '*' in m1[z:j]:
                            x=m2[z:j][m2[z:j].index('*')+1:]
                            y=m2[z:j][0:m2[z:j].index('*')]
                        else:
                            x=m2[z:j]
                            y='1'
                        t2.append([x,y])
                        z=j+1
                if '*' in m2[z:]:
                    x=m2[z:][m2[z:].index('*')+1:]
                    y=m2[z:][z:m2[z:].index('*')]
                else:
                    x=m2[z:]
                    y='1'
                t2.append([x,y])
            bomoutput.append([t2,l[2][i],temid,num])
        production_ID=Order[key][0]
        Raw_Material=[]
        Raw_Material_num=[]
        output=[]
        output.append(production_ID)
        for i in range(len(bominput)):
            for j in range(len(bominput[i][0])):
                km=bominput[i][0][j][0]
                km_num=bominput[i][0][j][1]
                h=0
                for z in range(len(bomoutput)):
                    for f in range(len(bomoutput[z][0])):
                        if bomoutput[z][0][f][0]==km:
                            h=1
                            break
                    if h==1:
                        break
                if h==0:
                    Raw_Material.append(km)
                    Raw_Material_num.append(km_num)

        satisfy_time=[]
        for i in range(len(Raw_Material)):
            satisfy_time.append(NowTime)
        Raw_Material=[Raw_Material,satisfy_time]
        Bomoutput=copy.deepcopy(bomoutput)
        Bominput=copy.deepcopy(bominput)
        time_start=time.time()
        while Bomoutput!=[]:
            payload={"cmd":"wis-production/scheduling/getSchedulingById","parameters":{"id":Materials['schedulingId'],"owner":Materials['owner']}}
            payload=json.dumps(payload)
            res=urllib2.Request(urlpath,data=payload)
            res=urllib2.urlopen(res)
            res=res.read()
            T_=json.loads(res)
            if 'response' in T_ and 'result' in T_['response'] and type(T_['response']['result'])=='dict' and 'statusDict' in T_['response']['result'] and T_['response']['result']['statusDict']=='stop':
                OUTPUT={}
                OUTPUT['error']=0
                return OUTPUT
            stopbreak=0
            for i in range(len(Bominput)):
                num=Bomoutput[i][-1]
                hg=1
                for j in range(len(Bominput[i][0])):
                    if Bominput[i][0][j][0] not in Raw_Material[0]:
                        hg=hg*0
                    else:
                        hg=hg*1
                if hg==1:
                    Datesatic=[]
                    for z in range(len(Bominput[i][0])):
                        if Datesatic==[]:
                            Datesatic=Raw_Material[1][Raw_Material[0].index(Bominput[i][0][z][0])]
                        if datecompare(Raw_Material[1][Raw_Material[0].index(Bominput[i][0][z][0])],Datesatic)=='true':
                            Datesatic=Raw_Material[1][Raw_Material[0].index(Bominput[i][0][z][0])]
                    capcity_list=[]
                    k=l[2].index(Bominput[i][1])
                    if l[13][k]=='equipment':
                        machinecapacitylist=[]
                        keysource='equipment'
                        if l[3][k]==[]:
                            OUTPUT['error']=100
                            OUTPUT['workCenterId']=int(l[15][k])
                            return OUTPUT
                            os.exit()
                        for z in range(len(l[3][k])):
                            machinecapacitylist.append(Machine_Employee_Tool_Calendar[l[3][k][z]])
                    elif l[13][k]=='person':
                        keysource='person'
                        machinecapacitylist=[]
                        if l[4][k]==[]:
                            OUTPUT['error']=100
                            OUTPUT['workCenterId']=int(l[15][k])
                            return OUTPUT
                            os.exit()
                        for z in range(len(l[4][k])):
                            machinecapacitylist.append(Machine_Employee_Tool_Calendar[l[4][k][z]])
                    T=machinecapacitylist[0][0]
                    if Datesatic[:10] in T:
                        po=T.index(Datesatic[:10])
                        poo=copy.deepcopy(po)
                        starttime=copy.deepcopy(Datesatic[11:])
                        z=po
                        while z<len(T):
                            payload={"cmd":"wis-production/scheduling/getSchedulingById","parameters":{"id":Materials['schedulingId'],"owner":Materials['owner']}}
                            payload=json.dumps(payload)
                            res=urllib2.Request(urlpath,data=payload)
                            res=urllib2.urlopen(res)
                            res=res.read()
                            T_=json.loads(res)

                            if 'response' in T_ and 'result' in T_['response'] and type(T_['response']['result'])=='dict' and 'statusDict' in T_['response']['result'] and T_['response']['result']['statusDict']=='stop':

                                OUTPUT={}
                                OUTPUT['error']=0
                                return OUTPUT
                            if z==len(T)-1:
                                t=T[z]+' 00:00:00'
                                adddays=[]
                                for f in range(1,366):
                                    adddays.append(dateadddays(t,f)[:10])
                                sd_=adddays[0]
                                ed_=adddays[-1]
                                for vivo in Machine_Employee_Tool_Calendar:
                                    Machine_Employee_Tool_Calendar[vivo][0]=copy.deepcopy(Machine_Employee_Tool_Calendar[vivo][0]+adddays)
                                    Machine_Employee_Tool_Calendar[vivo][1]=copy.deepcopy(Machine_Employee_Tool_Calendar[vivo][1]+[['00:00:00','24:00:00'] for oppo in range(len(adddays))])
                                    Kpi=0
                                    if Machine_Employee_Tool_Calendar[vivo][3]!='None':
                                        timeID=int(Machine_Employee_Tool_Calendar[vivo][3])
                                        if timeID not in AddTimeCalendarList:
                                            payload={"cmd": "wis-basic/calendar/parseCalendarModelWithOwner","parameters": {"entity": {"calendarModelId": timeID,"begin": sd_+' 00:00:00',"end": ed_+' 00:00:00',"owner":Materials['owner']}}}
                                            payload=json.dumps(payload)
                                            res=urllib2.Request(urlpath, data=payload)
                                            res=urllib2.urlopen(res)
                                            res=res.read()
                                            T_=json.loads(res)
                                            if 'statusCode' in T_ and T_['statusCode']!=200:
                                                Kpi=1
                                            else:
                                                AddTimeCalendarList[timeID]=T_
                                        else:
                                            T_=AddTimeCalendarList[timeID]
                                        if Kpi==0:
                                            NewTimeList=T_['response']['result']
                                            if NewTimeList!=None:
                                                NewTimeList=insertcount(NewTimeList)
                                                for ss in range(len(NewTimeList)):
                                                    sd=NewTimeList[ss]['beginTime']
                                                    ed=NewTimeList[ss]['endTime']
                                                    date_insert=sd[:10]
                                                    r=Machine_Employee_Tool_Calendar[vivo][1][Machine_Employee_Tool_Calendar[vivo][0].index(date_insert)]
                                                    if sd[:10]==NowTime[:10]:
                                                        sd=NowTime
                                                    k_=[sd[11:],ed[11:]]
                                                    if r==k_:
                                                        Machine_Employee_Tool_Calendar[vivo][1][Machine_Employee_Tool_Calendar[vivo][0].index(date_insert)]='None'
                                                    else:
                                                        if r!='None':
                                                            for zz in range(len(r)):
                                                                r[zz]=int(r[zz][:2])*3600+int(r[zz][3:5])*60+int(r[zz][6:])
                                                            for zq in range(len(k_)):
                                                                k_[zq]=int(k_[zq][:2])*3600+int(k_[zq][3:5])*60+int(k_[zq][6:])
                                                            k_=Time_Occupation(k_,r)
                                                            if k_!='None':
                                                                k_=k_[1:-1]
                                                                l_time=Machine_Employee_Tool_Calendar[vivo][1]
                                                                point_=Machine_Employee_Tool_Calendar[vivo][0].index(date_insert)
                                                                l_time[point_]=copy.deepcopy(inttotime(k_))
                                                                Machine_Employee_Tool_Calendar[vivo][1]=copy.deepcopy(l_time)
                                                            else:
                                                                Machine_Employee_Tool_Calendar[vivo][1][Machine_Employee_Tool_Calendar[vivo][0].index(date_insert)]=copy.deepcopy('None')
                                    T=Machine_Employee_Tool_Calendar[vivo][0]
                                    
                                if l[13][k]=='equipment' and l[3][k]!='None':
                                    machinecapacitylist=[]
                                    keysource='equipment'
                                    for s in range(len(l[3][k])):
                                        machinecapacitylist.append(Machine_Employee_Tool_Calendar[l[3][k][s]])
                                elif l[13][k]=='person' or l[4][k]=='None':
                                    machinecapacitylist=[]
                                    keysource='person'
                                    for s in range(len(l[4][k])):
                                        machinecapacitylist.append(Machine_Employee_Tool_Calendar[l[4][k][s]])
 
                            for w in range(len(machinecapacitylist)):
                                stopbreak=0
                                time_=[]
                                mn=[]
                                if machinecapacitylist[w][1][z]!='None':
                                    time_.append(machinecapacitylist[w][1][z])
                                    for f in range(1,len(time_[0])):
                                        if f%2!=0:
                                            mn.append([time_[0][f-1],time_[0][f]])
                                if mn!=[]:
                                    for f in range(len(mn)):
                                        st=mn[f][0]
                                        et=mn[f][1]
                                        if timecompare(starttime,et)=='true' and z==poo:
                                            continue
                                        elif timecompare(starttime,et)=='false' and timecompare(starttime,st)=='true' and z==poo:
                                            st=starttime
                                        mn[f]=[st,et]
                                        timeduring=(int(et[:2])*3600+int(et[3:5])*60+int(et[6:]))-(int(st[:2])*3600+int(st[3:5])*60+int(st[6:]))
                                        if l[7][l[2].index(Bominput[i][1])]==0:
                                            n=num
                                        else:
                                            n=round(timeduring/l[7][l[2].index(Bominput[i][1])],6)
                                        if n<num:
                                            if n>=l[6][k]:
                                                num-=n
                                                r=copy.deepcopy(mn[f])
                                                fe=copy.deepcopy(machinecapacitylist[w][1])
                                                re=copy.deepcopy(inserttime(r,fe[z],T[z],T[poo],starttime))
                                                machinecapacitylist[w][1][z]=copy.deepcopy(re)
                                                v_=l[2].index(Bominput[i][1])
                                                if keysource=='equipment':
                                                    productmachine=l[3][v_][w]
                                                else:
                                                    productmachine=l[4][v_][w]
                                                endtime=T[z]+' '+et
                                                if et=='24:00:00':
                                                    endtime=dateadddays(T[z][:10]+' 00:00:00',1)
                                                U.append([key,[Bominput[i],Bomoutput[i]],n,T[z]+' '+st,endtime,productmachine,l[12][v_],machinecapacitylist[w][4]])

                                                t_k=T[z]+' '+et
                                                if et=='24:00:00':
                                                    t_k=dateadddays(T[z][:10]+' 00:00:00',1)
                                                if Bomoutput[i][0][0][0] not in Raw_Material[0]:
                                                    Raw_Material[0].append(Bomoutput[i][0][0][0])
                                                    Raw_Material[1].append(t_k)
                                                else:
                                                    ctime=Raw_Material[1][Raw_Material[0].index(Bomoutput[i][0][0][0])]
                                                    if datecompare(t_k,ctime)=='true':
                                                        Raw_Material[1][Raw_Material[0].index(Bomoutput[i][0][0][0])]=t_k
                                        else:
                                            if num>=l[6][k]:
                                                et=dateaddtime(st,math.ceil(num*l[7][l[2].index(Bominput[i][1])]))[11:]
                                                mn[f]=[st,et]
                                                v_=l[2].index(Bominput[i][1])
                                                if keysource=='equipment':
                                                    productmachine=l[3][v_][w]
                                                else:
                                                    productmachine=l[4][v_][w]
                                                endtime=T[z]+' '+et
                                                if et=='24:00:00':
                                                    endtime=dateadddays(T[z][:10]+' 00:00:00',1)
                                                U.append([key,[Bominput[i],Bomoutput[i]],num,T[z]+' '+st,endtime,productmachine,l[12][v_],machinecapacitylist[w][4]])
                                                r=copy.deepcopy(mn[f])
                                                fe=copy.deepcopy(machinecapacitylist[w][1])
                                                re=copy.deepcopy(inserttime(r,fe[z],T[z],T[poo],starttime))
                                                machinecapacitylist[w][1][z]=copy.deepcopy(re)
                                                t_k=T[z]+' '+et
                                                if et=='24:00:00':
                                                    t_k=dateadddays(T[z][:10]+' 00:00:00',1)
                                                if Bomoutput[i][0][0][0] not in Raw_Material[0]:
                                                    Raw_Material[0].append(Bomoutput[i][0][0][0])
                                                    Raw_Material[1].append(t_k)
                                                else:
                                                    ctime=Raw_Material[1][Raw_Material[0].index(Bomoutput[i][0][0][0])]
                                                    if datecompare(t_k,ctime)=='true':
                                                        Raw_Material[1][Raw_Material[0].index(Bomoutput[i][0][0][0])]=t_k
                                                del Bominput[i]
                                                del Bomoutput[i]
                                                stopbreak=1
                                        if stopbreak==1:
                                            break
                                if stopbreak==1:
                                    break

                            if keysource=='person':
                                for e in range(len(machinecapacitylist)):
                                    Machine_Employee_Tool_Calendar[l[4][k][e]]=copy.deepcopy(machinecapacitylist[e])
                            else:
                                for e in range(len(machinecapacitylist)):
                                    Machine_Employee_Tool_Calendar[l[3][k][e]]=copy.deepcopy(machinecapacitylist[e])
                            if stopbreak==1:
                                break
                            z+=1
                if stopbreak==1:
                    break
    m='None'
    OUTPUT['productionOrder']=[]
    for i in range(len(U)):
        h=U[i][0]+'-'+U[i][1][1][1]
        if h!=m:
            m=h
            zq=1
            U[i].append(str(zq))
        else:
            zq=zq+1
            U[i].append(str(zq))
        if NoKeyCapacity==0:  
            id=U[i][5]
            center=JobCenter[Machine_Employee_Tool_Calendar[id][4]]
            if id in center[0]:
                peo=center[1]
                if peo!=[]:
                    stop_n=0
                    chooseperson=[]
                    st=U[i][3]
                    et=U[i][4]
                    date_=st[:10]
                    st_=timetosecond(st[11:])
                    if et[11:]=='00:00:00':
                        et_=timetosecond('24:00:00')
                    else:
                        et_=timetosecond(et[11:])
                    selectemployee=[]
                    for j in range(len(peo)):
                        payload={"cmd":"wis-production/scheduling/getSchedulingById","parameters":{"id":Materials['schedulingId'],"owner":Materials['owner']}}
                        payload=json.dumps(payload)
                        res=urllib2.Request(urlpath,data=payload)
                        res=urllib2.urlopen(res)
                        res=res.read()
                        T_=json.loads(res)
                        if 'response' in T_ and 'result' in T_['response'] and type(T_['response']['result'])=='dict' and 'statusDict' in T_['response']['result'] and T_['response']['result']['statusDict']=='stop':
                            OUTPUT={}
                            OUTPUT['error']=0
                            return OUTPUT
                        peoinfor=copy.deepcopy(Machine_Employee_Tool_Calendar[peo[j]])
                        time_dur=copy.deepcopy(peoinfor[1][peoinfor[0].index(date_)])
                        if time_dur!='None':
                            for z in range(len(time_dur)):
                                time_dur[z]=timetosecond(time_dur[z])

                            for z in range(len(time_dur)):
                                if z%2!=0:
                                    if et_<=time_dur[z] and st_>=time_dur[z-1]:
                                        selectemployee.append(peo[j])
                    jobcount=[]
                    if selectemployee!=[]:
                        for j in range(len(selectemployee)):
                            jobcount.append(Machine_Employee_Tool_Calendar[selectemployee[j]][5])
                        po=selectemployee[jobcount.index(min(jobcount))]
                        peoinfor=copy.deepcopy(Machine_Employee_Tool_Calendar[po])
                        time_dur=copy.deepcopy(peoinfor[1][peoinfor[0].index(date_)])
                        for z in range(len(time_dur)):
                            time_dur[z]=timetosecond(time_dur[z])
                        time_dur=[0]+time_dur+[86400]
                        time_dur=Time_Occupation([st_,et_],time_dur)
                        if time_dur!='None':
                            time_dur=time_dur[1:-1]
                            time_dur=inttotime(time_dur)
                            if time_dur[0]!=time_dur[-1] and time_dur[-1]=='00:00:00':
                                time_dur[-1]='24:00:00'
                            if time_dur[0]==time_dur[-1]:
                                time_dur='None'
                        peoinfor[5]+=1
                        peoinfor[1][peoinfor[0].index(date_)]=copy.deepcopy(time_dur)
                        Machine_Employee_Tool_Calendar[po]=peoinfor
                        U[i].append(po)

                    else:
                        Overload_Index=[]
                        for z in range(len(peo)):
                            Overload_Index.append(Machine_Employee_Tool_Calendar[peo[z]][6])
                        chooseworker=peo[Overload_Index.index(min(Overload_Index))]
                        Machine_Employee_Tool_Calendar[chooseworker][6]+=1
                        U[i].append(chooseworker)
                else:
                    U[i].append(-1)

            if id in center[1]:
                peo=center[0]
                if peo!=[]:
                    stop_n=0
                    chooseperson=[]
                    st=U[i][3]
                    et=U[i][4]
                    date_=st[:10]
                    st_=timetosecond(st[11:])
                    if et[11:]=='00:00:00':
                        et_=timetosecond('24:00:00')
                    else:
                        et_=timetosecond(et[11:])
                    selectequipment=[]
                    for j in range(len(peo)):
                        peoinfor=copy.deepcopy(Machine_Employee_Tool_Calendar[peo[j]])
                        time_dur=copy.deepcopy(peoinfor[1][peoinfor[0].index(date_)])
                        if time_dur!='None':
                            for z in range(len(time_dur)):
                                time_dur[z]=timetosecond(time_dur[z])
                            for z in range(len(time_dur)):
                                if z%2!=0:
                                    if et_<=time_dur[z] and st_>=time_dur[z-1]:
                                        selectequipment.append(peo[j])
                    jobcount=[]
                    if selectequipment!=[]:
                        for j in range(len(selectequipment)):
                            jobcount.append(Machine_Employee_Tool_Calendar[selectequipment[j]][5])
                        po=selectequipment[jobcount.index(min(jobcount))]
                        peoinfor=copy.deepcopy(Machine_Employee_Tool_Calendar[po])
                        time_dur=copy.deepcopy(peoinfor[1][peoinfor[0].index(date_)])
                        for z in range(len(time_dur)):
                            time_dur[z]=timetosecond(time_dur[z])
                        time_dur=[0]+time_dur+[86400]
                        time_dur=Time_Occupation([st_,et_],time_dur)
                        if time_dur!='None':
                            time_dur=time_dur[1:-1]
                            time_dur=inttotime(time_dur)
                            if time_dur[0]!=time_dur[-1] and time_dur[-1]=='00:00:00':
                                time_dur[-1]='24:00:00'
                            if time_dur[0]==time_dur[-1]:
                                time_dur='None'
                        peoinfor[5]+=1
                        peoinfor[1][peoinfor[0].index(date_)]=copy.deepcopy(time_dur)
                        Machine_Employee_Tool_Calendar[po]=peoinfor
                        U[i].append(po)

                    else:
                        Overload_Index=[]
                        for z in range(len(peo)):
                            Overload_Index.append(Machine_Employee_Tool_Calendar[peo[z]][6])
                        chooseequipment=peo[Overload_Index.index(min(Overload_Index))]
                        Machine_Employee_Tool_Calendar[chooseequipment][6]+=1
                        U[i].append(chooseequipment)
                else:
                    U[i].append('NoEquipment')
        else:
            U[i].append(-1)
        outmaterials_=U[i][1][1][0]
        for j in range(len(outmaterials_)):
            if '-' in outmaterials_[j][0]:
                U[i][1][1][0][j][0]=U[i][1][1][0][j][0][:U[i][1][1][0][j][0].index('-')]
        l={}
        if '-' in U[i][0]:
            l['saleOrderId']=U[i][0][:U[i][0].index('-')]
            l['saleOrderLineId']=U[i][0][U[i][0].index('-')+1:]
        l['materialId']=U[i][1][1][0][0][0]
        l['quantity']=U[i][2]
        l['materialRequirement']=[]
        for j in range(len(U[i][1][0][0])):
            PROcess=U[i][1][0][1]
            ppo_=Order[U[i][0]][2].index(PROcess)
            mater_need={}
            if '#' in U[i][1][0][0][j][0]:
                U[i][1][0][0][j][0]=U[i][1][0][0][j][0][0:U[i][1][0][0][j][0].index('#')]
            if U[i][1][0][0][j][0]!="0"and U[i][1][0][0][j][0]!= l['materialId'] and '-' not in U[i][1][0][0][j][0]:
                mater_need['materialId']=U[i][1][0][0][j][0]
            else:
                mater_need['materialId']=-1
            mater_need['quantity']=round(float(U[i][1][0][0][j][1])*float(U[i][2])*(1+float(U[i][1][0][0][j][2])/100),6)
            mater_need['time']=U[i][3]
            mater_need['consumptionRate']=U[i][1][0][0][j][2]
            if mater_need['materialId']!=-1:
                l['materialRequirement'].append(mater_need)
        if l['materialRequirement']==[]:
            del l['materialRequirement']
        k_=[]
        for z in Order[U[i][0]][17][ppo_]:
            k_material={}
            if '-' in z:
                continue
            s=Order[U[i][0]][17][ppo_][z]
            if '#' in z:
                k_material['materialId']=z[0:z.index('#')]
                k_material['quantity']=s
            else:
                if z!='0':
                    k_material['materialId']=z
                    k_material['quantity']=s
            if k_material!={}:
                 k_.append(k_material)
        if k_!=[]:
            l['materialNetRequirement']=k_
        l['technologyId']=U[i][1][1][2]
        l['operationId']=U[i][6]
        l['productionTaskNumber']=U[i][8]
        l['startTime']=U[i][3]
        l['endTime']=U[i][4]
        l['workCenterId']=U[i][7]
        if U[i][5] in JobCenter[U[i][7]][0]:
            l['equipmentIds']=[U[i][5]]
        elif U[i][5] in JobCenter[U[i][7]][1]:
            l['workerIds']=[U[i][5]]
        if U[i][9] in JobCenter[U[i][7]][0]:
            l['equipmentIds']=[U[i][9]]
        elif U[i][9] in JobCenter[U[i][7]][1]:
            l['workerIds']=[U[i][9]]
        OUTPUT['productionOrder'].append(l)
    return OUTPUT

def Scheduling_Plan(Production_Calendar,BOM,Sales_Order,Materials):
    OUTPUT={}
    Production_Calendar=json.loads(Production_Calendar)
    Materials=json.loads(Materials)
    BOM=json.loads(BOM)
    Sales_Order=json.loads(Sales_Order)
    file_path=Materials['path']
    #file_path='application.properties'
    props=Properties(file_path)
    urlpath=props.get('cgi.url')
    NowTime=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    Sales_Order=CheckSales_Order(Sales_Order)
    BOM=CheckBOM(BOM)
    Materials=CheckMaterials(Materials)
    Production_Calendar=CheckProduction_Calendar(Production_Calendar)
    if 'error' in Sales_Order:
        OUTPUT=Sales_Order
        return OUTPUT
    if 'error' in BOM:
        OUTPUT=BOM
        return OUTPUT
    if 'error' in Materials:
        OUTPUT=Materials
        return OUTPUT
    if 'error' in Production_Calendar:
        OUTPUT=Production_Calendar
        return OUTPUT
    try:
        OUTPUT=calculateplan(Production_Calendar,BOM,Sales_Order,Materials,NowTime,OUTPUT,urlpath)
    except Exception as e:
        OUTPUT['error']=500
    if 'error' in OUTPUT and OUTPUT['error']==0:
        OUTPUT={'productionOrder':[]}
    OUTPUT=json.dumps(OUTPUT)
    return OUTPUT


