#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -*- Python -*-

import sys
import time
import requests
import json
import os
import traceback
import urllib.parse

sys.path.append(".")

# Import RTM module
import RTC
import OpenRTM_aist

# コンポーネント仕様
cosmetics_rec_spec = ["implementation_id", "cosmetics_rec", 
             "type_name",           "cosmetics_rec", 
             "description",         "Recommend Cosmetics based on Skin and Weather", 
             "version",             "1.0.0", 
             "vendor",              "MikaKARASUDA", 
             "category",            "Recommend", 
             "activity_type",       "PERIODIC", 
             "max_instance",        "1", 
             "language",            "Python", 
             "lang_type",           "SCRIPT",
             ""]

class cosmetics_rec(OpenRTM_aist.DataFlowComponentBase):
    
    def __init__(self, manager):
        OpenRTM_aist.DataFlowComponentBase.__init__(self, manager)

        # InPort
        self._d_userinfo = OpenRTM_aist.instantiateDataType(RTC.TimedString)
        self._userinfoIn = OpenRTM_aist.InPort("userinfo", self._d_userinfo)
        
        self._d_rednum = OpenRTM_aist.instantiateDataType(RTC.TimedFloat)
        self._rednumIn = OpenRTM_aist.InPort("rednum", self._d_rednum)
        
        self._d_weatherinfo = OpenRTM_aist.instantiateDataType(RTC.TimedString)
        self._weatherinfoIn = OpenRTM_aist.InPort("weatherinfo", self._d_weatherinfo)
        
        # OutPort
        self._d_reccos = OpenRTM_aist.instantiateDataType(RTC.TimedString)
        self._reccosOut = OpenRTM_aist.OutPort("reccos", self._d_reccos)
        
        # 受信確認フラグ
        self._has_user_info = False
        self._has_red_num = False
        self._has_weather_info = False
        
        self._current_user_info = ""
        self._current_red_num = 0.0
        self._current_weather_info = ""
        
        print("[CosmeRec] コンポーネント初期化完了。")

    def onInitialize(self):
        self.addInPort("userinfo", self._userinfoIn)
        self.addInPort("rednum", self._rednumIn)
        self.addInPort("weatherinfo", self._weatherinfoIn)
        self.addOutPort("reccos", self._reccosOut)
        return RTC.RTC_OK
    
    def onExecute(self, ec_id):
        try:
            # 1. データ受信
            if self._userinfoIn.isNew():
                self._current_user_info = self._userinfoIn.read().data
                self._has_user_info = True
                print(f"[CosmeRec] ✅ ユーザー情報受信")

            if self._rednumIn.isNew():
                self._current_red_num = float(self._rednumIn.read().data)
                self._has_red_num = True
                print(f"[CosmeRec] ✅ 赤みスコア受信: {self._current_red_num:.2f}")

            if self._weatherinfoIn.isNew():
                self._current_weather_info = self._weatherinfoIn.read().data
                self._has_weather_info = True
                print(f"[CosmeRec] ✅ 天気情報受信")

            # 2. 3つ揃ったら実行
            if self._has_user_info and self._has_red_num and self._has_weather_info:
                print("--------------------------------------------------")
                print("[CosmeRec] ✨ データが揃いました。Gemini API呼び出し中...")
                
                api_key = os.environ.get("GEMINI_API_KEY")
                recommendation = ""
                
                if not api_key:
                    print("[CosmeRec] ❌ エラー: GEMINI_API_KEYがありません")
                    recommendation = "システムエラー: APIキー未設定"
                else:
                    # ★★★★★ ここを編集！ (具体的な指示内容) ★★★★★
                    prompt = (
                        "以下の情報に基づき、ユーザーに最適な化粧品を2個推薦してください。"
                        "特に「肌の赤み」と「現在の天気」の関係性を考慮し、なぜその商品が良いのか論理的に説明してください。また、親しみやすいように絵文字を適度に使用してください。"
                        "出力は箇条書きで見やすく、300文字以内、出力結果を太字やMarkdown方式にするための＊は消してください。"
                        "推薦する化粧品は実在するものにしてください。"
                        "また、箇条書きの項目は次のように書いてください：〈商品名〉〈おおよその価格〉〈おすすめポイント〉〈効果〉〈使用方法〉"
                        f"\n[肌の状態（赤み指数）]: {self._current_red_num:.2f}% (高いほど赤みが強い)"
                        f"\n[ユーザー情報]: {self._current_user_info}"
                        f"\n[現在の気象情報]: {self._current_weather_info}"
                    )
                    # ★★★★★★★★★★★★★★★★★★★★★★★★★★★
                    
                    recommendation = self._call_gemini_api(prompt, api_key)

                if recommendation:
                    print("[CosmeRec] 📤 結果を送信します...")
                    
                    # URLエンコードして送信
                    safe_message = urllib.parse.quote(recommendation)
                    
                    self._d_reccos.data = safe_message
                    OpenRTM_aist.setTimestamp(self._d_reccos)
                    self._reccosOut.write()
                    print("[CosmeRec] ✅ 送信完了")
                
                # フラグクリア
                self._has_user_info = False
                self._has_red_num = False
                self._has_weather_info = False
                print("--------------------------------------------------")

        except Exception as e:
            print(f"[CosmeRec] エラー: {e}")
            traceback.print_exc()
            
        return RTC.RTC_OK

    def _call_gemini_api(self, prompt, api_key):
        apiUrl = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-09-2025:generateContent?key={api_key}"
        headers = {'Content-Type': 'application/json'}
        
        # ★★★★★ ここを編集！ (AIのキャラクター設定) ★★★★★
        system_instruction = "あなたは世界一の美容アドバイザーです。専門的なアドバイスを具体的な商品名とともに提案してください。"
        # ★★★★★★★★★★★★★★★★★★★★★★★★★★★
        
        payload = {
            "contents": [{ "parts": [{ "text": prompt }] }],
            "systemInstruction": { "parts": [{ "text": system_instruction }] }
        }
        try:
            response = requests.post(apiUrl, headers=headers, json=payload, timeout=30)
            if response.status_code == 200:
                return response.json()['candidates'][0]['content']['parts'][0]['text']
            return f"AIエラー: {response.status_code}"
        except Exception as e:
            return f"通信エラー: {e}"


def cosmetics_recInit(manager):
    profile = OpenRTM_aist.Properties(defaults_str=cosmetics_rec_spec)
    manager.registerFactory(profile, cosmetics_rec, OpenRTM_aist.Delete)

def MyModuleInit(manager):
    cosmetics_recInit(manager)
    instance_name_arg = ""
    for arg in sys.argv:
        if arg.startswith("--instance_name="):
            instance_name_arg = arg.replace("--", "?")
            break
    comp = manager.createComponent("cosmetics_rec" + instance_name_arg)

def main():
    program_name = sys.argv[0]
    sys.argv = [program_name]
    
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
        print("[CosmeRec] 起動完了。")
        mgr.runManager()

if __name__ == "__main__":
    main()