import copy, hashlib, hmac, json, uuid
from datetime import datetime
import streamlit as st

st.set_page_config(page_title="ハードウェア保守案件管理", page_icon="🛠️", layout="wide")

# シンプルな単一ユーザー認証設定。パスワード平文は保存していません。
AUTH_USERNAME = "baofu"
AUTH_PASSWORD_SALT = "21a88771258a5305ce33c172be844305"
AUTH_PASSWORD_HASH = "d843d8ce3e7f6a65950cc2e0de871f4652dfa828209a2d34fdbf810f99cd837a"
STATUS=["未対応","切り分け中","PFU依頼待ち","部材・作業待ち","作業中","完了"]
CHECKS=["電源・LED状態を確認","エラーメッセージ・ログを収集","ケーブル・接続状態を確認","再起動可否と影響を確認","オプションカード情報を確認","お客様提供情報シートを回収"]

PROCESS_STEPS = [
 "1. 障害受付と契約内容の確認", "2. お客様申告内容と影響範囲のヒアリング", "3. 製品別の障害切り分け", "4. ハードウェア故障判定と必要情報の回収",
 "5. 保守機・オプションカード・付属品の選定", "6. バックアップ、ファームウェア、ライセンス等のキッティング情報確認", "7. PFUへ初期依頼", "8. 保守機のキッティングと正常性確認",
 "9. お客様と交換日時を調整しPFUへ正式依頼", "10. 現地交換、動作確認、障害機回収", "11. 作業報告確認とケースクローズ", "12. 必要に応じてRMA、修理、在庫補充"
]
RUNBOOK = {
 "共通切り分け": [
  ("受付・影響確認", ["お客様申告内容、発生日時、継続・断続を確認", "サービス停止、性能低下、冗長性への影響を確認", "契約番号、契約種別、対象拠点、緊急度を確認", "対象機器の型番、筐体S/N、OS・ファームウェア版を確認"]),
  ("外観・電源・環境", ["電源ケーブル、PDU、ブレーカー、電源冗長構成を確認", "前面・背面LED、ディスプレイ、アラーム表示を記録", "異音、異臭、過熱、ファン停止、破損を確認", "設置環境、温度、ラック、最近の配線・電源作業有無を確認"]),
  ("接続性", ["管理GUI、SSH、シリアルコンソールへの接続可否を確認", "管理IP、サブネット、デフォルトゲートウェイを確認", "リンクLED、ポート状態、ケーブル、対向機器を確認", "可能であれば別ケーブル、別ポートで再現性を確認"]),
  ("証跡・再現", ["エラー画面、LED写真、発生時刻、操作内容を保存", "セルフチェック、診断結果、イベント・アラームを収集", "再起動実施の可否と業務影響をお客様に確認", "切り分け結果と故障被疑箇所を明記"]),
 ],
 "SSP": [
  ("SSP固有確認", ["マシン起動可否と前面LED状態を確認", "SSHとシリアルコンソールの反応を確認", "SNMPトラップ設定と受信状況を確認", "搭載アプリケーション、個数、版数を確認", "SSP本体とOption NICの型番、S/N、スロット位置を確認"]),
  ("バックアップ・リストア判断", ["バックアップファイルの有無、取得日時、種類、リストアパスワードを確認", "バックアップ作成時の版数と導入予定ファームウェアを一致させる", "バックアップがない場合は希望版数を確認し、ファームウェア導入と交換範囲を明確化", "3つ以上のアプリケーションがある場合はキッティング対象を調整"]),
 ],
 "SSL Visibility": [
  ("SSLV固有確認", ["起動可否、前面パネル表示、LED状態を確認", "SSH、シリアル、管理コンソールへのログイン可否を確認", "管理ネットワークとホスト名情報を確認", "ライセンス、ポリシー、Host Categorization利用有無を確認", "DiagnosticsとBackup、Full BackupまたはPolicy・PKI・Platformの各ファイルを確認"]),
 ],
 "故障判定ゲート": [
  ("交換へ進む条件", ["契約と対象S/Nが一致している", "外部要因、ケーブル、電源、対向機器を除外した", "再起動やセルフチェックの結果を記録した", "交換対象が筐体か部品かOption NICか特定した", "お客様またはサポート部門と交換判断を共有した"]),
 ]
}
WORK_STEPS = {
 "キッティング前": ["お客様提供情報シートを確認", "対象型番、筐体S/N、契約内容を照合", "交換用筐体、Option NIC、電源ケーブル、ラックキット、シリアルケーブル、LANケーブル、作業PCを準備", "ファームウェア、アップグレードパス、作業手順書を準備", "バックアップ、リストアパスワード、ライセンス、アクティベーション情報を確認"],
 "SSPキッティング": ["保守機を初期化", "保守機単体の正常性を確認", "ISGファームウェアを設定", "必要なSG VAまたはCAS VAを作成", "バックアップ版数に合わせてファームウェアを導入", "リストア後の情報取得、差分確認、正常性確認", "キッティング完了結果を記録"],
 "現地交換": ["入館手続きと作業員情報を確認", "障害機の型番、S/N、配線、Option NIC位置を現物確認", "障害機を安全にシャットダウン", "ケーブルとスロット位置を記録して機器を入れ替え", "保守機を起動し、LED・管理接続・アプリケーション状態を確認", "必要な設定、ライセンス、コンテンツフィルター等を確認", "お客様による業務動作確認を実施", "障害機を回収し、退館報告と作業報告書を受領"],
 "完了・RMA": ["作業結果、交換前後S/N、交換部品を記録", "障害機を指定先へ返送", "必要に応じてメーカーケースとRMA申請を作成", "交換パーツ到着後に修理・組立・動作確認", "修理済み機器を保守在庫へ戻す", "案件をクローズしJSONを保存"]
}
PART_RULES = [
 ("契約", "オンサイト、先出し・後出しセンドバック、特別対応のどれかを確認し、作業範囲を確定する"),
 ("筐体", "対象製品ファミリ、モデル、性能区分、筐体S/Nを一致させる"),
 ("Option NIC", "有無、種類、型番、S/N、枚数、スロット番号を現行機と照合する"),
 ("ファームウェア", "バックアップ作成時の版数、希望版数、アップグレードパスを確認する"),
 ("アプリケーション", "SSP上のSG VA、CAS VA、SSL Visibilityなど、構成とキッティング対象を確認する"),
 ("ライセンス", "スワップ、ライセンスファイル、アクティベーションコードの必要性を確認する"),
 ("付属品", "電源ケーブル、ラックキット、シリアルケーブル、LANケーブル等の必要数を確認する"),
 ("在庫", "保守機S/N、部品番号、配備倉庫、正常性確認結果、予約・発送可否を確認する")
]
TEMPLATES={
"customer": {"title":"顧客に依頼時","body":'''件名:TDSYNNEX -【情報提供のお願い】{ケース番号} {お客様名}\n\n{お客様名} ご担当者様\n\nいつもお世話になっております。\nTD SYNNEXの{自社担当者名}です。\n\nハードウェア障害の確認およびオンサイト対応の手配にあたり、以下の情報をご提供ください。\n\n【お客様情報】\n契約番号：{契約番号}\n機器設置住所：{機器設置住所}\nお客様名：{お客様名}\nご担当者名：{お客様ご担当者名}\n御連絡先：{お客様連絡先}\n\n【対象機器・障害情報】\n対象機器：{筐体型番}\n対象S/N：{筐体S/N}\nオプションカードの有無：{オプションカードの有無}\nオプションカードの種類：{オプションカードの種類}\nオプションカードのシリアル番号：{オプションカードのS/N}\nオプションカードのスロット番号：{オプションカードのスロット番号}\n障害内容：{障害内容}\n\nあわせて、お客様提供情報シートへのご記入をお願いいたします。\n\n以上、ご確認の程願います。'''},
"pfuInitial":{"title":"PFU初期依頼","body":'''件名:TDSYNNEX -【オンサイト対応依頼】{ケース番号} {お客様名}\n\n株式会社PFU ご担当者様\n\nいつもお世話になっております。\nTD SYNNEXの{自社担当者名}と申します。\n\n掲題のお客様より{製品名}のHW障害について、ご対応をお願いいたします。\n--------------------------------------\n【お客様情報】\n契約番号：{契約番号}\n機器設置住所：{機器設置住所}\nお客様名：{お客様名}\nご担当者名：{お客様ご担当者名}\n御連絡先：{お客様連絡先}\n\n【作業情報】\n対象機器：筐体型番：{筐体型番}\n対象S/N：筐体S/N：{筐体S/N}\n契約内容：{契約内容}\n＊重要ーオプションカードの有無：{オプションカードの有無}\n＊重要ーオプションカードの種類：{オプションカードの種類}\n＊重要ーオプションカードのシリアル番号：{オプションカードのS/N}\n＊重要ーオプションカードのスロット番号：{オプションカードのスロット番号}\n障害内容：{障害内容}\n設置場所：{設置場所}\n\n↓必要時、PFUに依頼\n【作業員情報】\n☆☆☆☆☆☆☆☆☆☆☆☆☆☆☆☆\n入館予定時刻：{入館予定時刻}\n作業員氏名：{作業員氏名}\n電話番号：{作業員電話番号}\n車両情報：{車両情報}\n☆☆☆☆☆☆☆☆☆☆☆☆☆☆☆☆\n--------------------------------------\n\nお客様提供情報シートを添付しますので、ご確認願います。\n\n以上、ご対応のほどよろしくお願いいたします。'''},
"pfuFormal":{"title":"PFU正式依頼","body":'''件名:TDSYNNEX -【オンサイト対応依頼】{ケース番号} {お客様名}\n\n株式会社PFU ご担当者様\n\nいつもお世話になっております。\nTD SYNNEXの{自社担当者名}と申します。\n\n掲題のお客様より{製品名}のHW障害について、ご対応をお願いいたします。\n--------------------------------------\n【お客様情報】\n契約番号：{契約番号}\n機器設置住所：{機器設置住所}\nお客様名：{お客様名}\nご担当者名：{お客様ご担当者名}\n御連絡先：{お客様連絡先}\n\n【作業情報】\n対象機器：筐体型番：{筐体型番}\n対象S/N：筐体S/N：{筐体S/N}\n契約内容：{契約内容}\n＊重要ーオプションカードの有無：{オプションカードの有無}\n＊重要ーオプションカードの種類：{オプションカードの種類}\n＊重要ーオプションカードのシリアル番号：{オプションカードのS/N}\n＊重要ーオプションカードのスロット番号：{オプションカードのスロット番号}\n障害内容：{障害内容}\n設置場所：{設置場所}\n\n作業希望日時：{作業希望日時}\n作業内容：{作業内容}\n\n作業立会会社名：{作業立会会社名}\nご担当者名：{立会ご担当者名}\n電話番号：{立会電話番号}\n\n保守部品：{保守部品}\n保守機S/N：{保守機S/N}\n配備倉庫：{配備倉庫}\n\n最終確認方法：{最終確認方法}\n駐車場使用可否：{駐車場使用可否}\n備考：{備考}\n\n【キッティングに必要な情報】\n・お客様提供情報シート：{お客様提供情報シート}\n・作業手順書：{作業手順書}\n・ファームウェア（アップグレードパスの通知含む）：{ファームウェア}\n・コンフィグファイルの提供：{コンフィグファイル}\n・ライセンスファイルの提供：{ライセンスファイル}\n・アクティベーションコード：{アクティベーションコード}\n\n↓必要時、PFUに依頼\n【作業員情報】\n☆☆☆☆☆☆☆☆☆☆☆☆☆☆☆☆\n入館予定時刻：{入館予定時刻}\n作業員氏名：{作業員氏名}\n電話番号：{作業員電話番号}\n車両情報：{車両情報}\n☆☆☆☆☆☆☆☆☆☆☆☆☆☆☆☆\n\n以上、ご対応のほどよろしくお願いいたします。'''}}

