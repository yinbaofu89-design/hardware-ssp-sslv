import streamlit as st, json, hashlib, hmac
from datetime import datetime
st.set_page_config(page_title='Hardware Repair Runbook',page_icon='🛠️',layout='wide')
st.markdown('''<style>
.stApp{background:linear-gradient(145deg,#06101d,#0b2035 55%,#081522);color:#eaf4fb}[data-testid="stSidebar"]{background:linear-gradient(180deg,#050d17,#0b2238);border-right:1px solid #205171}h1{color:#fff!important;border-bottom:2px solid #20d4bd;padding-bottom:.4rem}h2{color:#75d6ff!important}h3{color:#7df0d4!important}.stTabs [data-baseweb="tab-list"]{gap:7px;background:#071827;padding:7px;border-radius:12px}.stTabs [data-baseweb="tab"]{background:#102b44;border:1px solid #28516f;border-radius:9px;color:#d8efff}.stTabs [aria-selected="true"]{background:linear-gradient(135deg,#147cbe,#13a38f)!important;color:#fff!important}div[data-testid="stMetric"]{background:linear-gradient(135deg,#102d48,#123957);border:1px solid #2d6589;padding:15px;border-radius:14px}.stButton>button,.stDownloadButton>button{background:linear-gradient(135deg,#116fa9,#148e7e);color:#fff;border:1px solid #40a5bd;border-radius:9px}div[data-testid="stExpander"]{background:#0c2135;border:1px solid #28516f;border-radius:12px}code{color:#8ff4d5!important}</style>''',unsafe_allow_html=True)
USER='baofu';SALT='2aa2c973cd53ef201771a697e4f965b9';HASH='7578e676b92a04087702aadd5f833ef26ec959876877077129365516060981c6'
def verify(u,p):return hmac.compare_digest(u,USER) and hmac.compare_digest(hashlib.pbkdf2_hmac('sha256',p.encode(),bytes.fromhex(SALT),310000).hex(),HASH)
if not st.session_state.get('auth'):
 st.title('🔐 Hardware Repair Runbook')
 with st.form('login'):
  u=st.text_input('ユーザー名');p=st.text_input('パスワード',type='password');ok=st.form_submit_button('ログイン',type='primary')
 if ok:
  if verify(u,p):st.session_state.auth=True;st.rerun()
  else:st.error('ユーザー名またはパスワードが正しくありません。')
 st.stop()
if 'data' not in st.session_state:st.session_state.data={'schema_version':2,'cases':[{'id':'case1','case_no':'CASE-001','customer':'','model':'','serial':'','status':'未対応','checks':{},'timeline':[],'selected_assets':[]}],'current':'case1','saved_at':''}
D=st.session_state.data
def cur():return next((x for x in D['cases'] if x['id']==D['current']),None)
def check(key,label):
 c=cur();c['checks'][key]=st.checkbox(label,c['checks'].get(key,False),key=key);return c['checks'][key]
def cmd(x):st.code(x,language='shell')
def tabs_steps(items):
 ts=st.tabs([x[0] for x in items])
 for t,(name,body) in zip(ts,items):
  with t:st.markdown(body)
with st.sidebar:
 st.title('🛠️ Repair Runbook')
 page=st.radio('メニュー',['🏠 全体フロー','🔍 障害切り分け','📥 情報依頼','🧰 SSP作業','🌐 SG-VA','🧪 CAS-VA','🔐 SSLV→SSLV','🔄 SSLV→SSP','📦 保守機材','🏢 現地交換','✅ 品質ゲート','📋 ケース管理','🕘 タイムライン','💾 JSON管理'])
 if st.button('ログアウト'):st.session_state.clear();st.rerun()
