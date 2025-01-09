import os,subprocess,yaml
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
    
    def filenameRespone(self,filename):

        respone_path = os.path.splitext(filename)[0].split("/")[-2]
        respone_path = os.path.join(self.respone_path,respone_path)

        respone_file = os.path.splitext(filename)[0].split("/")[-1] + ".json"
        respone_file = os.path.join(respone_path,respone_file)

        return respone_file,respone_path


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


        respone_file,respone_path = self.filenameRespone(filename)

        if not os.path.exists(respone_path):
            os.mkdir(respone_path)
                
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
            file = log.filename.lstrip("/")
            file = os.path.join(self.log_path,file)
            size = os.path.getsize(file)

            print(file)

            if size != log.lastsize:

                status,msg= self.exe(file,ignore)
                if status:

                    print(f"Read log {file} Success")
                    respone_file,respone_path = self.filenameRespone(log.filename)
                    print(respone_file)
                    

                    with open(respone_file,"r") as file:
                        go_json = json.load(file)

                    exe = MetaModel(name=log.filename,data=json.dumps(go_json))
                    exe.save()

                    log.lastsize = size
                    log.save()

                else:
                    print(f"Read log {file} Failed with error: {msg}")
                    return False

        return True
    
    def CheckHostPath(self,path):
        endpoint = "http://" + os.getenv("DOCKER_IP") + ":" +os.getenv("DOCKER_MACH_PORT")

        #cek path in host machine
        endpoint_cek = endpoint + "/service/check_path"

        data_to_send = {
            "path":path
        }

        try:
            res = requests.post(endpoint_cek,json=data_to_send)
            if res.status_code == 200:
                return True
            
            return False

        except Exception as e:
            return False
        
    def editYaml(self,path_host,path_machine):
        docker_yaml_loc = "/home/kecilin/docker-compose-testing.yaml"
        with open(docker_yaml_loc,'r') as config:
                data = yaml.safe_load(config)

        try:
            if not data['services']['dashboard']['volumes']:
                return False,"Volumes not found"
            
            data_add = path_host+":"+path_machine

            for i in data['services']['dashboard']['volumes']:
                if i == data_add:
                    return False,"Already add volumes"

            data['services']['dashboard']['volumes'].append(data_add)

        except Exception as e:
            return False,"Error while read yaml"
        

        try:
            with open(docker_yaml_loc,'w') as file:
                yaml.dump(data, file, default_flow_style=False)
        except:
            return False
                
        return True,"Success Edit Yaml"
    

    def AddPath(self,path_host,path_machine):
        
        cek_host = self.CheckHostPath(path_host)

        if not cek_host:
            return False,"Path host not found or Error"
        
        editStatus,editMsg = self.editYaml(path_host,path_machine)

        if not editStatus:
            return False,editMsg

        endpoint = "http://" + os.getenv("DOCKER_IP") + ":" +os.getenv("DOCKER_MACH_PORT")

        endpoint_cek = endpoint + "/service/restart-docker"

        docker_filename = os.path.join(os.getenv("DOCKER_FILE_LOCATION"),os.getenv("DOCKER_FILE_NAME"))
        
        data_to_send = {
            "path":docker_filename
        }

        try:
            res = requests.post(endpoint_cek,json=data_to_send)
            if res.status_code == 200:
                return True
            
            return False,"Failed to send"

        except Exception as e:
            return False,"Failed host service is die"





        

        

    



        

 
    
    
    