def now(): return datetime.now().isoformat(timespec="seconds")
def new_case(n=1):
 return {"id":uuid.uuid4().hex,"case_no":f"CASE-{datetime.now().year}-{n:03d}","project_name":"","status":"未対応","customer":"","contract_no":"","product":"SP-S210-10","model":"","serial":"","address":"","customer_contact":"","customer_phone":"","contract_type":"","location":"","issue":"","owner":"","option_exists":"","option_type":"","option_serial":"","option_slot":"","preferred_date":"","work_content":"","attendance_company":"","attendance_contact":"","attendance_phone":"","final_check":"","parking":"","remarks":"","info_sheet":"","work_guide":"","firmware":"","config_file":"","license_file":"","activation_code":"","entry_time":"","worker_name":"","worker_phone":"","vehicle":"","diagnosis":"","procedure":"","attachments":"","part_number":"$TD_SYN-SSP-S210-10-PR","replacement_sn":"","warehouse":"東京ロジスティック倉庫","ship_date":"","tracking":"","return_status":"未手配","part_notes":"","checks":[{"label":x,"done":False} for x in CHECKS],"timeline":[],"created_at":now(),"updated_at":now()}
def initial(): return {"schema_version":1,"app":"hardware_case_manager","cases":[new_case()],"templates":copy.deepcopy(TEMPLATES),"saved_at":now()}
def verify(u,p):
 try:
  actual=hashlib.pbkdf2_hmac("sha256",p.encode(),bytes.fromhex(AUTH_PASSWORD_SALT),310000).hex()
  return hmac.compare_digest(u,AUTH_USERNAME) and hmac.compare_digest(actual,AUTH_PASSWORD_HASH)
 except Exception:
  return False
