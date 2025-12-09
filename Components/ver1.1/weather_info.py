#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -*- Python -*-

import sys
import time
import requests
import json
import os

sys.path.append(".")

# Import RTM module
import RTC
import OpenRTM_aist

# コンポーネント仕様
weather_info_spec = ["implementation_id", "weather_info", 
             "type_name",           "weather_info", 
             "description",         "Fetches weather data from Open-Meteo", 
             "version",             "1.0.0", 
             "vendor",              "MikaKARASUDA", 
             "category",            "Data Fetching", 
             "activity_type",       "PERIODIC", 
             "max_instance",        "1", 
             "language",            "Python", 
             "lang_type",           "SCRIPT",
             ""]

class weather_info(OpenRTM_aist.DataFlowComponentBase):
    
    def __init__(self, manager):
        OpenRTM_aist.DataFlowComponentBase.__init__(self, manager)

        self._d_find_weatherinfo = OpenRTM_aist.instantiateDataType(RTC.TimedBoolean)
        self._find_weatherinfoIn = OpenRTM_aist.InPort("find_weatherinfo", self._d_find_weatherinfo)
        
        self._d_get_weatherinfo = OpenRTM_aist.instantiateDataType(RTC.TimedString)
        self._get_weatherinfoOut = OpenRTM_aist.OutPort("get_weatherinfo", self._d_get_weatherinfo)

        print("[Weather] コンポーネント初期化完了。")

    def onInitialize(self):
        self.addInPort("find_weatherinfo", self._find_weatherinfoIn)
        self.addOutPort("get_weatherinfo", self._get_weatherinfoOut)
        return RTC.RTC_OK
    
    def onExecute(self, ec_id):
        if self._find_weatherinfoIn.isNew():
            data = self._find_weatherinfoIn.read()
            if data.data == True:
                print("[Weather] 起動トリガー受信。天気情報を取得します...")
                
                weather_str = self.fetch_weather()
                
                self._d_get_weatherinfo.data = weather_str
                OpenRTM_aist.setTimestamp(self._d_get_weatherinfo)
                self._get_weatherinfoOut.write()
                
                print(f"[Weather] 送信完了: {weather_str}")
                
        return RTC.RTC_OK

    def fetch_weather(self):
        # 東京の座標
        latitude = "35.6895"
        longitude = "139.6917"
        
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "current": "weather_code,temperature_2m,relative_humidity_2m",
            "timezone": "Asia/Tokyo"
        }

        try:
            response = requests.get(url, params=params, timeout=5)
            response.raise_for_status()
            data = response.json()
            
            current = data.get("current", {})
            temp = current.get("temperature_2m", "N/A")
            humid = current.get("relative_humidity_2m", "N/A")
            code = current.get("weather_code", 0)
            
            # 【修正】日本語を使わず英語で返す (通信エラー回避のため)
            weather_desc = "Clear"
            if code > 3: weather_desc = "Cloudy"
            if code > 50: weather_desc = "Rainy"
            
            # 半角英数字のみの文字列を作成
            return f"Weather:{weather_desc}, Temp:{temp}C, Humidity:{humid}%"

        except Exception as e:
            print(f"[Weather] API Error: {e}")
            return "Weather Info Fetch Failed"


def weather_infoInit(manager):
    profile = OpenRTM_aist.Properties(defaults_str=weather_info_spec)
    manager.registerFactory(profile,
                            weather_info,
                            OpenRTM_aist.Delete)

def MyModuleInit(manager):
    weather_infoInit(manager)
    instance_name_arg = ""
    for arg in sys.argv:
        if arg.startswith("--instance_name="):
            instance_name_arg = arg.replace("--", "?")
            break
    comp = manager.createComponent("weather_info" + instance_name_arg)

def main():
    program_name = sys.argv[0]
    sys.argv = [program_name]

    conf_file = "rtc.conf"
    try:
        with open(conf_file, "w") as f:
            f.write("corba.nameservers: 127.0.0.1:2809\n")
            f.write("corba.endpoints: 127.0.0.1:\n")
            f.write("logger.enable: YES\n")
    except:
        pass

    argv = [program_name, '-f', conf_file]
    mgr = OpenRTM_aist.Manager.init(argv)
    if mgr:
        mgr.setModuleInitProc(MyModuleInit)
        mgr.activateManager()
        print("[Weather] 起動しました。待機中...")
        mgr.runManager()

if __name__ == "__main__":
    main()
