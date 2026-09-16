import json
import uuid
from datetime import datetime
import streamlit as st

st.set_page_config(page_title="Symantec ハードウェア修理 統合ランブック", page_icon="🛠️", layout="wide")

USERNAME = "baofu"
PASSWORD = "Oosaka197982$"

LOAN_DEFAULTS = [
    {"no":1,"status":"可","loan_id":"KTC","sku":"NFR-SSP-S210-10","serial":"3921710016","maintenance_until":"5/26/2028","modules":"","borrower":"","loan_start":"","planned_return":"","remarks":""},
    {"no":2,"status":"貸出中","loan_id":"本社\n2026/06/04~","sku":"NFR-SSP-S210-10","serial":"2422710006","maintenance_until":"5/26/2028","modules":"","borrower":"本社","loan_start":"2026/06/04","planned_return":"","remarks":""},
    {"no":3,"status":"可","loan_id":"KTC","sku":"NFR-SSP-S210-10","serial":"3921710001","maintenance_until":"5/26/2028","modules":"","borrower":"","loan_start":"","planned_return":"","remarks":""},
    {"no":4,"status":"可","loan_id":"KTC","sku":"NFR-SSP-S210-10","serial":"3921710003","maintenance_until":"5/26/2028","modules":"","borrower":"","loan_start":"","planned_return":"","remarks":""},
    {"no":5,"status":"可","loan_id":"KTC","sku":"SSP-S410-10","serial":"1920700004","maintenance_until":"12/31/2026","modules":"","borrower":"","loan_start":"","planned_return":"","remarks":""},
    {"no":6,"status":"可","loan_id":"KTC","sku":"SSP-S410-10","serial":"1621700111","maintenance_until":"12/31/2026","modules":"","borrower":"","loan_start":"","planned_return":"","remarks":""},
    {"no":7,"status":"可","loan_id":"KTC","sku":"SSP-S410-10","serial":"3920700035","maintenance_until":"12/31/2026","modules":"","borrower":"","loan_start":"","planned_return":"","remarks":""},
    {"no":8,"status":"可","loan_id":"KTC","sku":"SSP-S410-20","serial":"4020700013","maintenance_until":"1/11/2027","modules":"","borrower":"","loan_start":"","planned_return":"","remarks":""},
    {"no":9,"status":"可","loan_id":"KTC","sku":"SSP-S410-20B","serial":"4222700036","maintenance_until":"6/20/2028","modules":"BCM57416 NetXtreme-E Dual-Media 10G RDMA Ethernet Controller\nEthernet Controller X710 for 10GbE SFP+","borrower":"","loan_start":"","planned_return":"","remarks":""},
    {"no":10,"status":"可","loan_id":"KTC","sku":"SSP-S410-20B","serial":"3023700022","maintenance_until":"11/20/2026","modules":"BCM57416 NetXtreme-E Dual-Media 10G RDMA Ethernet Controller\nEthernet Controller X710 for 10GbE SFP+","borrower":"","loan_start":"","planned_return":"","remarks":""},
    {"no":11,"status":"貸出中","loan_id":"本社","sku":"SV-S550-5","serial":"3222610001","maintenance_until":"3/6/2027","modules":"NIC-4X1G-10G-SRD-SFP-NBP (S550)\nNIC-4X10GIG-LC-BP (SSP)","borrower":"本社","loan_start":"","planned_return":"","remarks":""},
    {"no":12,"status":"貸出中","loan_id":"KTC","sku":"NFR-SSP-S410-20","serial":"1422700031","maintenance_until":"5/26/2028","modules":"","borrower":"KTC","loan_start":"","planned_return":"","remarks":""},
    {"no":13,"status":"可","loan_id":"KTC","sku":"ラックレール","serial":"","maintenance_until":"","modules":"","borrower":"","loan_start":"","planned_return":"","remarks":""},
    {"no":14,"status":"可","loan_id":"KTC","sku":"ラックレール","serial":"","maintenance_until":"","modules":"","borrower":"","loan_start":"","planned_return":"","remarks":""},
    {"no":15,"status":"可","loan_id":"KTC","sku":"ラックレール","serial":"","maintenance_until":"","modules":"","borrower":"","loan_start":"","planned_return":"","remarks":""},
    {"no":16,"status":"可","loan_id":"KTC","sku":"ラックレール","serial":"","maintenance_until":"","modules":"","borrower":"","loan_start":"","planned_return":"","remarks":""},
    {"no":17,"status":"可","loan_id":"KTC","sku":"ラックレール","serial":"","maintenance_until":"","modules":"","borrower":"","loan_start":"","planned_return":"","remarks":""},
    {"no":18,"status":"可","loan_id":"KTC","sku":"ISG-FRU-QAT-S410","serial":"2509173509","maintenance_until":"","modules":"","borrower":"","loan_start":"","planned_return":"","remarks":""},
    {"no":19,"status":"可","loan_id":"KTC","sku":"ISG-FRU-QAT-S410","serial":"2509173510","maintenance_until":"","modules":"","borrower":"","loan_start":"","planned_return":"","remarks":""},
]