if not st.session_state.get("authenticated"):
 st.title("🔐 ハードウェア保守案件管理ツール");st.caption("ログイン後、JSONを読み込むか新規ケースを作成してください。")
 with st.form("login"):
  u=st.text_input("ユーザー名");p=st.text_input("パスワード",type="password");ok=st.form_submit_button("ログイン",type="primary",use_container_width=True)
 if ok:
  if verify(u,p):st.session_state.authenticated=True;st.rerun()
  else:st.error("ユーザー名またはパスワードが正しくありません。")
 st.stop()
if "data" not in st.session_state:st.session_state.data=initial()
if "current_id" not in st.session_state:st.session_state.current_id=st.session_state.data["cases"][0]["id"]
D=st.session_state.data
def current():return next((c for c in D["cases"] if c["id"]==st.session_state.current_id),None)
def touch(c):c["updated_at"]=now();D["saved_at"]=now()
def json_bytes(obj):return json.dumps(obj,ensure_ascii=False,indent=2).encode("utf-8")
def choose_case():
 if not D["cases"]:st.info("ケースがありません。ケース一覧から新規作成してください。");return None
 labels={f'{c["case_no"]} | {c["customer"] or "未入力"}':c["id"] for c in D["cases"]};keys=list(labels);idx=next((i for i,k in enumerate(keys) if labels[k]==st.session_state.current_id),0);sel=st.selectbox("対象ケース",keys,index=idx);st.session_state.current_id=labels[sel];return current()
with st.sidebar:
 st.title("🛠️ 保守案件管理");page=st.radio("メニュー",["全体の流れ","障害切り分け","作業手順","保守部品選定","ケース管理","案件タイムライン","メールテンプレート","JSONデータ管理"])
 st.divider();st.caption("データはセッション内だけに保持されます。終了前にJSONをダウンロードしてください。")
 if st.button("ログアウト"):st.session_state.clear();st.rerun()
