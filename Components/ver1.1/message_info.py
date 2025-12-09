#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -*- Python -*-

import sys
import time
import json
import os
import urllib.request
import urllib.error
import urllib.parse

sys.path.append(".")

# Import RTM module
import RTC
import OpenRTM_aist

# コンポーネント仕様
message_info_spec = ["implementation_id", "message_info", 
             "type_name",           "message_info", 
             "description",         "Receives recommendation and sends to LINE", 
             "version",             "1.0.0", 
             "vendor",              "MikaKARASUDA", 
             "category",            "Messaging", 
             "activity_type",       "PERIODIC", 
             "max_instance",        "1", 
             "language",            "Python", 
             "lang_type",           "SCRIPT",
             ""]

class message_info(OpenRTM_aist.DataFlowComponentBase):
    
    def __init__(self, manager):
        OpenRTM_aist.DataFlowComponentBase.__init__(self, manager)

        # InPort: Cosmetics_recからの推薦結果 (TimedString)
        self._d_reccos_send = OpenRTM_aist.instantiateDataType(RTC.TimedString)
        self._reccos_sendIn = OpenRTM_aist.InPort("reccos", self._d_reccos_send)
        
        self._last_sent_recommendation = ""
        
        print("[MessageInfo] コンポーネント初期化完了。")

    def onInitialize(self):
        self.addInPort("reccos", self._reccos_sendIn)
        return RTC.RTC_OK
    
    def onActivated(self, ec_id):
        print("\n[MessageInfo] ▶ アクティブ化されました。データ待機中...")
        return RTC.RTC_OK

    def onDeactivated(self, ec_id):
        print("[MessageInfo] ■ 非アクティブ化されました。")
        return RTC.RTC_OK

    def onExecute(self, ec_id):
        # データが来たときだけ動く
        if self._reccos_sendIn.isNew():
            data = self._reccos_sendIn.read()
            raw_data = data.data
            
            if raw_data:
                # URLエンコードされた文字列を日本語に戻す
                recommendation = urllib.parse.unquote(raw_data)
                
                # 重複チェック (前回と同じ内容は送らない)
                if recommendation != self._last_sent_recommendation:
                    print("\n==================================================")
                    print(f"[MessageInfo] 📩 推薦データを受信しました！")
                    print("--------------------------------------------------")
                    # コンソールには短縮して表示
                    print(f"内容(抜粋): {recommendation[:50]}...") 
                    print("--------------------------------------------------")
                    print("[MessageInfo] LINEサーバーへ送信中...")
                    
                    if self._send_line_message(recommendation):
                        print("[MessageInfo] ✅ LINE送信成功！")
                        print("[MessageInfo] 🎉 全工程が完了しました。次のトリガーまで静かに待機します。")
                        self._last_sent_recommendation = recommendation
                    else:
                        print("[MessageInfo] ❌ LINE送信失敗")
                    print("==================================================\n")
        
        # データが来ていないときは何もしない（ログを出さない）
        return RTC.RTC_OK

    def _send_line_message(self, message_text):
        token = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN")
        user_id = os.environ.get("LINE_USER_ID")
        sender_name = os.environ.get("LINE_SENDER_NAME", "AI美容部員")
        
        if not token or not user_id:
            print("[MessageInfo] エラー: LINE設定(TOKEN/USER_ID)が不足しています")
            return False

        full_message = f"【{sender_name}】\n{message_text}"
        
        url = "https://api.line.me/v2/bot/message/push"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token}'
        }
        data = json.dumps({
            "to": user_id,
            "messages": [{"type": "text", "text": full_message}]
        }).encode('utf-8')

        try:
            req = urllib.request.Request(url, data=data, headers=headers, method='POST')
            with urllib.request.urlopen(req) as res:
                return res.getcode() == 200
        except Exception as e:
            print(f"[MessageInfo] 送信エラー: {e}")
            return False


def message_infoInit(manager):
    profile = OpenRTM_aist.Properties(defaults_str=message_info_spec)
    manager.registerFactory(profile,
                            message_info,
                            OpenRTM_aist.Delete)

def MyModuleInit(manager):
    message_infoInit(manager)
    instance_name_arg = ""
    for arg in sys.argv:
        if arg.startswith("--instance_name="):
            instance_name_arg = arg.replace("--", "?")
            break
    comp = manager.createComponent("message_info" + instance_name_arg)

def main():
    program_name = sys.argv[0]
    sys.argv = [program_name]

    # 設定ファイル生成 (エラー回避のためシンプルに)
    conf_file = "rtc.conf"
    try:
        with open(conf_file, "w") as f:
            f.write("logger.enable: YES\n")
            f.write("logger.log_level: PARANOID\n")
            f.write("corba.nameservers: 127.0.0.1:2809\n")
            f.write("corba.endpoints: 127.0.0.1:\n")
    except: pass

    argv = [program_name, '-f', conf_file]
    mgr = OpenRTM_aist.Manager.init(argv)
    if mgr:
        mgr.setModuleInitProc(MyModuleInit)
        mgr.activateManager()
        print("[MessageInfo] 起動完了。データ待機中...")
        mgr.runManager()

if __name__ == "__main__":
    main()