if page=='🏠 全体フロー':
 st.title('🏠 ハードウェア修理 統合ランブック')
 st.warning('🔒 関係者外秘。手順書にない作業・コマンドは実施せず、不明点や異常はエスカレーションしてください。')
 cols=st.columns(4)
 for c,(a,b) in zip(cols,[('受付','契約・影響'),('切り分け','LED・Console'),('構築・復元','版数・License'),('現地・完了','交換・検証')]):c.metric(a,b)
 st.markdown('''```text
受付 → 切り分け → 情報回収 → 保守機材選定 → キッティング → 現地交換 → 検証 → 完了/RMA
```''')
 for i,x in enumerate(['ケース・契約確認','症状・影響・起動/LED/Console確認','設定・診断・Backup回収','同一モデル/NIC/倉庫確認','版数整合・License・復元','現地交換・顧客確認','報告・回収・RMA'],1):check(f'flow{i}',f'{i}. {x}')
elif page=='🔍 障害切り分け':
 st.title('🔍 障害切り分け')
 t=st.tabs(['共通','SSP S410','SSLV S550','判定ゲート'])
 with t[0]:
  for i,x in enumerate(['申告内容、発生日時、影響範囲、直前変更','セルフチェック結果','電源・起動・異音・再起動ループ','前面/背面LED・LCD','SSH・Serial・Web GUI','SNMP Trap・MIB'],1):check(f'tri{i}',x)
 with t[1]:
  st.markdown('**NMI:** 対象版数条件を確認し、前面IDボタンを10秒長押し。ID LEDの青点滅後、再起動を確認。')
  cmd('show json-config\nhealth-monitoring view current')
 with t[2]:st.markdown('**NMI:** `Menu → Left → Right`。LCD、LED、SSH、Serial、管理GUIを確認。')
 with t[3]:st.markdown('- 外部要因を除外\n- 契約・S/N一致\n- 被疑部品を特定\n- 判断不能、情報矛盾、影響不明なら停止してエスカレーション')
elif page=='📥 情報依頼':
 st.title('📥 情報依頼')
 tabs_steps([('案件情報','受付番号、契約番号、保守時間帯、お客様、連絡先、設置場所、入館条件、希望日時、モデル、S/N、障害内容、ラック条件を回収します。'),('SSP/SG/CAS','ISG Release、json-config、running-config、health、applications、event-log、LAG、IP、資格情報、Image ID、License ID、config、sysinfo、証明書、Backupを回収します。'),('SSLV','モデル、S/N、OS、Option NIC、管理IP、GUI/Enable資格情報、Diagnostics、Full BackupまたはPolicy/PKI/Platform、画面情報を回収します。')])
elif page=='🧰 SSP作業':
 st.title('🧰 SSP キッティング・リストア')
 tabs_steps([('準備','MD、Serial/LAN、SSP、IIS、Firmware、License、情報シート、Backup、標準工具を準備。IIS保存先は `C:\\inetpub\\wwwroot`。'),('Serial','9600 / 8 bit / parity none / stop 1 / flow none。Tera Termログを`受付No_日付.txt`で開始。'),('正常性','```shell\nenable\nshow json-config\nhealth-monitoring view current\n```\nS/N、Model、CPU、Fan、Memory、Power、RAID、Temperature、Voltageを確認。'),('初期化','```shell\nrestore-defaults factory-defaults\n```\n対象が保守機であることを確認して実施。'),('ISG設定','Setup ConsoleでIP/mask/gateway/DNS/Console/Enableを設定。\n```shell\ninstalled-systems view\nlicensing view\n```')])
elif page=='🌐 SG-VA':
 st.title('🌐 SG-VA 構築・リストア')
 tabs_steps([('Image','```shell\nconfigure\nimages\nload http://<WEB_SERVER>/ProxySG_xxxx.bcsi\nview\n```'),('作成・起動','```shell\napplications\ncreate sg <NAME> model <MODEL> license-id <LICENSE> image-id <IMAGE>\nview\nstart <NAME>\nview\n```\nCreatedからRunningを確認。'),('初期設定','```shell\nattach-console <NAME>\n```\nManual setup、network、Admin/Console/Enable設定。戻る時は`Ctrl + ]`。'),('復元順序','**trust_package → configuration-passwords-key → SSL秘密鍵/証明書 → config**。順序を崩さない。'),('検証','sysinfo、eventlog、Health、CPU/Memory、Disk、CLI/Web、設定差分を確認。')])
