#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -*- Python -*-

import sys
import time
import numpy as np
import cv2
import os

sys.path.append(".")

# Import RTM module
import RTC
import OpenRTM_aist

# コンポーネント仕様
skinana_red_spec = ["implementation_id", "skinana_red", 
             "type_name",           "skinana_red", 
             "description",         "Analyzes skin image (File Based)", 
             "version",             "1.0.0", 
             "vendor",              "MikaKARASUDA", 
             "category",            "Image Analysis", 
             "activity_type",       "PERIODIC", 
             "max_instance",        "1", 
             "language",            "Python", 
             "lang_type",           "SCRIPT",
             ""]

class skinana_red(OpenRTM_aist.DataFlowComponentBase):
    
    def __init__(self, manager):
        OpenRTM_aist.DataFlowComponentBase.__init__(self, manager)

        # InPort: 【変更】ファイルパス(文字列)を受け取る
        self._d_tookpic = OpenRTM_aist.instantiateDataType(RTC.TimedString)
        self._tookpicIn = OpenRTM_aist.InPort("tookpic", self._d_tookpic)
        
        self._d_rednum = OpenRTM_aist.instantiateDataType(RTC.TimedFloat)
        self._rednumOut = OpenRTM_aist.OutPort("rednum", self._d_rednum)

        print("[SkinAna] 初期化完了 (ファイル連携モード)")

    def onInitialize(self):
        self.addInPort("tookpic", self._tookpicIn)
        self.addOutPort("rednum", self._rednumOut)
        return RTC.RTC_OK
    
    def onExecute(self, ec_id):
        # パスの受信チェック
        if self._tookpicIn.isNew():
            data = self._tookpicIn.read()
            filepath = data.data
            
            print(f"【SkinAna】画像パスを受信: {filepath}")
            
            # ファイルが存在するか確認してから読み込む
            if os.path.exists(filepath):
                # 保存直後だと書き込み中の場合があるので少し待つ
                time.sleep(0.5) 
                
                image = cv2.imread(filepath)
                if image is not None:
                    print("【SkinAna】画像読み込み成功。解析開始...")
                    score = self.analyze_redness(image)
                    
                    self._d_rednum.data = float(score)
                    OpenRTM_aist.setTimestamp(self._d_rednum)
                    self._rednumOut.write()
                    print(f"【SkinAna】解析完了。スコア({score:.2f}%)を送信しました。")
                else:
                    print("エラー: 画像ファイルが読み込めませんでした。")
            else:
                print("エラー: 指定されたファイルが見つかりません。")

        return RTC.RTC_OK
    
    def analyze_redness(self, image_bgr):
        hsv = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2HSV)
        
        lower_red1 = np.array([0, 50, 50])
        upper_red1 = np.array([10, 255, 255])
        lower_red2 = np.array([170, 50, 50])
        upper_red2 = np.array([180, 255, 255])
        
        mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
        mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
        red_mask = mask1 + mask2
        
        # 確認用保存
        cv2.imwrite("debug_mask.jpg", red_mask)
        
        total = image_bgr.shape[0] * image_bgr.shape[1]
        red_pixels = cv2.countNonZero(red_mask)
        
        return (red_pixels / total * 100.0) if total > 0 else 0.0


def skinana_redInit(manager):
    profile = OpenRTM_aist.Properties(defaults_str=skinana_red_spec)
    manager.registerFactory(profile,
                            skinana_red,
                            OpenRTM_aist.Delete)

def MyModuleInit(manager):
    skinana_redInit(manager)
    instance_name_arg = ""
    for arg in sys.argv:
        if arg.startswith("--instance_name="):
            instance_name_arg = arg.replace("--", "?")
            break
    comp = manager.createComponent("skinana_red" + instance_name_arg)

def main():
    sys.argv = [sys.argv[0]]
    conf_file = "rtc.conf"
    try:
        with open(conf_file, "w") as f:
            f.write("corba.nameservers: 127.0.0.1:2809\n")
            f.write("logger.enable: NO\n")
    except:
        pass

    argv = [sys.argv[0], '-f', conf_file]
    mgr = OpenRTM_aist.Manager.init(argv)
    if mgr:
        mgr.setModuleInitProc(MyModuleInit)
        mgr.activateManager()
        print("[SkinAna] 起動しました。")
        mgr.runManager()

if __name__ == "__main__":
    main()