if page=="全体の流れ":
 st.title("ハードウェア修理ランブック")
 st.info("ケース管理よりも、障害切り分け、作業手順、保守機材選定を中心に再構成しています。")
 cols=st.columns(4)
 counts=[("切り分け", "症状・影響・被疑箇所"),("情報回収", "機器・契約・バックアップ"),("機材選定", "筐体・Option NIC・付属品"),("交換完了", "動作確認・回収・RMA")]
 for col,(a,b) in zip(cols,counts): col.metric(a,b)
 st.subheader("全体プロセス")
 for x in PROCESS_STEPS: st.markdown(f"- {x}")
 with st.expander("品質ゲート",expanded=True):
  st.markdown("""- 故障判定前に外部要因を除外する
- 発注・発送前に型番、S/N、Option NIC、契約を二重確認する
- キッティング前にバックアップ版数とファームウェア版数を確認する
- 現地交換後はお客様の業務確認と作業報告を残す
- 終了前に全ケースJSONを保存する""")
elif page=="障害切り分け":
 st.title("障害切り分け")
 c=choose_case()
 if c:
  c.setdefault("runbook_checks",{})
  products=list(RUNBOOK)
  product_tabs=st.tabs(products)
  done=total=0
  for tab,product in zip(product_tabs,products):
   with tab:
    sections=RUNBOOK[product]
    section_tabs=st.tabs([x[0] for x in sections])
    for sec_tab,(section,items) in zip(section_tabs,sections):
     with sec_tab:
      for item in items:
       key=f"{product}|{section}|{item}"; old=c["runbook_checks"].get(key,False)
       v=st.checkbox(item,value=old,key=key+c["id"]);c["runbook_checks"][key]=v;done+=int(v);total+=1
      if product=="SSP" and section=="SSP固有確認":
       st.markdown("""### NMI・確認情報
- SSP-S410では、対象バージョン条件を確認したうえで前面IDボタン長押しによるNMI手順が資料に記載されています。
- LED、SSH、シリアル、SNMPトラップ、MIBを確認します。

```text
SSP前面: [Power] [Status LED] [ID button]
                              └─ 対象条件を確認して操作
```
""")
      if product=="SSL Visibility":
       st.markdown("""### SV-S550 NMI
```text
Menu > Left > Right
```
反応しない場合の電源操作は、影響と承認を確認し、原手順書に従って実施します。
""")
  st.progress(done/total if total else 0,text=f"チェック進捗 {done}/{total}")
  with st.form("triage_notes"):
   d=st.text_area("切り分け結果・故障被疑箇所",c.get("diagnosis",""),height=180)
   a=st.text_area("収集した証跡・添付情報",c.get("attachments",""),height=140)
   if st.form_submit_button("セッションへ反映",type="primary"):c.update(diagnosis=d,attachments=a);touch(c);st.success("反映しました。")