elif page=='🧪 CAS-VA':
 st.title('🧪 CAS-VA 構築・リストア')
 st.info('CAS-VA構築編 Ver.1.0の作成、初期設定、正常性確認、リストア、個別設定、差分確認、停止を工程別に整理しました。')
 t=st.tabs(['1️⃣ Image','2️⃣ 作成・起動','3️⃣ 初期設定','4️⃣ 正常性','5️⃣ Config復元','6️⃣ 個別設定','7️⃣ 差分確認','8️⃣ Shutdown'])
 with t[0]:
  st.markdown('CAS Image IDをお客様提供情報と照合します。');cmd('enable\nconfigure\nimages\nload http://<WEB_SERVER_IP>/casma_xxxx.bcsi\nview')
 with t[1]:
  cmd('exit\napplications\ncreate cas <CAS_NAME> model <CAS_MODEL> license-id <LICENSE_ID> image-id <IMAGE_ID>\nview\nstart <CAS_NAME>\nview')
  st.markdown('NAME、TYPE、MODEL、IMAGE ID、LICENSE IDを照合し、`Created`から`Starting`を経て`Running`を確認します。')
 with t[2]:
  cmd('enable\nconfigure\napplications\nattach-console <CAS_NAME>')
  st.markdown('Enterを3回押し、`2) Setup console`を選択。IP、mask、gateway、DNS、Console/Enable Passwordを設定。Gateway/DNSは同一サブネットのNICへ設定。完了後は`Ctrl + ]`。')
 with t[3]:
  st.markdown('`https://<CAS-VA_IP>:8082/`へAdminでログイン。`Utilities > System Information`をUTF-8の`保守機CASsysinfo.txt`として保存。serialNumber=License ID、version=Image ID、System Status=OKを確認。')
 with t[4]:
  st.markdown('`Utilities > Configuration > Upload Entire Configuration > Choose File`から`CASconfig.xml`を復元。エラーは案件記録へ残します。')
 with t[5]:
  subt=st.tabs(['License','Interface','Access/Routes','Proxy/Users','LDAP/RADIUS','Report/SNMP','List/Banner','NTP/Cache'])
  with subt[0]:st.markdown('`System > Licensing`でActive化。インターネット接続がない場合は現地実施。')
  with subt[1]:cmd('show full-configuration interface\ninterface 0:0 speed ?\ninterface 0:0 speed 100 duplex full\nshow full-configuration interface')
  with subt[2]:cmd('web-management access-list 192.168.0.0/24\nshow full-configuration web-management\nip route 192.168.45.0 255.255.255.0 10.0.0.1 metric 10')
  with subt[3]:st.markdown('`Settings > Proxy`、`Settings > Users > Local Users`。保存後、新資格情報で再ログイン確認。')
  with subt[4]:st.markdown('LDAP/RADIUS Server、Credentials、Search Criteria、User/Group Role Mappingを設定。')
  with subt[5]:st.markdown('StatisticsのEmail Day ReportをSchedule。`Settings > Alerts > SNMP Trap`を設定。')
  with subt[6]:st.markdown('Whitelist/Blacklist CSVをBulk Import。Content BannerのTextとLogoを設定。')
  with subt[7]:st.markdown('NTP Server追加・削除。SandboxingのThreats Cache/Clean Cacheを設定。')
 with t[6]:st.markdown('UTF-8で`キッティング後CASsysinfo.txt`と`キッティング後CASconfig.xml`を保存し、提供ファイルと比較。意図しない差分はエスカレーション。CLI/Web/System Statusも再確認。')
 with t[7]:
  cmd('enable\nshutdown\n# safe to power offを確認しCtrl+]\nconfigure\napplications\nstop <CAS_NAME>\nview')
  st.markdown('最後にSTATUS=`Stopped`を確認します。')
elif page=='🔐 SSLV→SSLV':
 st.title('🔐 SSLVからSSLV')
 st.markdown('DiagnosticsからOS/SN/Model/NICを確認。同一モデル・NICを選定。Serialは115200/8/none/1/none。Full BackupまたはPKI→Policy→Platformで復元し、Diagnostics差分を確認。Backupなしなら完全復元不可、PKIなしなら新CAと再配布が必要。')
