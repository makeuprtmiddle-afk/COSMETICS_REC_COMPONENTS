#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -*- Python -*-

import sys
import time
import tkinter as tk
from tkinter import ttk
import threading
import os

sys.path.append(".")

# Import RTM module
import RTC
import OpenRTM_aist

# コンポーネント仕様
system_open_spec = ["implementation_id", "system_open", 
             "type_name",           "system_open", 
             "description",         "GUI Trigger & User Info Input", 
             "version",             "1.0.0", 
             "vendor",              "MikaKARASUDA", 
             "category",            "System", 
             "activity_type",       "PERIODIC", 
             "max_instance",        "1", 
             "language",            "Python", 
             "lang_type",           "SCRIPT",
             ""]

class system_open(OpenRTM_aist.DataFlowComponentBase):
    
    # GUIからの操作データを受け取るためのクラス変数
    TRIGGER_REQUESTED = False
    USER_PROFILE_DATA = ""

    def __init__(self, manager):
        OpenRTM_aist.DataFlowComponentBase.__init__(self, manager)

        # OutPort 1: Camera_cap用 (Boolean)
        self._d_camera_trigger = OpenRTM_aist.instantiateDataType(RTC.TimedBoolean)
        self._cameraTriggerOut = OpenRTM_aist.OutPort("cameraTrigger", self._d_camera_trigger)

        # OutPort 2: Weather_info用 (Boolean)
        self._d_weather_trigger = OpenRTM_aist.instantiateDataType(RTC.TimedBoolean)
        self._weatherTriggerOut = OpenRTM_aist.OutPort("weatherTrigger", self._d_weather_trigger)

        # OutPort 3: Cosmetics_rec用 ユーザー情報 (WString: 日本語対応)
        self._d_userinfo = OpenRTM_aist.instantiateDataType(RTC.TimedWString)
        self._userinfoOut = OpenRTM_aist.OutPort("userinfo", self._d_userinfo)

    def onInitialize(self):
        # Set OutPort buffers
        self.addOutPort("cameraTrigger", self._cameraTriggerOut)
        self.addOutPort("weatherTrigger", self._weatherTriggerOut)
        self.addOutPort("userinfo", self._userinfoOut)
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

            # 3. Cosmetics_recへユーザー情報を送信
            self._d_userinfo.data = system_open.USER_PROFILE_DATA
            OpenRTM_aist.setTimestamp(self._d_userinfo)
            self._userinfoOut.write()
            print(f"[System] ユーザー情報を送信: {system_open.USER_PROFILE_DATA}")
            
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
    
    instance_name_arg = ""
    for arg in sys.argv:
        if arg.startswith("--instance_name="):
            instance_name_arg = arg.replace("--", "?")
            break

    comp = manager.createComponent("system_open" + instance_name_arg)

