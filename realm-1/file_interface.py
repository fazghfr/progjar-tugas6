import os
import json
import base64
from glob import glob


class FileInterface:
    def __init__(self):
        os.chdir('files/')


    def list(self,params=[]):
        try:
            filelist = glob('*.*')
            return dict(status='OK',data=filelist)
        except Exception as e:
            return dict(status='ERROR',data=str(e))

    def get(self,params=[]):
        try:
            filename = params[0]
            if (filename == ''):
                return None
            fp = open(f"{filename}",'rb')
            isifile = base64.b64encode(fp.read()).decode()
            return dict(status='OK',data_namafile=filename,data_file=isifile)
        except Exception as e:
            return dict(status='ERROR',data=str(e))
        
    def delete(self,params=[]):
        try:
            filename = params[0]
            os.remove(f"{filename}")
            return dict(status='OK',data='File deleted')
        except Exception as e:
            return dict(status='ERROR',data=str(e))
        
    def data(self, params=[]):
        try:
            if "=u=" in params[0]:
                parts = params[0].split('=u=')
                username = parts[0]
                filename = parts[1]
                username_from = parts[2]

                filename = "user_"+username+"_from_"+username_from+"_"+filename


            else :
                parts = params[0].split('=g=')
                print("parts ", parts)
                groupname = parts[0]
                filename = parts[1]
                username_from = parts[2]

                filename = "group_"+groupname+"_from_"+username_from+"_"+filename

            isifile = params[2][1:]
            if os.path.exists(f"{filename}"):
                fp = open(f"{filename}",'ab')
            else:
                fp = open(f"{filename}",'wb')
            fp.write(base64.b64decode(isifile))
            fp.close()
            return dict(status='OK',data=f"Data Chunk uploaded on file {filename}")
        except Exception as e:
            return dict(status='ERROR',data=str(e))



if __name__=='__main__':
    f = FileInterface()
    print(f.list())
    # print(f.delete(['pokijan2.jpg']))