elif page=="作業手順":
 st.title("キッティング・現地交換・完了手順")
 c=choose_case()
 if c:
  c.setdefault("work_checks",{})
  step_tabs=st.tabs(["1. 事前準備","2. コンソール接続","3. 保守機正常性","4. 初期化・ISG設定","5. SG-VA","6. SSLV-VA","7. 現地交換","8. 完了・RMA"])
  with step_tabs[0]:
   st.markdown("""## 1. 事前準備

### キッティング用機材
- メンテナンスデバイス: Windows 10以上、Ethernet、最新Edge、Tera Term等、ファイル比較ツール
- シリアルケーブル: RJ-45 - DB-9pinメス Cisco互換
- LANケーブル、保守機材、標準工具
- ローカルWebサーバー
- ISG、SG-VA、CAS-VA、SSLV-VAの対象ファームウェア
- ライセンスファイル、アクティベーションコード
- お客様提供情報シート、バックアップ、Diagnostics、作業報告書

> **重要:** バックアップを利用する場合、バックアップ作成時の版数にファームウェアを合わせます。バックアップがない場合は、お客様希望版数を確認します。

### IIS利用時の保存場所
```text
C:\inetpub\wwwroot
```
`FST_DELETE`ではありません。

### 原資料の図を読み替えた構成イメージ
```text
[作業PC / MD]
   ├─ LAN ──> SSP Interface 0:0 (Management)
   ├─ Serial ──> SSP Serial Console
   └─ IIS / wwwroot
         ├─ ISG firmware
         ├─ SG/CAS/SSLV image
         └─ trust_package.bctp
```
""")
   for item in WORK_STEPS["キッティング前"]:
    k="prep|"+item;c["work_checks"][k]=st.checkbox(item,c["work_checks"].get(k,False),key=k+c["id"])
  with step_tabs[1]:
   st.markdown("""## 2. コンソール接続

### LAN接続
1. MDに障害機と同一セグメントで、SG/CAS設定IPと重複しないIPを設定します。
2. MDと保守機のInterface 0:0をLANケーブルで接続します。

### シリアル設定
| 項目 | 設定 |
|---|---|
| Speed | 9600 |
| Data | 8 bit |
| Parity | none |
| Stop bit | 1 bit |
| Flow control | none |

Tera Termでは、`設定 > シリアルポート`、`設定 > キーボード > Backspace`を確認します。`ファイル > ログ`で作業ログを開始します。

```text
保存名: 受付No_日付.txt
例: NC14XXXXX_20240101.txt
```

> 作業ログは正常完了の証跡になるため、電源投入前に記録を開始します。

### 画面イメージ
```text
Welcome to the Symantec S410 Series Appliance Serial Console
------------------------- MENU -----------------------------
1) Command Line Interface
2) Setup Console
------------------------------------------------------------
Enter option: 1 または 2
```
""")
  with step_tabs[2]:
   st.markdown("""## 3. 保守機の正常性確認

### 電源投入
- シリアルケーブル接続とログ開始を確認してから電源ボタンを押します。
- 電源ボタンは長押ししません。
- `Press "enter" three times...`が表示されたらEnterを3回押し、`1) Command Line Interface`を選択します。

### モデル・S/N確認
```shell
enable
show json-config
```
確認ポイント:
- `serialNumber`が筐体ラベルおよび指定された保守機S/Nと一致
- `model`が故障機と一致
- `platform`が対象シリーズを示す

### ヘルス確認
```shell
health-monitoring view current
```
CPU、Current Sensors、Fan、Memory、Power Supplies、RAID、Temperature、Voltageが`OK`であることを確認します。`Appliance Certificate Validation Status`以外にNGがある場合は別筐体対応を判断します。

### 原資料の出力イメージ
```text
Metric Name                         State
CPU Utilization                    OK
Current Sensors                    OK
Fan Sensors                        OK
Memory Utilization                 OK
Power Supplies                     OK
RAID raid1-1 Working Members       OK
Temperature Sensors                OK
Voltage Sensors                    OK
```
""")
  with step_tabs[3]:
   st.markdown("""## 4. 保守機初期化・ISG設定

> **警告:** 下記初期化はローカル設定と運用情報を消去します。対象が保守機であることを必ず確認します。

### 工場出荷状態へ初期化
```shell
restore-defaults factory-defaults
```
確認プロンプトで対象を再確認してから実行します。初期化後、Enterを3回押してコンソールを有効化します。

### Setup Console
```text
Press Enter three times
2) Setup Console
Enter option: 2
```
お客様提供情報シートを参照して、ISG IP、サブネットマスク、デフォルトゲートウェイ、DNS、Consoleパスワード、Enableパスワードを設定します。

### 導入済みシステムの確認
```shell
installed-systems view
```

### ライセンス自動更新
```shell
configure
licensing auto-update true
```

### NTP
```shell
configure
ntp
server <NTP_SERVER_IP>
enable
view
```
`<NTP_SERVER_IP>`は実際の値へ置換します。
""")
  with step_tabs[4]:
   st.markdown("""## 5. SG-VA作成・起動

> SG Image ID、ライセンスID、モデル、名称はお客様提供情報シートと一致させます。

### イメージのロード
```shell
enable
configure
images
load http://<WEB_SERVER_IP>/ProxySG_xxxx.bcsi
view
```

### SG-VA作成
```shell
exit
applications
create sg <SG_NAME> model <MODEL> license-id <LICENSE_ID> image-id <SG_IMAGE_ID>
view
```
`STATUS`が`Created`、NAME、TYPE、MODEL、IMAGE ID、LICENSE IDが提供情報と一致することを確認します。

### 起動
```shell
start <SG_NAME>
view
```
`Starting`を経て`Running`になるまで、時間をおいて`view`を再実行します。

### コンソール接続
```shell
attach-console <SG_NAME>
```
Enterを3回押してセットアップを進めます。ISGコンソールへ戻るときは`Ctrl + ]`を使用します。必要時のみ次を使用します。
```shell
attach-console <SG_NAME> force
```

### Web確認
```text
https://<SG-VA_IP>:8082/
```
""")
  with step_tabs[5]:
   st.markdown("""## 6. SSLV-VA作成・設定

### SSLVイメージのロード
```shell
configure
images
load http://<WEB_SERVER_IP>/sslv_6.2.1.1-308357.bcsi
view
```

### ネットワーク定義
```shell
configure
network-definition
create sslv-netdef
edit sslv-netdef add mode shared interfaces 0:0
edit sslv-netdef add mode passthrough interfaces [ 1:0 1:1 2:0 2:1 3:0 3:1 3:2 3:3 ]
view
```

### アプリケーション作成
```shell
applications
create sv license-id <LICENSE_ID> image-id <IMAGE_ID> model <MODEL> network-definition sslv-netdef SSLV1
view
start SSLV1
view
attach-console SSLV1
```
モデル例は原資料に従い、対象筐体とライセンス条件を照合してください。

### ライセンス
```shell
licensing inline passphrase <PASSWORD>
# ライセンス本文を貼り付け、Ctrl+D
licensing view
```

### Full Backupリストア
1. SSLV GUIで`Backup/Restore`を開く
2. `Full Backup`を選択
3. `Allow policies from other appliances`を選択
4. `Enable segment activation`を選択
5. バックアップファイルとパスワードを指定
6. リストア後の再起動を待つ

### Option NIC / セグメント
SSP上の拡張カードはSlot 3です。旧物理SSLVでSlot 3以外を使っていた場合は、リストア後にセグメントのMain/CopyインターフェースをSlot 3へ読み替えて調整します。

```text
例: 旧 6:0,6:1 Main / 6:2,6:3 Copy
        ↓
    新 3:0,3:1 Main / 3:2,3:3 Copy
```
""")
  with step_tabs[6]:
   st.markdown("""## 7. 現地交換

### 故障機取り外し
1. 入館後、故障機の場所、型番、S/N、配線、Option NIC位置を確認
2. ケーブルへタグを付け、交換後も判別できるようにする
3. 故障機のシャットダウンはお客様へ依頼
4. 前面表示の消灯を確認後、全ケーブルを抜線して取り外す

### 交換機設置
1. 必要なレールへ交換
2. 最初は管理ポートのみ接続
3. 電源ケーブルは2本とも接続
4. 起動後、管理画面とHost Categorization等を確認
5. 一度安全にシャットダウン
6. お客様指示に従って通信ポートを接続
7. 再起動してお客様に業務確認を依頼

### シャットダウン例
```shell
enable
shutdown
```
電源ケーブルを抜く場合は、手順書の指示に従い、ディスクLED消灯を確認してから実施します。

### Host Categorization確認
```text
Policies > Host Categorization List
Provider: Blue Coat
Database Status: Up to Date
Last Inquiry: 値が表示されること
```
""")
   for item in WORK_STEPS["現地交換"]:
    k="site|"+item;c["work_checks"][k]=st.checkbox(item,c["work_checks"].get(k,False),key=k+c["id"])
  with step_tabs[7]:
   st.markdown("""## 8. 完了・RMA

### 完了確認
- お客様による業務動作確認
- 交換前後の筐体S/N、Option NIC S/N、保守部品を記録
- PFUの退館報告、作業報告書、ターミナルログを回収
- Diagnostics、画面キャプチャ、差分確認結果を保存
- 障害機を指定先へ返送
- 必要に応じてメーカーケース、RMA申請、修理、在庫戻しを実施
- 最終的に全ケースJSONを保存

### SSLVリストア後の確認例
```text
sosreport-.../networking/ip_addr
sosreport-.../sslv_diags_platform/platform_version.txt
sosreport-.../sslv_diags_pki/sslv_diags_pki.txt
sosreport-.../sslv_diags_policy/sslv_diags_policy.txt
sosreport-.../var/log/user_syslog.log
```
CPU、メモリー、各センサー、証明書、Policy、ネットワーク、ファームウェアを故障機情報と比較します。
""")
   for item in WORK_STEPS["完了・RMA"]:
    k="finish|"+item;c["work_checks"][k]=st.checkbox(item,c["work_checks"].get(k,False),key=k+c["id"])
  st.divider()
  with st.form("procedure"):
   proc=st.text_area("案件固有の作業手順・注意事項",c.get("procedure",""),height=220)
   if st.form_submit_button("セッションへ反映",type="primary"):c["procedure"]=proc;touch(c);st.success("反映しました。")
