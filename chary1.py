# -*- coding: utf-8 -*-
import os
import io
import base64
import sys
import struct
import time
import threading
import hashlib
import logging
import chardet
from naoqi import ALProxy
reload(sys)
sys.setdefaultencoding('utf8')

class MyClass:
    def __init__(self):
        ip = "172.16.100.116"
        # GeneratedClass.__init__(self)
        self.pkg = ALProxy('PackageManager', ip, 9559)
        self.ALsys = ALProxy('ALSystem', ip, 9559)
        self.ALBattery = ALProxy('ALBattery', ip, 9559)
        self.Behavior = ALProxy('ALBehaviorManager', ip, 9559)
        self.RobotPosture = ALProxy('ALRobotPosture', ip, 9559)
        self.Motion = ALProxy('ALMotion', ip, 9559)
        self.Dialog = ALProxy('ALDialog', ip, 9559)
        self.tts = ALProxy('ALTextToSpeech', ip, 9559)
        self.ALMemory = ALProxy('ALMemory', ip, 9559)
        self.ALAudio = ALProxy('ALAudioDevice', ip, 9559)
        self.photoCapture = ALProxy("ALPhotoCapture", ip, 9559)
        self.videoRecorder = ALProxy("ALVideoRecorder", ip, 9559)
        global flag
        flag = True

    def onLoad(self):
        self.log("onLoad")
        pass

    def onUnload(self):
        self.log("onUnload")
        flag = False
        s.shutdown(2)
        s.close()
        # put clean-up code here
        pass
    def log(self,printContent):
        print(printContent)

    def onInput_onStart(self):
        #        self.search("/home/nao/.local/share/PackageManager/apps", ".top")
        # self.onStopped() #activate the output of the box
        self.log("onInput_onStart")
        #        self.alter("/home/nao/test1.txt", "123", "python")
        #        self.pkgM()
        #        self.ShutDown()
        #        self.search_r_elec()
        #        self.stand_up()
        import socket

        # 服务器IP
        ip_port = ("172.16.100.118", 1234)
        # ip_port = ("101.132.70.174", 1234)
        # ip_port = ("172.16.100.117", 9999)

        global s

        global listtop
        listtop = []
        # 创建socket
        s = socket.socket()

        s.connect(ip_port)

        # # 获取电量线程
        # trdBattery = threading.Thread(target=self.rec, args=(s,))
        # trdBattery.start()

        # 获取机器人语句线程
        trdSayText = threading.Thread(target=self.saytext, args=(s,))
        trdSayText.start()

        trdTouch = threading.Thread(target=self.touchHands, args=(s,))
        trdTouch.start()
        while True:
            try:
                list1 = []
                global first
                first = 1
                self.log(s.getsockname())
                welcom_msg = s.recv(1024)

                # 补全1024个字节
                while len(welcom_msg) < 1024:
                    welcom_msg = welcom_msg + s.recv(1024 - len(welcom_msg))
                self.log(welcom_msg)
                welcom_msg = welcom_msg.replace('\r\n', '')
                print repr(welcom_msg.decode("utf-8"))
                # 获取解析结果
                numStr = self.R2SAnalysis(welcom_msg)
                #                self.log("num1 length = " + len(num1))
                #                num1 = self.pkg.packageIcon("helloworld-263d9a")
                try:
                    num1 = numStr[0]
                except Exception, ex:
                    num1 = ''
                    pass
                # 获取命令名称
                ordername = welcom_msg[8:33].replace(' ', '')
                if type(num1) == str:
                    self.log("num1 length = " + str(len(num1)))
                self.log(num1)
                #        print("dianliang = "+str(num1))
                #        sss = "R2S01return_search_r_elec     12 " + str(num1)
                self.log("pkgsucced")
                sss = str(num1)
                countPic = 0

                # 应用图片
                if ordername == "apppic":
                    uuid = welcom_msg[(38 + 10):].replace(' ', '')
                    apppic = threading.Thread(target=self.picthreading, args=(uuid, numStr, list1, countPic, first,))
                    apppic.start()

                # 对话
                elif ordername == "dialog1":
                    self.log("ordername = dialog1")

                # 安装app
                elif ordername == "install":
                    order = self.stringFormat("return_install", 25)
                    robotid = self.stringFormat("nao002", 10)
                    lasti = "R2S" + '11   ' + order + "1" + "7   " + robotid + Timestamps + "pkgDown"
                    lasti = self.stringFormat(lasti,1024)
                    if numStr == "pkgDown":
                        # s.sendall(lasti)
                        self.log("xxxxxxxxxx")
                    else:
                        self.log("install not finish")
                elif ordername == "take_video":
                    self.sendPhoto(numStr, ordername, 1)
                else:
                    self.sendMsg(numStr, ordername, 1)

            except Exception, ex:
                self.log("except err")
                err = str(ex).decode('SHIFT_JIS').encode('utf-8')
                self.log(err)
                s.shutdown(2)
                s.close()
                # s = socket.socket()
                # self.connecttos(s, ip_port)
        pass

    # 发送
    def sendMsg(self, returnContent, ordername, n):
        list2 = []
        count = 0
        firstCount = 1
        offsetlen = 33 + 1 + 4 * n + 10 + 10
        if ordername == "dialog":
            return 0

        while returnContent:
            self.log("pkgsucced1111111")
            pkgStr = returnContent[:1024 - offsetlen]
            self.log("pkgsucced22222222")
            list2.append(pkgStr)
            self.log("pkgsucced333333333")
            returnContent = returnContent[1024 - offsetlen:]
            self.log(count)
            count = count + 1
        # print list[0]

        for i in list2:
            iiString = self.stringFormat(count, 4)
            order = self.stringFormat("return_" + ordername, 25)
            robotidLen = self.stringFormat(len("nao002"), 4)
            robotid = self.stringFormat("nao002", 10)

            iString = self.stringFormat(len(i), 4)
            lasti = "R2S" + str(firstCount) + iiString + order + str(n) + iString + robotid + Timestamps + i

            #                    lasti = "R2S10000return_search_r_pkged    11024" + i
            if len(lasti) < 1024:
                lasti = self.stringFormat(lasti, 1024)
            self.log(len(lasti))
            self.log(lasti)

            self.Logging(lasti)
            s.sendall(lasti)
            firstCount = 0
            count = count - 1
        firstCount = 1
        # time.sleep(2)

         # 发送照片
    def sendPhoto(self, returnContent, ordername, n):
        list2 = []
        count = 0
        firstCount = 1
        offsetlen = 33 + 1 + 4 * n + 10 + 10
        if ordername == "dialog":
            return 0
        totalLength = len(returnContent)
        count = totalLength/(1024 - offsetlen)
        if(totalLength%(1024 - offsetlen )):
            count = count + 1
        while returnContent:
            self.log("pkgsucced1111111")
            pkgStr = returnContent[:1024 - offsetlen]
            self.log("pkgsucced22222222")
            list2.append(pkgStr)

            iiString = self.stringFormat(count, 4)
            order = self.stringFormat("return_" + ordername, 25)
            robotidLen = self.stringFormat(len("nao002"), 4)
            robotid = self.stringFormat("nao002", 10)

            iString = self.stringFormat(len(pkgStr), 4)
            lasti = "R2S" + str(firstCount) + iiString + order + str(n) + iString + robotid + Timestamps + pkgStr

            #                    lasti = "R2S10000return_search_r_pkged    11024" + i
            if len(lasti) < 1024:
                lasti = self.stringFormat(lasti, 1024)
            self.log(len(lasti))
            self.log(lasti)

            self.Logging(lasti)
            s.sendall(lasti)
            firstCount = 0
            count = count - 1

            self.log("pkgsucced333333333")
            returnContent = returnContent[1024 - offsetlen:]
            self.log(count)
        # print list[0]

    # 电量线程函数 和上次不同才发送，间隔时间为10s
    def rec(self, sock):
        BatteryResultNext = -1
        while True:
            BatteryResult = self.ALBattery.getBatteryCharge()
            if BatteryResult != BatteryResultNext:
                battery =  str(BatteryResult)
                batteryLen = len(battery)
                iString = self.stringFormat(str(batteryLen),4)
                lasti = "R2S" + '1' + '1   ' + "return_search_r_elec     " + "1" + iString + "nao002    " + battery

                #                    lasti = "R2S10000return_search_r_pkged    11024" + i
                if len(lasti) < 1024:
                    lasti = self.stringFormat(lasti, 1024)
                self.log(len(lasti))
                self.log(lasti)

                self.Logging(lasti)
                s.sendall(lasti)

            BatteryResultNext = BatteryResult
            time.sleep(10)

    # 语句线程函数
    def saytext(self, sock):
        saycontentTemp = ""
        while True:
            saycontent = self.ALMemory.getData("ALTextToSpeech/CurrentSentence")
            if (saycontent and (saycontent != saycontentTemp)):
                saycontent = str(saycontent)
                saycontentLen = len(saycontent)
                iString = self.stringFormat(str(saycontentLen), 4)
                lasti = "R2S" + '1' + '1   ' + "return_dialog            " + "1" + iString + "nao002    " + Timestamps + saycontent
                if len(lasti) < 1024:
                    lasti = self.stringFormat(lasti, 1024)
                self.log(len(lasti))
                self.log(lasti)
                self.Logging(lasti)
                sock.sendall(lasti)
            saycontentTemp = saycontent
        time.sleep(1)

    def touchHands(self, sock):
        saycontentTemp = ""
        while True:
            touchleft = self.ALMemory.getData("HandLeftBackTouched")
            touchright = self.ALMemory.getData("HandRightBackTouched")
            self.touchSend("left", touchleft, sock)
            self.touchSend("right", touchright, sock)
        time.sleep(1)

    def Logging(self, logStr):
        logging.basicConfig(filename=os.path.join(os.getcwd(), 'C:\\log.txt'), level=logging.DEBUG)
        logging.debug(logStr)

    def touchSend(self,hands, touchmsg , sock):
        if (touchmsg == 1):
            touchmsg = str(touchmsg)
            touchcontentLen = len(touchmsg)
            iString = self.stringFormat(str(touchcontentLen), 4)
            if hands == "left":
                lasti = "R2S" + '1' + '1   ' + "return_lefthand          " + "1" + iString + "nao002    " + Timestamps + touchmsg
            elif hands == "right":
                lasti = "R2S" + '1' + '1   ' + "return_righthand         " + "1" + iString + "nao002    " + Timestamps + touchmsg
            if len(lasti) < 1024:
                lasti = self.stringFormat(lasti, 1024)
            self.log(len(lasti))
            self.log(lasti)
            self.Logging(lasti)
            sock.sendall(lasti)
        # saycontentTemp = touchleft

    # 图片线程函数
    def picthreading(self, uuid, sss, list1, countPic, first):
        n = 2
        offsetlen = 33 + 1 + 4 * n + 10 + 10 + len(uuid)
        if sss == '':
            iiStringNull = self.stringFormat(1, 4)
            orderNull = self.stringFormat("return_apppic", 25)
            robotidLenNull = self.stringFormat(len("nao002"), 4)
            robotidNull = self.stringFormat("nao002", 10)
            uuidLenNull = self.stringFormat(len(uuid), 4)
            iStringNull = self.stringFormat('', 4)
            lastiNull = "R2S" + str(first) + iiStringNull + orderNull + "1" + uuidLenNull + robotidNull + Timestamps + uuid + ''
            if len(lastiNull) < 1024:
                lastiNull = self.stringFormat(lastiNull, 1024)
            self.log(len(lastiNull))
            self.log(lastiNull)
            self.Logging(lastiNull)
            s.sendall(lastiNull)
            return 0

        totalLength = len(sss)
        countPic = totalLength / (1024 - offsetlen)
        if (totalLength % (1024 - offsetlen)):
            countPic = countPic + 1

        while sss:
            self.log("pkgsucced1111111")
            pkgStr = sss[:1024 - offsetlen]

            iiString = self.stringFormat(countPic, 4)
            order = self.stringFormat("return_apppic", 25)
            robotidLen = self.stringFormat(len("nao002"), 4)
            robotid = self.stringFormat("nao002", 10)
            uuidLen = self.stringFormat(len(uuid), 4)
            iString = self.stringFormat(len(pkgStr), 4)
            lasti = "R2S" + str(first) + iiString + order + "2" + uuidLen + iString + robotid + Timestamps + uuid + pkgStr

            if len(lasti) < 1024:
                lasti = self.stringFormat(lasti, 1024)
            self.log(len(lasti))
            self.log(lasti)
            self.Logging(lasti)
            s.sendall(lasti)
            first = 0
            countPic = countPic - 1

            self.log("pkgsucced22222222")

            self.log("pkgsucced333333333")
            sss = sss[1024 - offsetlen:]
            self.log(countPic)

        # print list[0]

    def connecttos(self, ss, ipport):
        try:
            time.sleep(2)
            ss.connect(ipport)
        except:
            self.connecttos(ss, ipport)

    def onInput_onStop(self):
        self.log("ffffffff1")
        self.onUnload()  # it is recommended to reuse the clean-up as the box is stopped
        self.onStopped()  # activate the output of the box

    # Set the string format
    def stringFormat(self, oldString, newStringLen):
        oldString = str(oldString)
        while len(oldString) < newStringLen:
            oldString = oldString + ' '
        return oldString

    # Icon获取
    def pkgM(self, buf1):
        self.log("pkgM444444444")
        pkgs = self.pkg.packageIcon(buf1)
        self.log("pkgM555555555")
        pkgs = base64.b64encode(pkgs)
        self.log(pkgs)

        #        self.tts.say(pkgs)
        #        str = base64.b64encode(pkgs)
        #        fh = open("/home/nao/imageToSave1.png", "wb")
        #        fh.write(str.decode('base64'))
        #        fh.close()
        return pkgs

    # Robot Name
    def search_r_name(self):
        name = self.ALsys.robotName()
        self.log(name)
        return name

    # Reboot
    def restart(self):
        self.ALsys.reboot()
        return "restart"

    # Shut Down
    def shut_down(self):
        self.ALsys.shutdown()
        return "shut_down"

    # battery power
    def search_r_elec(self):
        self.log(self.ALBattery.getBatteryCharge())
        BatteryResult = self.ALBattery.getBatteryCharge()
        # self.tts.say(str(BatteryResult))
        return str(BatteryResult)

    # package list
    def search_r_pkged(self):
        self.log("package succeed")
        packageContent = self.pkg.packages()

        countA = 0
        strPack = ''
        packageLen = len(packageContent)
        while packageLen > 0:
            countB = 0
            pkgbehaviorContentTemp = ''
            # UUID
            pkgUUID = packageContent[countA][0][1]
            if pkgUUID == "animations":
                countA = countA + 1
                packageLen = packageLen - 1
                continue
            # Version
            pkgVerion = packageContent[countA][2][1]
            # Behavior
            pkgbehavior = packageContent[countA][11][1]

            pkgbehaviorLen = len(pkgbehavior)
            try:
                while pkgbehaviorLen > 0:
                    pkgbehaviorContent = pkgbehavior[countB][0][1]
                    print pkgbehaviorContent
                    if pkgbehaviorContent == '.':
                        pkgbehaviorContent = pkgUUID
                    else:
                        pkgbehaviorContent = pkgUUID + '/' + pkgbehaviorContent

                    pkgbehaviorContentTemp = pkgbehaviorContentTemp + ',' + pkgbehaviorContent
                    countB = countB + 1
                    pkgbehaviorLen = pkgbehaviorLen - 1
            except:
                pass

            strPack = strPack + pkgUUID + ',' + pkgVerion + pkgbehaviorContentTemp + ';'
            #            print(strPack)
            countA = countA + 1
            packageLen = packageLen - 1
            strLen = len(strPack)
        return strPack

    # Image verification
    def imageVerification(self):
        self.log("imageVerification")
        packageContent = self.pkg.packages()

        countA = 0
        strPack = ''
        # app number
        packageLen = len(packageContent)
        while packageLen > 0:
            # UUID
            pkgUUID = packageContent[countA][0][1]
            pkgs = self.pkg.packageIcon(pkgUUID)
            # Code conversion
            pkgs = base64.b64encode(pkgs)
            pkgs = pkgs.replace(' ', '')
            # md5 conversion
            md5 = hashlib.md5()
            md5.update(pkgs)
            pkgs = str(md5.hexdigest())
            strPack = strPack + pkgUUID + ',' + pkgs + ';'
            countA = countA + 1
            packageLen = packageLen - 1
        return strPack

    # start behavior
    def start_beh(self, behavior):
        if self.Behavior.isBehaviorRunning(behavior):
            return "start_beh"
        self.Behavior.startBehavior(behavior)
        return "start_beh"

    # stop behavior
    def stop_beh(self, behavior):
        if behavior == "":
            self.Behavior.stopBehavior("connecttoai_1108/behavior_1")
        self.Behavior.stopBehavior(behavior)
        return "stop_beh"

    # start move behavior
    def start_move_beh(self):
        if self.Behavior.isBehaviorRunning("connecttoai_1108/behavior_1"):
            return "start_move_beh"
        self.Behavior.startBehavior("connecttoai_1108/behavior_1")
        return "start_move_beh"

    # stop move behavior
    def stop_move_beh(self):
        self.Behavior.stopBehavior("connecttoai_1108/behavior_1")
        return "stop_move_beh"

    # dance
    def dance(self):
        self.Behavior.startBehavior("little-apple-dance")
        return "start_beh"

    # stand up
    def stand_up(self):
        self.RobotPosture.goToPosture('Stand', 0.5)
        return "stand_up"

    # sit
    def sit_down(self):
        self.Motion.rest()
        # self.RobotPosture.goToPosture('Crouch', 0.3)
        return "sit_down"

    # move
    def move(self, x, y, theta):
        if x == "":
            x = float(0)
        if y == "":
            y = float(0)
        if theta == "":
            theta = float(0)

        x = float(x)
        y = float(y)
        theta = float(theta)
        self.Motion.moveTo(x, y, theta)
        return "move"

    # stop move
    def stop_move(self):
        self.Motion.stopMove()
        return "stop_move"

    # Dialog
    def dialog(self, content):
        # content = str(content).decode('GBK').encode('utf-8')
        print repr(content.decode("utf-8"))
        print chardet.detect(content)
        if content == "1111":
            result = self.take_picture()
            # ss = '<img class="right" src="data:image/gif;base64,R0lGODlhDwAPAKECAAAAzMzM/////wAAACwAAAAADwAPAAACIISPeQHsrZ5ModrLlN48CXF8m2iQ3YmmKqVlRtW4MLwWACH+H09wdGltaXplZCBieSBVbGVhZCBTbWFydFNhdmVyIQAAOw=="alt="Base64 encoded image" width="50" height="50"/>';

            head = '<img class="right" src='
            end = 'alt="Base64 encoded image" width="160" height="120"/>'
            # mind = "data:image/gif;base64,R0lGODlhDwAPAKECAAAAzMzM/////wAAACwAAAAADwAPAAACIISPeQHsrZ5ModrLlN48CXF8m2iQ3YmmKqVlRtW4MLwWACH+H09wdGltaXplZCBieSBVbGVhZCBTbWFydFNhdmVyIQAAOw=="
            mind = result
            mind = '"data:image/jpeg;base64,' + mind + '"'
            result = head + mind + end
            # if ss == result:
            #     self.log("same str")
            self.log(result)
            return result
        else:
            # content = base64.b64encode(content)
            self.Dialog.forceInput(str(content))
            return "say succeed"

    # get volume
    def getVolume(self):
        volumeNum = str(self.ALAudio.getOutputVolume())
        return volumeNum

    # set volume
    def setVolume(self, volume):
        volume = int(volume)
        if volume >= 0 and volume <= 100 :
            self.ALAudio.setOutputVolume(volume)
            return "set_volume"
        else:
            return "set_volume_failed"

    # search top
    def search_r_top(self, path, word):
        for filename in os.listdir(path):
            fp = os.path.join(path, filename)
            if os.path.isfile(fp) and word in filename:
                self.log(fp)
                listtop.append(fp)
            elif os.path.isdir(fp):
                self.search_r_top(fp, word)
        return listtop

    # Display top file contents
    def show_top_c(self, path):
        f = open(path, "r")
        lines = f.read()
        f.close()
        return str(lines)

    # Add top file contents
    def add_top_c(self, path, contents):
        f = file(path, "a+")
        f.write('\n' + contents + '\n')
        f.close()
        self.Dialog.loadTopic("/home/nao/.local/share/PackageManager/apps/connecttoai_1108/behavior_1/ExampleDialog/ExampleDialog_mnc.top")
        return "add_top_c"

    # Delete top file contents
    def delete_top_c(self, path, contents):
        with io.open(path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            # print(lines)
        with io.open(path, "w", encoding="utf-8") as f_w:
            for line in lines:
                if contents in line:
                    continue
                f_w.write(line)
        self.Dialog.loadTopic("/home/nao/.local/share/PackageManager/apps/connecttoai_1108/behavior_1/ExampleDialog/ExampleDialog_mnc.top")
        return "delete_top_c"

    # Edit top file contents
    def edit_top_c(self, file, old_str, new_str):
        file_data = ""
        with io.open(file, "r", encoding="utf-8") as f:
            for line in f:
                if old_str in line:
                    line = line.replace(old_str, new_str)
                file_data += line
        with io.open(file, "w", encoding="utf-8") as f:
            f.write(file_data)

        self.Dialog.loadTopic("/home/nao/.local/share/PackageManager/apps/connecttoai_1108/behavior_1/ExampleDialog/ExampleDialog_mnc.top")
        return "edit_top_c"

    # Delete top file
    def delete_top(self, path):
        os.remove(path)
        return "delete_top"

    # Add top file
    def add_top(self, path):
        fp = open(path, "w")
        fp.write("topic: ~ExampleDialog()\nlanguage: mnc")
        fp.close()
        return "add_top"

    # take picture
    def take_picture(self):
        # recordFolder = "/home/nao/recordings/cameras/"
        # self.photoCapture.setResolution(2)
        # self.photoCapture.setCameraID(0)
        # self.photoCapture.setPictureFormat("jpg")
        # self.photoCapture.takePicture(recordFolder, "image1")
        #
        # with open("/home/nao/recordings/cameras/image1.jpg", "rb") as f:
        #     # b64encode是编码，b64decode是解码
        #     base64_data = base64.b64encode(f.read())
        #     # base64.b64decode(base64data)
        #     print(base64_data)
        #     return base64_data
        with open("C:\\Users\\transcosmos\\Desktop\\image1.jpg", "rb") as f:
            # b64encode是编码，b64decode是解码
            base64_data = base64.b64encode(f.read())
            # base64.b64decode(base64data)
            self.log(base64_data)
            return base64_data

    # take video
    def take_video(self):
        self.videoRecorder.setFrameRate(10.0)
        self.videoRecorder.setResolution(2)
        self.videoRecorder.startRecording("/home/nao/recordings/cameras", "test")
        self.log("Video record started.")

        time.sleep(5)

        videoInfo = self.videoRecorder.stopRecording()
        self.log("Video was saved on the robot: ", videoInfo[1])
        self.log("Total number of frames: ", videoInfo[0])

        with open("/home/nao/recordings/cameras/test.avi", "rb") as f:
            # b64encode是编码，b64decode是解码
            base64_data = base64.b64encode(f.read())
            # base64.b64decode(base64data)
            self.log(base64_data)
            return base64_data


    # Download pkg
    def pkgDown(self, buf1):
        isExists = os.path.exists('D:/pythoncreatFiletest/')
        if not isExists:
            # 如果不存在则创建目录
            # 创建目录操作函数
            os.makedirs('D:/pythoncreatFiletest/')

        filepath = 'D:/pythoncreatFiletest/' + buf1[2]
        self.log(os.getcwd())
        if buf1[0] == '1':
            if os.path.isfile(filepath) == False:
                f = open(filepath, 'ab+')
                f.write(buf1[3])
                f.close()

            else:
                os.remove(filepath)
                f = open(filepath, 'ab+')
                f.write(buf1[3])
                f.close()
        else:
            if int(buf1[1]) == 1:
                f = open(filepath, 'ab+')
                f.write(buf1[3])
                f.close()
                self.log("Download SUCCEED")
                self.install(filepath)
            else:
                f = open(filepath, 'ab+')
                f.write(buf1[3])
                f.close()
        return "pkgDown"

    # Install pkg
    def install(self, path):
        self.pkg.install(path)
        return "install"
        pass

    # Remove pkg
    def uninstall(self, uuid):
        # self.pkg.removePkg(uuid)
        return "uninstall"

    # 解析具体是那个命令
    def Annn(self, buf, buf1):
        # listtop = []
        # 根据接受的命令执行不同操作
        self.log("buf =" + buf)
        self.log("buf1 =" + repr(buf))
        if buf == "search_r_name":
            return self.search_r_name()
        elif buf == "search_r_elec":
            self.log("okokokokokok")
            return self.search_r_elec()
        elif buf == "search_r_pkged":
            self.log("okokokokokok1")
            return self.search_r_pkged()
        elif buf == "apppic":
            self.log("pkgM66666")
            self.log("self.pkgM()=" + self.pkgM(buf1[2]))
            return self.pkgM(buf1[2])
        elif buf == "restart":
            return self.restart()
        elif buf == "shut_down":
            return self.shut_down()
        elif buf == "start_beh":
            return self.start_beh(buf1[2])
        elif buf == "stop_beh":
            return self.stop_beh(buf1[2])
        elif buf == "start_move_beh":
            return self.start_move_beh()
        elif buf == "stop_move_beh":
            return self.stop_move_beh()
        elif buf == "dance":
            return self.dance()
        elif buf == "stand_up":
            return self.stand_up()
        elif buf == "sit_down":
            return self.sit_down()
        elif buf == "move":
            self.log("movexyz")
            self.log(buf1[2])
            self.log(buf1[3])
            self.log(buf1[4])
            return self.move(buf1[2] , buf1[3] ,buf1[4])
        elif buf == "stop_move":
            return self.stop_move()
        elif buf == "dialog":
            return self.dialog(buf1[2])
        elif buf == "get_volume":
            return self.getVolume()
        elif buf == "set_volume":
            return self.setVolume(buf1[2])
        elif buf == "search_r_top":
            del listtop[:]
            result_search_r_top = ''
            result = self.search_r_top("D:\\test", ".top")
            for i in result:
                result_search_r_top = result_search_r_top + i + ';'
            return result_search_r_top
        elif buf == "show_top_c":
            result_show_top_c = self.show_top_c(buf1[2])
            return result_show_top_c
        elif buf == "add_top_c":
            result_add_top_c = self.add_top_c(buf1[2] , buf1[3])
            return result_add_top_c
        elif buf == "delete_top_c":
            result_delete_top_c = self.delete_top_c(buf1[2] , buf1[3])
            return result_delete_top_c
        elif buf == "edit_top_c":
            result_edit_top_c = self.edit_top_c(buf1[2] , buf1[3] ,buf1[4])
            return result_edit_top_c
        elif buf == "delete_top":
            result_delete_top = self.delete_top(buf1[2])
            return result_delete_top
        elif buf == "add_top":
            result_add_top = self.add_top(buf1[2])
            return result_add_top
        elif buf == "take_picture":
            result_take_picture = self.take_picture()
            return result_take_picture
        elif buf == "take_video":
            result_take_video = self.take_video()
            return result_take_video

            #        elif buf == "install":
            #            install(path)
            #        elif buf == "uninstall":
            #            uninstall(uuid)
        elif buf == "install":
            result_install = self.pkgDown(buf1)
            return result_install
        elif buf == "imageVerification":
            result_imageVerification = self.imageVerification()
            return result_imageVerification
    # protocol
    def R2Sprotocol(self, isLargeFile, returnCount, order, parametersCount, tup, tup2Content, RobotID):
        head = "R2S"
        result1 = ''
        result2 = ''
        i = 0

        result0 = struct.pack("3sBB25sB", head, isLargeFile, returnCount, order, parametersCount)
        tup1Count = len(tup)
        for tupContent in tup:
            result1 = result1 + struct.pack("h", tupContent)

        for tup2Content in tup2Content:
            s = str(tup[i]) + 's'
            result2 = result2 + struct.pack(s, tup2Content)
            i = i + 1
        RobotIDByte = struct.pack("10s", RobotID)
        result = result0 + result1 + RobotIDByte + result2
        return result

    # 解析函数
    def R2SAnalysis(self, s):
        # s = s.replace('\r\n', '')
        s1 = s
        self.log(s1)
        self.log("s length =" + str(len(s)))
        self.log("s1 length =" + str(len(s1)))
        self.log("s = " + repr(s))
        self.log("s1 = " + repr(s1))
        orderName = s[8:33].replace(' ', '')

        #获取参数个数
        paraNum = int(s1[33:34])
        self.log(paraNum)
        paraNumTemp = paraNum
        firstNum = 34
        lastNum = 38

        #参数长度列表
        listparaLen = []

        #参数内容列表
        listpara = []

        #获取各参数长度
        while paraNumTemp:
            tempSize = int(s1[firstNum:lastNum].replace(' ', ''))
            listparaLen.append(tempSize)
            firstNum = firstNum + 4
            lastNum = lastNum + 4
            paraNumTemp = paraNumTemp - 1
        self.log(listparaLen)
        lenlistparaLen = len(listparaLen)
        firstNum = firstNum - 4
        lastNum = lastNum - 4

        global Timestamps
        Timestamps = s1[lastNum: lastNum + 10]

        lastNum = lastNum + 10

        #获取各参数内容
        for tt in listparaLen:
            listpara.append(s1[lastNum: lastNum + tt])
            lastNum = lastNum + tt

        self.log(listpara)
        addContent = "10s"

        #计算实际字符串长度
        for ttt in listparaLen:
            addContent = addContent + str(ttt) + "s"
        addstr = str(paraNum * 4) + "s" + addContent
        allNum = 0

        for tttt in listparaLen:
            allNum = allNum + tttt
        allNum = allNum + 34 + paraNum * 4 + 10
        s1 = s1[0:allNum]

        headR2SAnalysis = struct.unpack("3sBBBBB25ss" + addstr, s1)
        self.log(headR2SAnalysis[6])
        self.log("headR2SAnalysis[6] = " + repr(headR2SAnalysis[6]))
        self.log(len(headR2SAnalysis[6]))
        ss = headR2SAnalysis[6].replace(' ', '')
        self.log(ss)
        self.log("ss = " + repr(ss))
        isFirstandSendNum = []

        #获取是否是第一条消息
        isFirstandSendNum.append(s1[3:4])

        #获取发送次数（是否最后一次）
        isFirstandSendNum.append(s1[4:8].replace(' ', ''))
        if s1[4:8].replace(' ', '') == "44":
            self.log("44444444444444444444")
        isFirstandSendNum.extend(listpara)
        return self.Annn(ss, isFirstandSendNum)
xxxx = MyClass()
xxxx.onInput_onStart()# NaoRobot
