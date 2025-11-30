#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -*- Python -*-

import sys
import time
import tkinter as tk
sys.path.append(".")

# Import RTM module
import RTC
import OpenRTM_aist

# コンポーネント仕様
system_open_spec = ["implementation_id", "system_open",
                    "type_name",         "system_open",
                    "description",       "GUI Trigger Component",
                    "version",           "1.0.0",
                    "vendor",            "MikaKARASUDA",
                    "category",          "System",
                    "activity_type",     "PERIODIC",
                    "max_instance",      "1",
                    "language",          "Python",
                    "lang_type",         "SCRIPT",
                    ""]

class system_open(OpenRTM_aist.DataFlowComponentBase):
    
    # GUIからの操作を受け取るためのフラグ (クラス変数)
    TRIGGER_REQUESTED = False

    def __init__(self, manager):
        OpenRTM_aist.DataFlowComponentBase.__init__(self, manager)

        # OutPort 1: Camera_cap用 (Boolean)
        self._d_camera_trigger = OpenRTM_aist.instantiateDataType(RTC.TimedBoolean)
        self._cameraTriggerOut = OpenRTM_aist.OutPort("cameraTrigger", self._d_camera_trigger)

        # OutPort 2: Weather_info用 (Boolean)
        self._d_weather_trigger = OpenRTM_aist.instantiateDataType(RTC.TimedBoolean)
        self._weatherTriggerOut = OpenRTM_aist.OutPort("weatherTrigger", self._d_weather_trigger)

    def onInitialize(self):
        # Set OutPort buffers
        self.addOutPort("cameraTrigger", self._cameraTriggerOut)
        self.addOutPort("weatherTrigger", self._weatherTriggerOut)
        return RTC.RTC_OK
    
    def onExecute(self, ec_id):
        # GUIボタンが押された場合のみ処理を実行
        if system_open.TRIGGER_REQUESTED:
            print("[System] GUI Trigger Detected. Sending signals...")
            
            # 1. Camera_capへTrueを送信
            self._d_camera_trigger.data = True
            OpenRTM_aist.setTimestamp(self._d_camera_trigger)
            self._cameraTriggerOut.write()

            # 2. Weather_infoへTrueを送信
            self._d_weather_trigger.data = True
            OpenRTM_aist.setTimestamp(self._d_weather_trigger)
            self._weatherTriggerOut.write()
            
            # フラグをリセット (1回だけ送信)
            system_open.TRIGGER_REQUESTED = False
            
            print("[System] Signals sent successfully.")
            
        return RTC.RTC_OK


def system_openInit(manager):
    profile = OpenRTM_aist.Properties(defaults_str=system_open_spec)
    manager.registerFactory(profile,
                            system_open,
                            OpenRTM_aist.Delete)

def MyModuleInit(manager):
    system_openInit(manager)
    comp = manager.createComponent("system_open")

# --- GUIクラス ---
class LauncherGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("System Launcher")
        self.root.geometry("250x100")
        
        btn = tk.Button(root, text="📋 診断開始 🌟", font=("Arial", 14),
                        bg="#dddddd", command=self.on_click)
        btn.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)
        
    def on_click(self):
        print("[GUI] Start button clicked!")
        system_open.TRIGGER_REQUESTED = True

def main():
    # -----------------------------------------------------------
    # RTM初期化: 引数エラー回避のための強力なクリーンアップ
    # -----------------------------------------------------------
    # sys.argvをプログラム名のみに強制上書きし、外部からの不要な引数を排除
    sys.argv = [sys.argv[0]]
    
    # RTM Manager初期化
    mgr = OpenRTM_aist.Manager.init(sys.argv)
    
    if mgr is None:
        print("Error: Manager init failed.")
        return

    mgr.setModuleInitProc(MyModuleInit)
    mgr.activateManager()
    
    # 非ブロッキングモードでRTMを開始 (GUIを表示するため)
    mgr.runManager(True)
    
    # GUI起動
    print("Starting GUI...")
    root = tk.Tk()
    app = LauncherGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()