INVENTORY = [
    ("SSP-S410-10-PR","西日本・松山倉庫","GP524169","1921700015"),("SSP-S410-20-PR","西日本・北九州倉庫","GP524172","1422700035"),("SSP-S210-10-PR","宇都宮ＷＨ","GP524176","123710030"),("SSP-S210-10-PR","神戸ＷＨ","GP524184","223710032"),("SSP-S210-10-PR","大阪ロジスティック倉庫","GP524185","1922710014"),("SSP-S410-10-PR","大阪ロジスティック倉庫","GP524186","1921700022"),("SSP-S410-10-PR","大阪ロジスティック倉庫","GP524187","1921700034"),("SSP-S410-20-PR","大阪ロジスティック倉庫","GP524188","221700049"),("SV-S550-5","大阪ロジスティック倉庫","GP524189","3922610001"),("SV-S550-5","大阪ロジスティック倉庫","GP524190","524610017"),("SV-S550-10","大阪ロジスティック倉庫","GP524191","3922610002"),("SSP-S210-10-PR-OKI","東京ロジスティック倉庫","GP524214","1922710096"),("SSP-S210-10-PR-OKI","東京ロジスティック倉庫","GP524215","1422710001"),("SSP-S210-10-PR","東京ロジスティック倉庫","GP524216","3524710013"),("SSP-S210-10-PR","東京ロジスティック倉庫","GP524217","3524710002"),("SSP-S410-10-PR","東京ロジスティック倉庫","GP524218","1921700013"),("SSP-S410-10-PR-SME","東京ロジスティック倉庫","GP524219","1921700043"),("SSP-S410-10-PR","東京ロジスティック倉庫","GP524220","4720700059"),("SSP-S410-20-PR","東京ロジスティック倉庫","GP524221","2722700138"),("SSP-S410-20-PR","東京ロジスティック倉庫","GP524222","1422700078"),("SSP-S410-20-PR","東京ロジスティック倉庫","GP524223","4020700027"),("SSP-S410-20B-PR","東京ロジスティック倉庫","GP524224","4222700037"),("SSP-S410-20B-PR","東京ロジスティック倉庫","GP524225","4222700015"),("SSP-S410-20B-PR","東京ロジスティック倉庫","GP524226","2423700018"),("SV-S550-5","東京ロジスティック倉庫","GP524227","3222610016"),("SV-S550-10","東京ロジスティック倉庫","GP524228","3222610007"),("NIC-4X1G-10G-SRD-SFP-NBP","東京ロジスティック倉庫","GP525824","2305316068"),("NIC-4X1G-10G-SRD-SFP-NBP","大阪ロジスティック倉庫","GP525825","2412184173"),("NIC-4X10GIG-LC-BP","東京ロジスティック倉庫","GP525826","2408056224"),("NIC-4X10GIG-LC-BP","大阪ロジスティック倉庫","GP525827","2409136107"),("Java用キッティングPC","東京ロジスティック倉庫","GP526118","0F387FV24013GT"),("Java用キッティングPC","大阪ロジスティック倉庫","GP526120","0F387KG24013GT")
]


def new_case():
    return {"id":uuid.uuid4().hex,"case_no":"","customer":"","serial":"","model":"","status":"受付","issue":"","memo":"","checks":{},"assets":[],"timeline":[]}


def initial_data():
    c = new_case()
    return {"schema_version":4,"cases":[c],"current":c["id"],"loan_assets":[dict(x) for x in LOAN_DEFAULTS],"loan_history":[],"saved_at":""}