elif page=="保守部品選定":
 st.title("保守機材の選定")
 c=choose_case()
 if c:
  st.warning("部品番号だけで決めず、契約、筐体モデル、Option NIC、アプリケーション、ファームウェア、ライセンス、付属品を順番に照合してください。")
  for name,rule in PART_RULES:
   with st.expander(name,expanded=True):st.write(rule)
  with st.form("selection"):
   a,b,c1=st.columns(3)
   d={"contract_type":a.text_input("契約内容",c.get("contract_type","")),"product":b.text_input("製品名",c.get("product","")),"model":c1.text_input("筐体型番",c.get("model","")),"serial":a.text_input("障害機S/N",c.get("serial","")),"option_exists":b.text_input("Option NIC有無",c.get("option_exists","")),"option_type":c1.text_input("Option NIC種類・型番",c.get("option_type","")),"option_serial":a.text_input("Option NIC S/N",c.get("option_serial","")),"option_slot":b.text_input("スロット番号",c.get("option_slot","")),"part_number":c1.text_input("選定した保守部品",c.get("part_number","")),"replacement_sn":a.text_input("保守機S/N",c.get("replacement_sn","")),"warehouse":b.text_input("配備倉庫",c.get("warehouse","")),"firmware":c1.text_input("導入ファームウェア",c.get("firmware","")),"work_guide":a.text_input("使用する作業手順書",c.get("work_guide","")),"license_file":b.text_input("ライセンスファイル",c.get("license_file","")),"activation_code":c1.text_input("アクティベーションコード",c.get("activation_code","")),"part_notes":st.text_area("選定根拠、照合結果、注意事項",c.get("part_notes",""),height=180)}
   if st.form_submit_button("選定内容を反映",type="primary"):c.update(d);touch(c);st.success("反映しました。")
 st.subheader("出庫前の最終確認")
 st.markdown("""- 障害機と保守機の製品・モデル整合
- Option NICの種類、枚数、スロット整合
- 保守機の単体正常性確認
- ファームウェアとバックアップ版数の整合
- 必要なケーブル、ラック部材、作業PCの準備
- PFU正式依頼に保守部品、保守機S/N、倉庫を反映""")
elif page=="ケース管理":
 st.title("ケース管理")
 q=st.text_input("検索",placeholder="ケース番号、顧客名、S/N、案件名").lower()
 rows=[c for c in D["cases"] if q in " ".join([c["case_no"],c["customer"],c["serial"],c["project_name"]]).lower()]
 st.dataframe([{"ケース番号":c["case_no"],"案件名":c["project_name"],"顧客名":c["customer"],"S/N":c["serial"],"ステータス":c["status"]} for c in rows],use_container_width=True)
 a,b,d=st.columns(3)
 if a.button("新規ケース",type="primary"):
  n=new_case(len(D["cases"])+1);D["cases"].append(n);st.session_state.current_id=n["id"];st.rerun()
 if b.button("選択ケースを複製",disabled=not current()):
  n=copy.deepcopy(current());n["id"]=uuid.uuid4().hex;n["case_no"]+="-COPY";touch(n);D["cases"].append(n);st.session_state.current_id=n["id"];st.rerun()
 if d.button("選択ケースを削除",disabled=not current()):
  D["cases"]=[x for x in D["cases"] if x["id"]!=st.session_state.current_id];st.session_state.current_id=D["cases"][0]["id"] if D["cases"] else None;st.rerun()
 c=choose_case()
 if c:
  st.subheader("ケース基本情報")
  with st.form("case"):
   x,y,z=st.columns(3);data={}
   specs=[("case_no","ケース番号"),("project_name","案件名"),("status","ステータス"),("customer","お客様名"),("contract_no","契約番号"),("product","製品名"),("model","筐体型番"),("serial","筐体S/N"),("address","機器設置住所"),("customer_contact","お客様ご担当者名"),("customer_phone","お客様連絡先"),("contract_type","契約内容"),("location","設置場所"),("owner","自社担当者名"),("preferred_date","作業希望日時")]
   for i,(k,l) in enumerate(specs):
    with [x,y,z][i%3]:data[k]=st.selectbox(l,STATUS,index=STATUS.index(c[k])) if k=="status" else st.text_input(l,c.get(k,""))
   data["issue"]=st.text_area("障害内容",c.get("issue",""));data["remarks"]=st.text_area("備考",c.get("remarks",""))
   if st.form_submit_button("セッションへ反映",type="primary"):c.update(data);touch(c);st.success("反映しました。")
