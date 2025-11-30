# COSMETICS_REC_COMPONENTS

<h2>目的</h2>
　拡大が続く化粧品市場において、利用者は季節変動や日々の肌コンディションといった多様な要因に基づき、パーソナライズされた製品選定が求められている。この課題に対応するため、私たちはAIを活用した化粧品選定システムを開発した。
本システムは、気象情報、利用者の年齢や肌の悩みに関する情報、および利用者の肌の赤みを数値化したデータの3種類の情報を入力プロンプトとして統合する。このプロンプトに基づき、AIが個々の利用者に最適な化粧品を選出する。

<h2>コンポーネント概要</h2>
・System_open<br>
システムの起動<br>
・Camera_launch<br>
カメラでの撮影<br>
----<br>
・Weather_info<br>
Open-Meteo APIからの気象情報の取得<br>
・User_info<br>
ユーザーの基本情報（年齢・肌質・肌悩みなど）の提供<br>
・Skinana_red<br>
Camera_launchで撮影した画像を定量的に分析し、肌の赤みを数値化する。<br>
----<br>
・Cosmetics_rec<br>
Weather_info, User_info, Skinana_redからの情報を統合し、生成AIを用いて最適な化粧品を推薦する。<br>
・Message_info<br>
Cosmetics_recで推薦した内容をMessaging APIを用いて公式LINEから通知する。<br>

<h2>仕様</h2>
・言語：Python<br>
・OS：Windows 11<br>

<h2>ドキュメント</h2>
・[マニュアル]()
