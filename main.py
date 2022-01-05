import cv2
import numpy as np
from pyzbar.pyzbar import decode
from datetime import datetime
import mysql.connector
import winsound




class Video(object):

    def mark_attendance(self,r,n,d):
        with open("Attendence.csv","r+",newline="\n") as f:
            myDataList=f.readlines()
            name_list=[]
            for line in myDataList:
                entry=line.split((","))
                name_list.append(entry[0])
            if((r not in name_list) and (n not in name_list) and (d not in name_list)):
                now=datetime.now()
                d1=now.strftime("%d/%m/%Y")
                dtString=now.strftime("%H:%M:%S")
                winsound.Beep(440, 500)
                f.writelines(f"\n{n},{r},{d},{dtString},{d1},Preset")
   
    def __init__(self):
        self.video=cv2.VideoCapture(0)
        
    def __del__(self):
        self.video.release()
    def get_frame(self):
        ret,frame=self.video.read()
    
        
        while True:

           
            for barcode in decode(frame):
                print(barcode.data)
                myData = barcode.data.decode('utf-8')
                print(myData)
                pts = np.array([barcode.polygon], np.int32)
                pts = pts.reshape((-1, 1, 2))
                cv2.polylines(frame, [pts], True, (0, 255, 0), 5)
                pts2 = barcode.rect
                
                conn=mysql.connector.connect(host="localhost",username="root",password="1234",database="qr_atendencedb")  
                my_cursor=conn.cursor() 


                my_cursor.execute("select name from add_student where email=%s" , [myData])
                n=my_cursor.fetchone()
                n="+".join(n)

                
                my_cursor.execute("select email from add_student where email=%s", [myData])
                r=my_cursor.fetchone()
                r="+".join(r)


                my_cursor.execute("select language from add_student where email=%s", [myData])
                d=my_cursor.fetchone()
                d="+".join(d)

                
                
                self.mark_attendance(r,n,d)
                
                cv2.putText(frame, myData+" "+"Attended", (pts2[0], pts2[1]), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
                            
               
                

            ret,jpg=cv2.imencode('.jpg',frame)
            return jpg.tobytes()

    