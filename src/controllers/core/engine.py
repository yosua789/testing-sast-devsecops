import os,subprocess
import requests
from typing import Optional, Any


from dotenv import load_dotenv
from models import *

class GoaccessEngine():

    def __init__(self):
        load_dotenv(dotenv_path="/home/kecilin/src")

        self.respone_path = os.getenv("RES_LOG_PATH")
        self.log_path = os.getenv("LOG_PATH")

        try:
            self.duration = int(os.getenv("DURATION")) if os.getenv("DURATION") else 30
        except Exception as e:
            self.duration = 30

    # def run(self):
    def getGoaccess(self):
        res = subprocess.run(["which","goaccess"],stdout=subprocess.PIPE,text=True)

        if not res.stdout:
            return False,"failed"
        
        return True,res.stdout.strip()
    

    def exe(self,filename,ignore_setting=True):
        status,goacc = self.getGoaccess()

        if not status:
            return False,"Go Access not found"
        
        if not os.path.exists(filename):
            return False,"Error, filename or respone file not valid, please check your env"
        
        ignore_panel = ""
        if os.getenv("IGNORE_DATA") and os.getenv("IGNORE_DATA") != "" and ignore_setting:
            try:
                ignore = os.getenv("IGNORE_DATA")
                ignore = ignore.split("|")

                for item in ignore:
                    ignore_panel = ignore_panel+" --ignore-panel="+item

            except Exception as e:
                pass

        respone_file = os.path.splitext(filename)[0].split("/")[-1] + ".json"
        respone_file = os.path.join(self.respone_path,respone_file)

        print(respone_file)
                
        command = [
            goacc,
            filename,  # Path to the log file
            "--log-format=%h %^[%d:%t %^]%^\"%r\" %s %b \"%R\" \"%u\" %^",
            "--date-format=%d/%b/%Y",
            "--time-format=%T",
            *ignore_panel.split(),
            "-o",
            respone_file
        ]

        print(command)

        try:
            exe = subprocess.run(command,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
            print(exe.stderr)
        except Exception:
            return False,"Goaccess failed proccess data"
        

        if not os.path.exists(respone_file):
            return False,"Failed open respone fike"
        
        return True,"Success"

    def cekLogSize(self,filelog,old_size:int):
        if not os.path.exists(filelog):
            return False
        
        size = os.path.getsize(filelog)
        print(size,old_size)

        if size != old_size:
            return True
        
        return False
    
    def run(self):
        cekLog = LogModel.objects.all()
        ignore = os.getenv("IGNORE") if os.getenv("IGNORE") else False

        try:
            ignore = ignore.lower()
            if ignore == "true":
                ignore = True
            else:
                ignore = False

        except Exception as e:
            pass


        if not cekLog:
            print("LOG is empty")
            return False
        
        for log in cekLog:
            file = os.path.join(self.log_path,log.filename)
            size = os.path.getsize(file)

            if size != log.lastsize:

                status,msg= self.exe(file,ignore)
                if status:

                    print(f"Read log {file} Success")
                    respone_file = os.path.splitext(log.filename)[0].split("/")[-1] + ".json"
                    respone_file = os.path.join(self.respone_path,respone_file)

                    with open(respone_file,"r") as file:
                        go_json = json.load(file)

                    exe = MetaModel(name=log.filename,data=json.dumps(go_json))
                    exe.save()

                    log.lastsize = size
                    log.save()

                else:
                    print(f"Read log {file} Failed with error: {msg}")

        return True


        

 
    
    
    