def migrate(data):
    data.setdefault("schema_version",4)
    data.setdefault("cases",[])
    if not data["cases"]:
        data["cases"].append(new_case())
    data.setdefault("current",data["cases"][0]["id"])
    data.setdefault("loan_assets",[dict(x) for x in LOAN_DEFAULTS])
    data.setdefault("loan_history",[])
    data.setdefault("saved_at","")
    for item in data["loan_assets"]:
        for key,value in {"borrower":"","loan_start":"","planned_return":"","remarks":"","modules":"","maintenance_until":"","loan_id":"","serial":""}.items():
            item.setdefault(key,value)
    return data

if not st.session_state.get("auth"):
    st.title("🔐 Hardware Repair Runbook")
    with st.form("login"):
        user = st.text_input("ユーザー名")
        password = st.text_input("パスワード",type="password")
        login = st.form_submit_button("ログイン",type="primary")
    if login:
        if user == USERNAME and password == PASSWORD:
            st.session_state.auth = True
            st.rerun()
        else:
            st.error("ユーザー名またはパスワードが正しくありません。")
    st.stop()

if "db" not in st.session_state:
    st.session_state.db = initial_data()
D = migrate(st.session_state.db)

def current_case():
    return next((c for c in D["cases"] if c["id"] == D["current"]),D["cases"][0])

def checklist(prefix,items):
    c=current_case()
    for i,item in enumerate(items):
        key=f"{prefix}.{i}"
        c["checks"][key]=st.checkbox(item,value=c["checks"].get(key,False),key=key+c["id"])

def show_code(text):
    st.code(text,language="shell")

with st.sidebar:
    st.title("🛠️ Repair Runbook")
    page=st.radio("メニュー",[
        "🏠 全体の流れ","📋 ケース情報","🔍 障害切り分け","📥 情報の依頼","📦 保守機材の選定",
        "🔁 貸出機管理","🧰 SSPリストア","🌐 SSP上のSG","🧪 CAS-VA","🔐 SSLV→SSLV","🔄 SSLV→SSP",
        "🏢 現地交換・完了","✅ 品質ゲート","📚 資料対応表","🕘 タイムライン","💾 JSON管理"
    ])
    if st.button("ログアウト"):
        st.session_state.clear(); st.rerun()

if page=="🏠 全体の流れ":
    st.title("🏠 Symantec ハードウェア修理 統合ランブック")
    st.error("関係者外秘。手順書にない作業やコマンドは実施せず、特別対応・不明点・異常はサポートへエスカレーションしてください。")
    cols=st.columns(7)
    for col,(a,b) in zip(cols,[("受付","契約"),("切分","LED"),("情報","証跡"),("選定","機材"),("復元","版数"),("現地","交換"),("完了","検証")]): col.metric(a,b)
    checklist("flow",["ケース作成・契約確認","起動、LED、Console、Self-check","設定・診断・バックアップ","同一モデル、NIC、倉庫、状態","版数整合、ライセンス、設定","交換、起動、顧客確認"])

elif page=="📋 ケース情報":
    st.title("📋 ケース情報")
    c=current_case()
    with st.form("case_form"):
        a,b,d=st.columns(3)
        c["case_no"]=a.text_input("ケース番号",c.get("case_no",""));c["customer"]=b.text_input("顧客名",c.get("customer",""));c["serial"]=d.text_input("対象機S/N",c.get("serial",""))
        c["model"]=a.text_input("モデル",c.get("model",""));c["status"]=b.selectbox("状態",["受付","切り分け中","情報待ち","保守機選定","キッティング中","現地作業予定","完了"],index=["受付","切り分け中","情報待ち","保守機選定","キッティング中","現地作業予定","完了"].index(c.get("status","受付")))
        c["issue"]=st.text_area("障害概要",c.get("issue",""));c["memo"]=st.text_area("社内メモ",c.get("memo",""));st.form_submit_button("反映",type="primary")

elif page=="🔍 障害切り分け":
    st.title("🔍 ハードウェア障害切り分け方法")
    t1,t2,t3=st.tabs(["共通","SSP S410","SSLV SV-S550"])
    with t1: checklist("tri",["申告内容、発生日時、影響範囲、直前変更","セルフチェック実行有無と結果","電源・起動可否、異音、再起動ループ","前面・背面LED、LCD","SSH、シリアル、Web","SNMP Trap、MIB"])
    with t2: st.markdown("NMIは対象版数を確認し、前面IDボタンを10秒長押し。");show_code("show json-config\nhealth-monitoring view current")
    with t3: st.markdown("NMIは `Menu → Left → Right`。LCD、LED、SSH、Serial、管理GUI、Diagnosticsを確認します。")

