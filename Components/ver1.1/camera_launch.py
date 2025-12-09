#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -*- Python -*-

import sys
import time
import cv2
import os

sys.path.append(".")

# Import RTM module
import RTC
import OpenRTM_aist

# コンポーネント仕様
camera_launch_spec = ["implementation_id", "camera_launch", 
             "type_name",           "camera_launch", 
             "description",         "Camera Capture Component (File Based)", 
             "version",             "1.0.0", 
             "vendor",              "MikaKARASUDA", 
             "category",            "Camera", 
             "activity_type",       "PERIODIC", 
             "max_instance",        "1", 
             "language",            "Python", 
             "lang_type",           "SCRIPT",
             ""]

class camera_launch(OpenRTM_aist.DataFlowComponentBase):
    
    def __init__(self, manager):
        OpenRTM_aist.DataFlowComponentBase.__init__(self, manager)

        self._d_takepic = OpenRTM_aist.instantiateDataType(RTC.TimedBoolean)
        self._takepicIn = OpenRTM_aist.InPort("takepic", self._d_takepic)
        
        # 【変更】画像データではなく、ファイルパス(文字列)を送る
        self._d_filepath = OpenRTM_aist.instantiateDataType(RTC.TimedString)
        self._filepathOut = OpenRTM_aist.OutPort("picture", self._d_filepath) # ポート名はpictureのまま維持

        self._camera_index = 0
        print("[Camera] 初期化完了 (ファイル連携モード)")

    def onInitialize(self):
        self.addInPort("takepic", self._takepicIn)
        self.addOutPort("picture", self._filepathOut)
        return RTC.RTC_OK
    
    def onExecute(self, ec_id):
        if self._takepicIn.isNew():
            data = self._takepicIn.read()
            
            if data.data == True:
                print("【Camera】撮影トリガー受信。")
                self.capture_and_notify()
        
        return RTC.RTC_OK
    
    def capture_and_notify(self):
        try:
            cap = cv2.VideoCapture(self._camera_index)
            if not cap.isOpened():
                print(f"エラー: カメラ {self._camera_index} が開けません。")
                return

            ret, frame = cap.read()
            cap.release()
            
            if ret:
                # 画像を保存
                filename = "current_face.jpg"
                # フルパス（絶対パス）を取得して確実にする
                filepath = os.path.abspath(filename)
                
                cv2.imwrite(filepath, frame)
                print(f"【Camera】保存完了: {filepath}")
                
                # パスを送信
                self._d_filepath.data = filepath
                OpenRTM_aist.setTimestamp(self._d_filepath)
                self._filepathOut.write()
                print("【Camera】ファイルパスを送信しました。")
            else:
                print("エラー: 撮影失敗")

        except Exception as e:
            print(f"エラー: {e}")

def camera_launchInit(manager):
    profile = OpenRTM_aist.Properties(defaults_str=camera_launch_spec)
    manager.registerFactory(profile,
                            camera_launch,
                            OpenRTM_aist.Delete)

def MyModuleInit(manager):
    camera_launchInit(manager)
    instance_name_arg = ""
    for arg in sys.argv:
        if arg.startswith("--instance_name="):
            instance_name_arg = arg.replace("--", "?")
            break
    comp = manager.createComponent("camera_launch" + instance_name_arg)

def main():
    # RTM初期化 (引数クリーンアップ)
    sys.argv = [sys.argv[0]]
    
    # 設定ファイル生成 (シンプル設定)
    conf_file = "rtc.conf"
    try:
        with open(conf_file, "w") as f:
            f.write("corba.nameservers: 127.0.0.1:2809\n")
            f.write("logger.enable: NO\n") # ログ出力を切って動作を軽くする
    except:
        pass

    argv = [sys.argv[0], '-f', conf_file]
    mgr = OpenRTM_aist.Manager.init(argv)
    if mgr:
        mgr.setModuleInitProc(MyModuleInit)
        mgr.activateManager()
        print("[Camera] 起動しました。")
        mgr.runManager()

if __name__ == "__main__":
    main()