# --- かわいいGUIクラス ---
class SystemLauncherGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Cosmetics Recommender")
        self.root.geometry("480x550")
        
        # カラーパレット (かわいい系)
        self.colors = {
            "bg": "#FFF0F5",        # LavenderBlush (背景)
            "frame_bg": "#FFFFFF",  # White (入力エリア背景)
            "title": "#DB7093",     # PaleVioletRed (タイトル文字)
            "label": "#696969",     # DimGray (ラベル文字)
            "btn_bg": "#FFB6C1",    # LightPink (ボタン背景)
            "btn_fg": "#FFFFFF",    # White (ボタン文字)
            "btn_active": "#FF69B4" # HotPink (ボタン押下時)
        }
        
        # フォント設定
        self.title_font = ("Meiryo UI", 18, "bold")
        self.label_font = ("Meiryo UI", 10)
        self.entry_font = ("Meiryo UI", 10)
        
        # 全体の背景設定
        self.root.configure(bg=self.colors["bg"])
        
        # メインフレーム
        main_frame = tk.Frame(root, bg=self.colors["bg"], padx=20, pady=20)
        main_frame.pack(fill="both", expand=True)

        # タイトルラベル
        title_label = tk.Label(main_frame, text="✨ 化粧品推薦システム ✨", 
                               font=self.title_font, bg=self.colors["bg"], fg=self.colors["title"])
        title_label.pack(pady=(0, 15))
        
        # 入力フォームエリア (白いカード風)
        input_frame = tk.Frame(main_frame, bg=self.colors["frame_bg"], bd=1, relief="flat", padx=20, pady=20)
        input_frame.pack(fill="x", pady=5)

        # --- 1. 年齢 ---
        tk.Label(input_frame, text="年齢", font=self.label_font, bg=self.colors["frame_bg"], fg=self.colors["label"]).pack(anchor="w")
        self.entry_age = tk.Entry(input_frame, font=self.entry_font, bg="#FAFAFA", relief="solid", bd=1)
        self.entry_age.pack(fill="x", pady=(0, 10), ipady=3)

        # --- 2. 性別 ---
        tk.Label(input_frame, text="性別", font=self.label_font, bg=self.colors["frame_bg"], fg=self.colors["label"]).pack(anchor="w")
        self.combo_gender = ttk.Combobox(input_frame, values=["女性", "男性", "その他"], state="readonly", font=self.entry_font)
        self.combo_gender.current(0)
        self.combo_gender.pack(fill="x", pady=(0, 10))

        # --- 3. 悩み ---
        tk.Label(input_frame, text="悩み (ex. ニキビ、乾燥)", font=self.label_font, bg=self.colors["frame_bg"], fg=self.colors["label"]).pack(anchor="w")
        self.entry_worry = tk.Entry(input_frame, font=self.entry_font, bg="#FAFAFA", relief="solid", bd=1)
        self.entry_worry.pack(fill="x", pady=(0, 10), ipady=3)

        # --- 4. 提案する化粧品の種類 ---
        tk.Label(input_frame, text="提案してほしい種類 (ex. 化粧水)", font=self.label_font, bg=self.colors["frame_bg"], fg=self.colors["label"]).pack(anchor="w")
        self.entry_request = tk.Entry(input_frame, font=self.entry_font, bg="#FAFAFA", relief="solid", bd=1)
        self.entry_request.pack(fill="x", pady=(0, 10), ipady=3)

        # --- 5. 持っている化粧品 (複数行対応) ---
        tk.Label(input_frame, text="持っている化粧品 (※正式名称)", font=self.label_font, bg=self.colors["frame_bg"], fg=self.colors["label"]).pack(anchor="w")
        # ★ここを変更: Entry -> Text (高さ3行)
        self.entry_own = tk.Text(input_frame, height=3, font=self.entry_font, bg="#FAFAFA", relief="solid", bd=1)
        self.entry_own.pack(fill="x", pady=(0, 10))

        # 起動ボタン
        self.btn_start = tk.Button(main_frame, text="診断スタート (Start) 💖", font=("Meiryo UI", 12, "bold"), 
                                   bg=self.colors["btn_bg"], fg=self.colors["btn_fg"], 
                                   activebackground=self.colors["btn_active"], activeforeground="white",
                                   relief="flat", cursor="hand2", command=self.on_start_click)
        self.btn_start.pack(pady=20, ipadx=30, ipady=10)
        
    def on_start_click(self):
        # 入力値を取得
        age = self.entry_age.get()
        gender = self.combo_gender.get()
        worry = self.entry_worry.get()
        request = self.entry_request.get()
        # Textウィジェットからの取得は "1.0" から "end-1c" (最後の改行を除く) まで
        own_items = self.entry_own.get("1.0", "end-1c").replace("\n", " ") 
        
        # AIへ送るプロンプト用に整形
        profile_str = (f"年齢:{age}, 性別:{gender}, 悩み:{worry}, "
                       f"提案希望:{request}, 所持品:{own_items}")
        
        print(f"[GUI] Start button clicked! Profile: {profile_str}")
        
        # コンポーネントへデータを渡す
        system_open.USER_PROFILE_DATA = profile_str
        system_open.TRIGGER_REQUESTED = True

def main():
    # RTM初期化
    program_name = sys.argv[0]
    sys.argv = [program_name]

    # 設定ファイル生成
    conf_file = "rtc.conf"
    try:
        with open(conf_file, "w") as f:
            f.write("corba.nameservers: 127.0.0.1:2809\n")
            f.write("corba.endpoints: 127.0.0.1:\n")
            f.write("logger.enable: YES\n")
    except Exception as e:
        print(f"Warning: Failed to create {conf_file}: {e}")

    argv = [program_name, '-f', conf_file]
    
    mgr = OpenRTM_aist.Manager.init(argv)
    if mgr is None:
        print("ERROR: RTM Managerの初期化に失敗しました。")
        return

    mgr.setModuleInitProc(MyModuleInit)
    mgr.activateManager()
    
    # GUIを表示するため非ブロッキングモードで実行
    mgr.runManager(True)
    
    print("Starting GUI...")
    root = tk.Tk()
    app = SystemLauncherGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()