elif page=="📥 情報の依頼":
    st.title("📥 情報の依頼方法")
    t1,t2,t3=st.tabs(["案件","SSP / SG / CAS","SSLV"])
    with t1: checklist("req1",["受付番号 / ケース番号","契約番号・保守時間帯","顧客名、担当者、連絡先","設置場所、入館条件、作業希望日時","対象機モデル、10桁S/N","障害内容と切り分け結果","ラック位置、高所・重量物、駐車場"])
    with t2: checklist("req2",["ISG Release、json-config、running-config、health、applications、event-log、LAG","ISG IP/mask/gateway/DNS、Console/Enable","SG情報、config、sysinfo、秘密鍵、証明書、trust_package","CAS情報、CASconfig.xml、C-C～C-P資料","バックアップ有無と復元条件の了承"])
    with t3: checklist("req3",["モデル、S/N、OS版数","Option NIC種類・枚数・Slot・S/N","管理Network、GUI、Enable","Host Categorization","Diagnostics","Full BackupまたはPolicy/PKI/Platformとrestore password","必要画面"])

elif page=="📦 保守機材の選定":
    st.title("📦 保守機材の選定")
    q=st.text_input("モデル、倉庫、PFU管理番号、S/Nで検索").lower()
    rows=[];c=current_case()
    for i,(name,warehouse,pfu,sn) in enumerate(INVENTORY,1):
        if q and q not in f"{name} {warehouse} {pfu} {sn}".lower(): continue
        selected=st.checkbox(f"{i}. {name} | {warehouse} | {pfu} | {sn}",sn in c["assets"],key="inv"+sn)
        if selected and sn not in c["assets"]: c["assets"].append(sn)
        if not selected and sn in c["assets"]: c["assets"].remove(sn)
        rows.append({"No.":i,"品名":name,"倉庫":warehouse,"預り数":1,"状態":"保管中 1","PFU管理番号":pfu,"製造番号":sn})
    st.dataframe(rows,use_container_width=True)
    st.warning("選定順: 同一系統・性能モデル → NIC型式/Slot適合 → 保管状態 → 倉庫・現地条件。")

elif page=="🔁 貸出機管理":
    st.title("🔁 貸出機管理")
    assets=D["loan_assets"]
    available=sum(1 for x in assets if x["status"]=="可")
    loaned=sum(1 for x in assets if x["status"]=="貸出中")
    a,b,c=st.columns(3);a.metric("登録数",len(assets));b.metric("貸出可能",available);c.metric("貸出中",loaned)
    q=st.text_input("SKU、Serial#、貸出ID、モジュールで検索").lower()
    filtered=[x for x in assets if not q or q in " ".join(str(x.get(k,"")) for k in ["sku","serial","loan_id","modules","borrower"]).lower()]
    st.dataframe([{"No":x["no"],"ステータス":x["status"],"貸出ID":x["loan_id"],"SKU":x["sku"],"Serial#":x["serial"],"保守期限":x["maintenance_until"],"組込み済モジュール":x["modules"],"貸出先":x["borrower"],"貸出開始":x["loan_start"],"返却予定":x["planned_return"]} for x in filtered],use_container_width=True)
    labels=[f'{x["no"]}. {x["sku"]} | {x["serial"] or "S/Nなし"} | {x["status"]}' for x in assets]
    selected_label=st.selectbox("変更する貸出機",labels)
    item=assets[labels.index(selected_label)]
    with st.form("loan_edit"):
        l,r=st.columns(2)
        status=l.selectbox("ステータス",["可","貸出中","予約中","点検中","修理中","利用不可"],index=["可","貸出中","予約中","点検中","修理中","利用不可"].index(item["status"]) if item["status"] in ["可","貸出中","予約中","点検中","修理中","利用不可"] else 0)
        loan_id=r.text_input("貸出ID / 保管場所",item["loan_id"])
        borrower=l.text_input("貸出先",item["borrower"])
        loan_start=r.text_input("貸出開始",item["loan_start"],placeholder="YYYY/MM/DD")
        planned_return=l.text_input("返却予定",item["planned_return"],placeholder="YYYY/MM/DD")
        maintenance=r.text_input("保守期限",item["maintenance_until"])
        modules=st.text_area("組込み済モジュール",item["modules"],height=100)
        remarks=st.text_area("備考",item["remarks"])
        save=st.form_submit_button("貸出状態を更新",type="primary")
    if save:
        before=dict(item)
        item.update(status=status,loan_id=loan_id,borrower=borrower,loan_start=loan_start,planned_return=planned_return,maintenance_until=maintenance,modules=modules,remarks=remarks)
        D["loan_history"].append({"timestamp":datetime.now().isoformat(),"no":item["no"],"sku":item["sku"],"serial":item["serial"],"from_status":before["status"],"to_status":status,"borrower":borrower,"loan_id":loan_id,"remarks":remarks})
        st.success("貸出状態を更新しました。JSON保存対象です。")
        st.rerun()
    with st.expander("貸出履歴"):
        st.dataframe(list(reversed(D["loan_history"])),use_container_width=True)

