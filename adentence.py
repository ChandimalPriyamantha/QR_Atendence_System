from datetime import datetime


class Atendence(object):
    def markAttendance(myData):
        with open('Attendence.csv','r+') as f:
            myDataList = f.readlines()
            nameList =[]
            for line in myDataList:
                entry = line.split(',')
                nameList.append(entry[0])
            if myData not in nameList:
                now = datetime.now()
                dtString = now.strftime('%H:%M:%S')
                f.writelines(f"\n{myData},{dtString}")