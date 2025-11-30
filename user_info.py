#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -*- Python -*-

import sys
import time
sys.path.append(".")

# Import RTM module
import RTC
import OpenRTM_aist

user_info_spec = ["implementation_id", "user_info", 
             "type_name",           "user_info", 
             "description",         "Provides User Profile Data", 
             "version",             "1.0.0", 
             "vendor",              "MikaKARASUDA", 
             "category",            "Database", 
             "activity_type",       "PERIODIC", 
             "max_instance",        "1", 
             "language",            "Python", 
             "lang_type",           "SCRIPT",
             ""]

class user_info(OpenRTM_aist.DataFlowComponentBase):
    
    def __init__(self, manager):
        OpenRTM_aist.DataFlowComponentBase.__init__(self, manager)

        self._d_trigger = OpenRTM_aist.instantiateDataType(RTC.TimedBoolean)
        self._triggerIn = OpenRTM_aist.InPort("trigger", self._d_trigger)
        
        self._d_userdata = OpenRTM_aist.instantiateDataType(RTC.TimedString)
        self._userdataOut = OpenRTM_aist.OutPort("userinfo", self._d_userdata)

        # 【修正】英語のみのプロフィールにする (通信エラー回避)
        self._user_profile = "Age:16s, Gender:Female, SkinType:Dry, Concern:acne, Preference:cheap"
        
        print("[UserInfo] コンポーネント初期化完了。")

    def onInitialize(self):
        self.addInPort("trigger", self._triggerIn)
        self.addOutPort("userinfo", self._userdataOut)
        return RTC.RTC_OK
    
    def onExecute(self, ec_id):
        if self._triggerIn.isNew():
            data = self._triggerIn.read()
            if data.data == True:
                print("[UserInfo] 起動トリガー受信。ユーザー情報を送信します。")
                
                self._d_userdata.data = self._user_profile
                OpenRTM_aist.setTimestamp(self._d_userdata)
                self._userdataOut.write()
                
                print(f"[UserInfo] 送信完了: {self._user_profile}")
        
        return RTC.RTC_OK


def user_infoInit(manager):
    profile = OpenRTM_aist.Properties(defaults_str=user_info_spec)
    manager.registerFactory(profile,
                            user_info,
                            OpenRTM_aist.Delete)

def MyModuleInit(manager):
    user_infoInit(manager)
    instance_name_arg = ""
    for arg in sys.argv:
        if arg.startswith("--instance_name="):
            instance_name_arg = arg.replace("--", "?")
            break
    comp = manager.createComponent("user_info" + instance_name_arg)

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
        print("[UserInfo] 起動しました。待機中...")
        mgr.runManager()

if __name__ == "__main__":
    main()