elif page=="ケース詳細":
 st.title("ケース詳細");c=choose_case()
 if c:
  with st.form("case"):
   x,y,z=st.columns(3);d={};spec=[("case_no","ケース番号"),("project_name","案件名"),("status","ステータス"),("customer","お客様名"),("contract_no","契約番号"),("product","製品名"),("model","筐体型番"),("serial","筐体S/N"),("address","機器設置住所"),("customer_contact","お客様ご担当者名"),("customer_phone","お客様連絡先"),("contract_type","契約内容"),("location","設置場所"),("owner","自社担当者名"),("option_exists","オプションカードの有無"),("option_type","オプションカードの種類"),("option_serial","オプションカードのS/N"),("option_slot","オプションカードのスロット番号"),("preferred_date","作業希望日時"),("attendance_company","作業立会会社名"),("attendance_contact","立会ご担当者名"),("attendance_phone","立会電話番号"),("parking","駐車場使用可否"),("info_sheet","お客様提供情報シート"),("work_guide","作業手順書"),("firmware","ファームウェア"),("config_file","コンフィグファイル"),("license_file","ライセンスファイル"),("activation_code","アクティベーションコード"),("entry_time","入館予定時刻"),("worker_name","作業員氏名"),("worker_phone","作業員電話番号"),("vehicle","車両情報")]
   for i,(k,l) in enumerate(spec):
    with [x,y,z][i%3]:d[k]=st.selectbox(l,STATUS,index=STATUS.index(c[k])) if k=="status" else st.text_input(l,c[k])
   for k,l in [("issue","障害内容"),("work_content","作業内容"),("final_check","最終確認方法"),("remarks","備考")]:d[k]=st.text_area(l,c[k])
   if st.form_submit_button("セッションへ反映",type="primary"):c.update(d);touch(c);st.success("反映しました。終了前にJSONを保存してください。")
elif page=="切り分け・作業手順":
 st.title("切り分け・作業手順");c=choose_case()
 if c:
  for i,item in enumerate(c["checks"]):
   a,b=st.columns([10,1]);v=a.checkbox(item["label"],item["done"],key=f'ch{i}_{c["id"]}');item["done"]=v
   if b.button("削除",key=f'del{i}_{c["id"]}'):c["checks"].pop(i);touch(c);st.rerun()
  with st.form("addcheck",clear_on_submit=True):label=st.text_input("チェック項目を追加");ok=st.form_submit_button("追加")
  if ok and label:c["checks"].append({"label":label,"done":False});touch(c);st.rerun()
  with st.form("notes"):
   d=st.text_area("切り分け結果",c["diagnosis"]);p=st.text_area("作業手順",c["procedure"],height=220);a=st.text_area("添付ファイル情報",c["attachments"])
   if st.form_submit_button("セッションへ反映",type="primary"):c.update(diagnosis=d,procedure=p,attachments=a);touch(c);st.success("反映しました。")