elif page=="🧰 SSPリストア":
    st.title("🧰 SSPリストア")
    checklist("ssp",["資料・保守機・MD・Cable・Firmware・License","Serial 9600/8/none/1/none、ログ開始","筐体S/Nとjson-config","health current","同一ISG版数","factory defaults","Setup Console","SG/CAS license","all_commands.txt","ISG_config比較","最大2 Application","停止、shutdown、成果物"])
    show_code("show json-config\nshow running-config | nomore\nhealth-monitoring view settings\nshow applications\nevent-log view configuration\nlag view")

elif page=="🌐 SSP上のSG":
    st.title("🌐 SSP上のSG-VA")
    checklist("sg",["Image load","create sg","Created確認","start / Running","attach-console / initial setup","sysinfo / eventlog","trust_package","configuration-passwords-key","秘密鍵・証明書","SGconfig","Access-log","差分確認","CLI/Web/Health","shutdown / stop / Stopped"])
    st.error("順序厳守: trust_package → configuration-passwords-key → SSL秘密鍵・証明書 → SGコンフィグ")

elif page=="🧪 CAS-VA":
    st.title("🧪 CAS-VA C-1～C-31")
    tabs=st.tabs(["C-1～2 作成","C-3 初期設定","C-4～7 正常性","C-8～10 Config","C-11～25 個別設定","C-26～30 検証","C-31 停止"])
    with tabs[0]: checklist("cas1",["Image ID一致imageをload","Image/Version照合","create cas","Created確認","start / Running"]);show_code("configure\nimages\nload http://<WEB_SERVER_IP>/casma_xxxx.bcsi\nview\nexit\napplications\ncreate cas <CAS_NAME> model <MODEL> license-id <LICENSE_ID> image-id <IMAGE_ID>\nstart <CAS_NAME>\nview")
    with tabs[1]: checklist("cas2",["attach-console","Trustpackage update待ち","Enter×3、Setup console 2","IP/mask/gateway/DNS","Console/Enable password","secure serial No","Ctrl+]で戻る"])
    with tabs[2]: checklist("cas3",["設定InterfaceへMD接続","https://<CAS-IP>:8082/へAdminでlogin","保守機CASsysinfo.txt UTF-8","serialNumber=License ID","version=Image ID","System Status OK"])
    with tabs[3]: checklist("cas4",["本編7/8/9、C-1/C-3完了","Utilities > Configuration","Upload Entire Configuration","CASconfig.xml","error記録"])
    with tabs[4]: st.markdown("License Active、Interface speed/duplex、Access-list、Network Routes、Proxy、Local Users、LDAP、RADIUS、Email Day Report、SNMP、Whitelist/Blacklist、Banner/Logo、NTP、Sandboxing Cache。提供資料がある変更項目だけ復元します。");show_code("show full-configuration interface\ninterface 0:0 speed 100 duplex full\nweb-management access-list 192.168.0.0/24\nip route 192.168.45.0 255.255.255.0 10.0.0.1 metric 10")
    with tabs[5]: checklist("cas5",["キッティング後CASsysinfo.txt","キッティング後CASconfig.xml","顧客configと比較","差分時エスカレーション","CLI","Web","System Status OK"])
    with tabs[6]: checklist("cas6",["App Running確認","attach-console","CAS shutdown","safe to power off","Ctrl+]","ISG stop","Stopped確認"])