elif page=='🔄 SSLV→SSP':
 st.title('🔄 SSLVからSSP')
 st.markdown('**Upgrade:** 2.4.10.1以前は `2.4.10.1 → 2.5.4.2 → 2.5.5.1`、2.5.xは2.5.5.1へ。SSLV 6.2.1.1以上を使用。')
 cmd('installed-systems view\ninstalled-systems load http://<WEB_SERVER>/<FIRMWARE.bcsi>\nrestart\nhealth-monitoring view current')
 st.markdown('sslv-netdefを作成。旧物理SSLVがSlot3以外なら末尾ポート番号を維持してSlot3へ再割当。')
elif page=='📦 保守機材':
 st.title('📦 保守機材選定')
 st.markdown('選定順: **同一系統・性能モデル → NIC型式/Slot適合 → 保管状態 → 倉庫/現地条件**')
 assets=['SSP-S210-10-PR','SSP-S410-10-PR','SSP-S410-20-PR','SSP-S410-20B-PR','SV-S550-5','SV-S550-10','NIC-4X1G-10G-SRD-SFP-NBP','NIC-4X10GIG-LC-BP','Java用キッティングPC']
 q=st.text_input('検索').lower();st.dataframe([{'品名':x,'状態':'保管中'} for x in assets if q in x.lower()],use_container_width=True,hide_index=True)
elif page=='🏢 現地交換':
 st.title('🏢 現地交換・完了')
 for i,x in enumerate(['入館・開始報告','障害機S/N照合','配線撮影/タグ','お客様に停止依頼','LED消灯後に抜線','保守機搭載','最初は管理Portのみ','電源Cable 2本','Health確認','Application Running','通信Port接続','お客様業務確認','報告書・故障機回収・退館'],1):check(f'site{i}',x)
elif page=='✅ 品質ゲート':
 st.title('✅ 品質ゲート')
 tabs_steps([('開始条件','契約・S/N・Model、Backup、保守機/NIC、Version/License、作業ログを確認。'),('出荷条件','Model/SN/Version/License、Health、差分、CLI/Web、成果物を確認。'),('停止条件','手順外操作、Health異常、Model/NIC不一致、復元エラー、資料矛盾は即時停止・エスカレーション。')])
elif page=='📋 ケース管理':
 st.title('📋 ケース管理');c=cur()
 with st.form('case'):
  c['case_no']=st.text_input('ケース番号',c.get('case_no',''));c['customer']=st.text_input('お客様名',c.get('customer',''));c['model']=st.text_input('モデル',c.get('model',''));c['serial']=st.text_input('S/N',c.get('serial',''));c['status']=st.selectbox('状態',['未対応','切り分け中','準備中','作業中','完了'],index=['未対応','切り分け中','準備中','作業中','完了'].index(c.get('status','未対応')));st.form_submit_button('反映')
elif page=='🕘 タイムライン':
 st.title('🕘 タイムライン');c=cur()
 with st.form('timeline',clear_on_submit=True):
  a,b=st.columns(2);d=a.date_input('日付');tm=b.time_input('時刻');kind=st.selectbox('種別',['顧客連絡','PFU依頼','部材発送','作業','回収','クローズ','メモ']);text=st.text_area('内容');ok=st.form_submit_button('追加')
 if ok and text:c['timeline'].append({'date':datetime.combine(d,tm).isoformat(),'type':kind,'text':text});st.rerun()
 for x in reversed(c['timeline']):st.markdown(f"**{x['type']}** {x['date']}  \n{x['text']}")
elif page=='💾 JSON管理':
 st.title('💾 JSONデータ管理');D['saved_at']=datetime.now().isoformat();raw=json.dumps(D,ensure_ascii=False,indent=2).encode();st.download_button('全データJSON保存',raw,'hardware_runbook.json','application/json',type='primary')
 up=st.file_uploader('JSONインポート',type='json')
 if up and st.button('読込'):
  obj=json.load(up)
  if 'cases' in obj:st.session_state.data=obj;st.rerun()