elif page=="保守部品・保守機":
 st.title("保守部品・保守機");c=choose_case()
 if c:
  with st.form("parts"):
   x,y,z=st.columns(3);d={"part_number":x.text_input("保守部品",c["part_number"]),"replacement_sn":y.text_input("保守機S/N",c["replacement_sn"]),"warehouse":z.text_input("配備倉庫",c["warehouse"]),"ship_date":x.text_input("発送日時",c["ship_date"]),"tracking":y.text_input("配送伝票番号",c["tracking"]),"return_status":z.selectbox("回収状況",["未手配","手配済み","回収済み"],index=["未手配","手配済み","回収済み"].index(c["return_status"])),"part_notes":st.text_area("選定根拠・注意事項",c["part_notes"])}
   if st.form_submit_button("セッションへ反映",type="primary"):c.update(d);touch(c);st.success("反映しました。")
elif page=="案件タイムライン":
 st.title("案件タイムライン");c=choose_case()
 if c:
  with st.form("timeline",clear_on_submit=True):when=st.datetime_input("日時",datetime.now());kind=st.selectbox("種別",["顧客連絡","PFU依頼","部材発送","作業","回収","クローズ","メモ"]);detail=st.text_area("内容");ok=st.form_submit_button("履歴を追加",type="primary")
  if ok and detail:c["timeline"].append({"date":when.isoformat(),"type":kind,"text":detail});touch(c);st.rerun()
  for x in sorted(c["timeline"],key=lambda i:i["date"],reverse=True):st.markdown(f'**{x["type"]}**  {x["date"]}  \n{x["text"]}')
elif page=="メールテンプレート":
 st.title("メールテンプレート");c=choose_case();key=st.radio("種類",list(D["templates"]),format_func=lambda k:D["templates"][k]["title"],horizontal=True);body=st.text_area("テンプレート編集",D["templates"][key]["body"],height=500,key=f'tpl_{key}')
 if st.button("テンプレート変更を反映"):D["templates"][key]["body"]=body;D["saved_at"]=now();st.success("反映しました。")
 if c:
  mp={"ケース番号":"case_no","お客様名":"customer","自社担当者名":"owner","契約番号":"contract_no","機器設置住所":"address","お客様ご担当者名":"customer_contact","お客様連絡先":"customer_phone","筐体型番":"model","筐体S/N":"serial","オプションカードの有無":"option_exists","オプションカードの種類":"option_type","オプションカードのS/N":"option_serial","オプションカードのスロット番号":"option_slot","障害内容":"issue","製品名":"product","契約内容":"contract_type","設置場所":"location","作業希望日時":"preferred_date","作業内容":"work_content","作業立会会社名":"attendance_company","立会ご担当者名":"attendance_contact","立会電話番号":"attendance_phone","保守部品":"part_number","保守機S/N":"replacement_sn","配備倉庫":"warehouse","最終確認方法":"final_check","駐車場使用可否":"parking","備考":"remarks","お客様提供情報シート":"info_sheet","作業手順書":"work_guide","ファームウェア":"firmware","コンフィグファイル":"config_file","ライセンスファイル":"license_file","アクティベーションコード":"activation_code","入館予定時刻":"entry_time","作業員氏名":"worker_name","作業員電話番号":"worker_phone","車両情報":"vehicle"};preview=body
  for label,k in mp.items():preview=preview.replace("{"+label+"}",c[k] or "［未入力］")
  st.text_area("差し込みプレビュー",preview,height=600);st.download_button("テキストをダウンロード",preview,f'{c["case_no"]}_{D["templates"][key]["title"]}.txt')
elif page=="JSONデータ管理":
 st.title("JSONデータ管理");st.warning("Streamlit Community Cloudではセッション終了後のデータ保持を前提にしません。作業終了前に必ずJSONをダウンロードしてください。")
 c=current();a,b=st.columns(2)
 a.download_button("全ケースをJSON保存",json_bytes(D),f'hardware_cases_{datetime.now():%Y%m%d_%H%M%S}.json','application/json',type="primary",use_container_width=True)
 if c:b.download_button("現在のケースだけJSON保存",json_bytes({"schema_version":1,"app":"hardware_case_manager","case":c,"templates":D["templates"]}),f'{c["case_no"]}.json','application/json',use_container_width=True)
 mode=st.radio("インポート方法",["全データを置換","ケースを追加・更新"]);up=st.file_uploader("JSONファイルをインポート",type=["json"])
 if up and st.button("インポート実行"):
  try:
   obj=json.load(up)
   if obj.get("app")!="hardware_case_manager" or obj.get("schema_version")!=1:raise ValueError("形式またはバージョンが異なります")
   incoming=obj.get("cases") or ([obj["case"]] if "case" in obj else [])
   if mode=="全データを置換":
    if not obj.get("cases"):raise ValueError("全データJSONを選択してください")
    st.session_state.data=obj
   else:
    byid={x["id"]:x for x in D["cases"]}
    for x in incoming:byid[x["id"]]=x
    D["cases"]=list(byid.values());D["templates"].update(obj.get("templates",{}))
   st.session_state.current_id=st.session_state.data["cases"][0]["id"] if st.session_state.data["cases"] else None;st.success("インポートしました。");st.rerun()
  except Exception as e:st.error(f"インポートできませんでした: {e}")
 st.divider();st.subheader("新規状態へ戻す")
 if st.button("セッション内データを初期化"):st.session_state.data=initial();st.session_state.current_id=st.session_state.data["cases"][0]["id"];st.rerun()
