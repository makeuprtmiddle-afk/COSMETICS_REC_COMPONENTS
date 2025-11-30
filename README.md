# COSMETICS_REC_COMPONENTS

<h2>目的</h2>
　拡大が続く化粧品市場において、利用者は季節変動や日々の肌コンディションといった多様な要因に基づき、パーソナライズされた製品選定が求められている。この課題に対応するため、私たちはAIを活用した化粧品選定システムを開発した。
本システムは、気象情報、利用者の年齢や肌の悩みに関する情報、および利用者の肌の赤みを数値化したデータの3種類の情報を入力プロンプトとして統合する。このプロンプトに基づき、AIが個々の利用者に最適な化粧品を選出する。<br>
<br>

<h2>コンポーネント概要</h2>
・System_open - システムの起動<br>
〈機能〉<br>
Tkinterを用いたGUI画面に「起動ボタン」を表示する。ボタンが押されると、カメラと気象情報取得コンポーネントへ同時に起動信号を送る。<br>
〈入出力〉<br>
・OutPort:cameraTrigger (Boolean), weatherTrigger (Boolean)<br>
〈補足〉<br>
当初、User_infoコンポーネントには独立した起動信号を割り当てる設計としていたが、Weather_info（気象情報取得）と実行タイミングが完全に同期していることを踏まえ、システム構成の簡素化を図るため、今回は weatherTrigger 信号を分岐させて共用する接続構成を採用した。<br>
<br>
-------------<br>
<br>
・Camera_launch - カメラでの撮影<br>
〈機能〉<br>
トリガー信号を受け取るとUSBカメラを起動し、静止画をキャプチャする。撮影した画像はローカルストレージに保存し、その「ファイルパス」を次の工程へ送信する（通信負荷軽減のため）。<br>
〈入出力〉<br>
・InPort: find_weatherinfo (Boolean)<br>
・OutPort: get_weatherinfo (String)<br>
<br>
-------------<br>
<br>
・Weather_info - Open-Meteo APIからの気象情報の取得<br>
〈機能〉<br>
Open-Meteo APIを使用し、指定座標（東京など）の「天気・気温・湿度」を取得する。UV指数などのパラメータを含めたテキストデータを作成して送信する。<br>
〈入出力〉<br>
・InPort: takepic (Boolean)<br>
・OutPort: picture (String / FilePath)<br>
<br>
-------------<br>
<br>
・User_info - ユーザーの基本情報（年齢・肌質・肌悩みなど）の提供<br>
〈機能〉<br>
事前に設定されたユーザープロファイルを保持しており、システム起動の合図に合わせて推薦エンジンへ情報を送信する。<br>
〈入出力〉<br>
・InPort: trigger (Boolean)<br>
・OutPort: userinfo (String)<br>
<br>
-------------<br>
<br>
・Skinana_red - Camera_launchで撮影した画像を定量的に分析し、肌の赤みを数値化<br>
〈機能〉<br>
受信したファイルパスから画像を読み込み、OpenCVを用いてHSV色空間変換を行う。赤色領域のマスクを作成し、顔全体に対する赤色ピクセルの割合（%）を算出する。<br>
〈入出力〉<br>
・InPort: tookpic (String / FilePath)<br>
・OutPort: rednum (Float)<br>
<br>
-------------<br>
<br>
・Cosmetics_rec - Weather_info, User_info, Skinana_redからの情報を統合し、生成AIを用いて最適な化粧品を推薦<br>
〈機能〉<br>
「肌の赤み数値」「気象情報」「ユーザー情報」の3つが揃うのを待機する。揃い次第、Google Gemini APIへプロンプトを送信し、論理的根拠（天気と肌状態の関係性など）を含めた推薦文を生成する。通信エラー回避のため、結果をURLエンコードして出力する。<br>
〈入出力〉<br>
・InPort: rednum (Float), weatherinfo (String), userinfo (String)<br>
・OutPort: reccos (String / URL Encoded)<br>
〈補足〉
プロンプトは以下のように設定している。
「以下の情報に基づき、ユーザーに最適な化粧品を2個推薦してください。特に「肌の赤み」と「現在の天気」の関係性を考慮し、なぜその商品が良いのか論理的に説明してください。また、親しみやすいように絵文字を適度に使用してください。出力は箇条書きで見やすく、300文字以内、出力結果を太字やMarkdown方式にするための＊は消してください。推薦する化粧品は実在するものにしてください。また、箇条書きの項目は次のように書いてください：〈商品名〉〈おおよその価格〉〈おすすめポイント〉〈効果〉〈使用方法〉<br>
[肌の状態（赤み指数）]: {self._current_red_num:.2f}% (高いほど赤みが強い)<br>
[ユーザー情報]: {self._current_user_info}<br>
[現在の気象情報]: {self._current_weather_info}」<br>
<br>
-------------<br>
<br>
・Message_info - Cosmetics_recで推薦した内容をMessaging APIを用いて公式LINEから通知<br>
〈機能〉<br>
受信したエンコード済みの推薦文をデコード（復元）する。LINE Messaging APIを使用して、指定されたユーザーIDへプッシュ通知を送信する。<br>
〈入出力〉<br>
・InPort: reccos (String)<br>
・OutPort: LINEアプリへのプッシュ通知 (HTTP Request)<br>
<br>

<h2>仕様</h2>
・言語：Python 3.10+<br>
・OS：Windows 11<br>

<h2>注意事項</h2>
■ API類の環境変数設定について<br>
GeminiのAPIキーとLINE_CHANNNEL_ACCESS, LINE_USER_IDは環境変数から設定する仕様にした。<br>
仕様上個人情報になってしまうため、こちらには記載しない。<br>
■ システム起動について<br>
System_openが表示するGUIのボタンを押すと、全体の動作が開始される。<br>
■ このリポジトリ内のImagesフォルダについて<br>
この中には私たちの検証時に用いられた赤みの検証用の写真を添付した。実際に人のニキビの写真になるため、閲覧時は注意してください。<br>
current_face.jpg -> 実際の写真<br>
debug_mask -> 実際の写真で赤みと判断された場所をマスクしたもの<br>
<br>

<h2>参考資料</h2>
・[マニュアル]()
・[使用した肌の画像](https://github.com/makeuprtmiddle-afk/COSMETICS_REC_COMPONENTS/tree/main/Images)