elif page=="🔐 SSLV→SSLV":
    st.title("🔐 SSLVからSSLV")
    checklist("sslv",["DiagnosticsでOS/SN/Model/NIC","同一Model/NIC選定","ACL A/B/C分類","Serial 115200/8/none/1/none","NIC装着とSlot確認","LED/LCD、CPU<60%、memory、sensor","同一5.x OS","License","Full BackupまたはPKI→Policy→Platform","2項目check","Type C ACL復旧","Diagnostics差分","Auto-Update Disabled","資料/log、shutdown、梱包"])

elif page=="🔄 SSLV→SSP":
    st.title("🔄 SSLVからSSP")
    st.info("ISG 2.5.5.1以上、SSLV 6.2.1.1以上。")
    checklist("s2s",["IIS MIME .bcsi/.bctp","installed-systems view","段階load","default確認 / restart","Current system","health","SSLV License","SSLV Image","sslv-netdef","Model対応","Full Backup","Slot3 segment調整","ACL復旧","Diagnostics比較"])
    show_code("installed-systems view\ninstalled-systems load http://<WebServer>/<firmware.bcsi>\nrestart\nhealth-monitoring view current")

elif page=="🏢 現地交換・完了":
    st.title("🏢 現地交換・完了")
    checklist("onsite",["入館・開始報告","障害機S/N","交換機単体確認","停止了承","配線撮影/marking","shutdown、LED消灯、撤去","保守機搭載・配線","起動・Health","App Running、CLI/Web","SG Filter / CAS License","顧客業務確認","報告書・梱包・退館"])

elif page=="✅ 品質ゲート":
    st.title("✅ 品質ゲート")
    a,b,c=st.tabs(["開始条件","出荷条件","即時停止"])
    with a: checklist("q1",["契約・S/N・Model","資料・Backup","保守機/NIC","Version/License","作業log"])
    with b: checklist("q2",["Model/SN/Version/License","Health","差分","CLI/Web","成果物"])
    with c: checklist("q3",["手順外操作","Health異常、不一致","差分、restore error、log異常","範囲外依頼","判断不能、資料矛盾"])

elif page=="📚 資料対応表":
    st.title("📚 資料対応表")
    docs=[{"資料":"ハードウェア障害関連対応フロー.docx","統合先":"受付、切り分け、情報依頼、エスカレーション","注意":"一次判断"},{"資料":"保守機リスト.xlsx","統合先":"保守機材","注意":"260730"},{"資料":"ハードウェア修理フォローver8 (1).pdf","統合先":"全体フロー、連絡、完了","注意":"他資料と整合"},{"資料":"SSP保守手順書_本編","統合先":"SSP、現地","注意":"Ver.3.1"},{"資料":"SG-VA構築編","統合先":"SSP上SG","注意":"順序依存"},{"資料":"CAS-VA構築編","統合先":"CAS","注意":"C-C～C-P"},{"資料":"SSLVA Ver5.x S550","統合先":"SSLV→SSLV","注意":"Ver.1.2、検証中"},{"資料":"SSP410で故障したSSLV","統合先":"SSLV→SSP","注意":"Slot3"},{"資料":"SSP-410 ISGアップグレード","統合先":"SSLV→SSP","注意":"段階upgrade"}]
    st.dataframe(docs,use_container_width=True)

elif page=="🕘 タイムライン":
    st.title("🕘 タイムライン");c=current_case()
    with st.form("timeline",clear_on_submit=True):
        a,b=st.columns(2);date=a.date_input("日付");time=b.time_input("時刻");kind=st.selectbox("種別",["顧客連絡","PFU依頼","部材発送","作業","回収","クローズ","メモ"]);text=st.text_area("内容");add=st.form_submit_button("追加")
    if add and text:
        c["timeline"].append({"date":datetime.combine(date,time).isoformat(),"type":kind,"text":text});st.rerun()
    st.dataframe(list(reversed(c["timeline"])),use_container_width=True)

elif page=="💾 JSON管理":
    st.title("💾 JSON管理")
    D["saved_at"]=datetime.now().isoformat()
    raw=json.dumps(D,ensure_ascii=False,indent=2).encode("utf-8")
    st.download_button("全データJSON保存",raw,"hardware_runbook_all_data.json","application/json",type="primary")
    up=st.file_uploader("全データJSON読込",type="json")
    if up and st.button("読込"):
        obj=json.load(up)
        st.session_state.db=migrate(obj);st.rerun()
    if st.button("＋ 新規ケース"):
        c=new_case();D["cases"].append(c);D["current"]=c["id"];st.rerun()
