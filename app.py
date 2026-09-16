import streamlit as st, json, uuid
from datetime import datetime
st.set_page_config(page_title='Symantec ハードウェア修理 統合ランブック',page_icon='🛠️',layout='wide')
# Streamlit標準テーマを使用します。背景色・文字色・タブ色は上書きしません。
st.markdown("""
<style>
.block-container { max-width: 1500px; }
</style>
""", unsafe_allow_html=True)
USERNAME='baofu';PASSWORD='Tamachi2609'
if not st.session_state.get('auth'):
 st.title('🔐 Hardware Repair Runbook')
 with st.form('login'):
  u=st.text_input('ユーザー名');p=st.text_input('パスワード',type='password');go=st.form_submit_button('ログイン',type='primary')
 if go:
  if u==USERNAME and p==PASSWORD:st.session_state.auth=True;st.rerun()
  else:st.error('ユーザー名またはパスワードが正しくありません。')
 st.stop()
def blank():return {'id':uuid.uuid4().hex,'case_no':'','customer':'','serial':'','model':'','contract':'','received':'','contact':'','phone':'','site':'','preferred':'','product':'','status':'受付','issue':'','memo':'','checks':{},'assets':[],'timeline':[],'templates':{}}
if 'db' not in st.session_state:st.session_state.db={'schema_version':3,'cases':[blank()],'current':None,'saved_at':''};st.session_state.db['current']=st.session_state.db['cases'][0]['id']
D=st.session_state.db
def case():return next((c for c in D['cases'] if c['id']==D['current']),None)
def ck(key,text):
 c=case();v=st.checkbox(text,value=c['checks'].get(key,False),key=key+c['id']);c['checks'][key]=v;return v
def checklist(prefix,items):
 for i,x in enumerate(items):ck(f'{prefix}.{i}',x)
def code(x):st.code(x,language='shell')
def tabs(labels,bodies):
 for t,b in zip(st.tabs(labels),bodies):
  with t:b()
INV=[('SSP-S410-10-PR','西日本・松山倉庫','GP524169','1921700015'),('SSP-S410-20-PR','西日本・北九州倉庫','GP524172','1422700035'),('SSP-S210-10-PR','宇都宮ＷＨ','GP524176','123710030'),('SSP-S210-10-PR','神戸ＷＨ','GP524184','223710032'),('SSP-S210-10-PR','大阪ロジスティック倉庫','GP524185','1922710014'),('SSP-S410-10-PR','大阪ロジスティック倉庫','GP524186','1921700022'),('SSP-S410-10-PR','大阪ロジスティック倉庫','GP524187','1921700034'),('SSP-S410-20-PR','大阪ロジスティック倉庫','GP524188','221700049'),('SV-S550-5','大阪ロジスティック倉庫','GP524189','3922610001'),('SV-S550-5','大阪ロジスティック倉庫','GP524190','524610017'),('SV-S550-10','大阪ロジスティック倉庫','GP524191','3922610002'),('SSP-S210-10-PR-OKI','東京ロジスティック倉庫','GP524214','1922710096'),('SSP-S210-10-PR-OKI','東京ロジスティック倉庫','GP524215','1422710001'),('SSP-S210-10-PR','東京ロジスティック倉庫','GP524216','3524710013'),('SSP-S210-10-PR','東京ロジスティック倉庫','GP524217','3524710002'),('SSP-S410-10-PR','東京ロジスティック倉庫','GP524218','1921700013'),('SSP-S410-10-PR-SME','東京ロジスティック倉庫','GP524219','1921700043'),('SSP-S410-10-PR','東京ロジスティック倉庫','GP524220','4720700059'),('SSP-S410-20-PR','東京ロジスティック倉庫','GP524221','2722700138'),('SSP-S410-20-PR','東京ロジスティック倉庫','GP524222','1422700078'),('SSP-S410-20-PR','東京ロジスティック倉庫','GP524223','4020700027'),('SSP-S410-20B-PR','東京ロジスティック倉庫','GP524224','4222700037'),('SSP-S410-20B-PR','東京ロジスティック倉庫','GP524225','4222700015'),('SSP-S410-20B-PR','東京ロジスティック倉庫','GP524226','2423700018'),('SV-S550-5','東京ロジスティック倉庫','GP524227','3222610016'),('SV-S550-10','東京ロジスティック倉庫','GP524228','3222610007'),('NIC-4X1G-10G-SRD-SFP-NBP','東京ロジスティック倉庫','GP525824','2305316068'),('NIC-4X1G-10G-SRD-SFP-NBP','大阪ロジスティック倉庫','GP525825','2412184173'),('NIC-4X10GIG-LC-BP','東京ロジスティック倉庫','GP525826','2408056224'),('NIC-4X10GIG-LC-BP','大阪ロジスティック倉庫','GP525827','2409136107'),('Java用キッティングPC','東京ロジスティック倉庫','GP526118','0F387FV24013GT'),('Java用キッティングPC','大阪ロジスティック倉庫','GP526120','0F387KG24013GT')]
with st.sidebar:
 st.title('🛠️ Repair Runbook');c=case();st.caption(f"Case: {c['case_no'] or '未設定'}")
 page=st.radio('メニュー',['🏠 全体の流れ','📋 ケース情報','🔍 障害切り分け','📥 情報の依頼','📦 保守機材の選定','🧰 SSPリストア','🌐 SSP上のSG','🧪 CAS-VA','🔐 SSLV→SSLV','🔄 SSLV→SSP','🏢 現地交換・完了','✅ 品質ゲート','📚 資料対応表','🕘 タイムライン','💾 JSON管理'])
 if st.button('ログアウト'):st.session_state.clear();st.rerun()
if page=='🏠 全体の流れ':
 st.title('🏠 Symantec ハードウェア修理 統合ランブック');st.error('関係者外秘。手順書にない作業やコマンドは実施せず、特別対応・不明点・異常はサポートへエスカレーション。')
 cols=st.columns(7)
 for col,(a,b) in zip(cols,[('受付','契約'),('切分','LED'),('情報','証跡'),('選定','機材'),('復元','版数'),('現地','交換'),('完了','検証')]):col.metric(a,b)
 checklist('flow',['ケース作成・契約確認','起動、LED、Console、Self-check','設定・診断・バックアップ','同一モデル、NIC、倉庫、状態','版数整合、ライセンス、設定','交換、起動、顧客確認'])
elif page=='📋 ケース情報':
 st.title('📋 ケース情報・連絡テンプレート');c=case()
 with st.form('case'):
  a,b,d=st.columns(3)
  fields=[('case_no','ケース番号'),('customer','顧客名'),('serial','対象機シリアル番号'),('model','対象モデル'),('contract','契約番号'),('received','受付日時'),('contact','顧客担当者'),('phone','連絡先'),('site','設置場所'),('preferred','作業希望日時')]
  for i,(k,l) in enumerate(fields):c[k]=[a,b,d][i%3].text_input(l,c.get(k,''))
  c['product']=st.selectbox('製品区分',['','SSP','SG-VA','CAS-VA','SSLV','SSLV → SSP'],index=['','SSP','SG-VA','CAS-VA','SSLV','SSLV → SSP'].index(c.get('product','')));c['status']=st.selectbox('対応状況',['受付','切り分け中','情報待ち','保守機選定','キッティング中','現地作業予定','完了'],index=['受付','切り分け中','情報待ち','保守機選定','キッティング中','現地作業予定','完了'].index(c.get('status','受付')));c['issue']=st.text_area('障害概要',c.get('issue',''));c['memo']=st.text_area('社内メモ',c.get('memo',''));st.form_submit_button('反映',type='primary')
 st.subheader('一次連絡用テンプレート');st.text_area('編集可能',f"件名：【{c['case_no']}】ハードウェア障害受付のご連絡\n{c['customer']} ご担当者様\nハードウェア障害のご連絡を受け付けました。\n対象機器：{c['model']}\nシリアル番号：{c['serial']}\n障害概要：{c['issue']}\n現在、障害の切り分けと交換準備に必要な情報を確認しています。",height=190)
 st.subheader('フル情報依頼テンプレート');st.text_area('編集可能 ',f"件名：【{c['case_no']}】ハードウェア障害に関する情報ご提供のお願い\n{c['customer']} ご担当者様\n■案件情報\n対象モデル：{c['model']}\nS/N：{c['serial']}\n設置場所：{c['site']}\n障害概要：{c['issue']}\n■共通確認情報\n発生日時、影響範囲、直前変更、電源・起動、LED/LCD、SSH、Serial、Web、Self-check、Health、診断ログ\n■構成・復元情報\nOS/ISG/Image版数、IP/mask/gateway/DNS、Option NIC、Backup、Diagnostics、sysinfo、config、証明書・秘密鍵",height=300)
elif page=='🔍 障害切り分け':
 st.title('🔍 ハードウェア障害切り分け方法')
 tabs(['共通ヒアリング','SSP S410','SSLV SV-S550'],[lambda:checklist('tri',['申告内容、発生日時、影響範囲、直前変更を記録','セルフチェック実行有無と結果','電源・起動可否、異音、再起動ループ','前面・背面LED、LCD表示','SSH、シリアル、Web管理画面','SNMP Trap受信状況とMIB']),lambda:(st.markdown('NMIはISG 2.5.4.1以降、前面IDボタンを10秒長押し。ID LEDが一瞬青く点滅後に再起動。'),code('show json-config\nhealth-monitoring view current')),lambda:st.markdown('NMIは **Menu → Left → Right**。LCD、LED、SSH、シリアル、管理GUIとDiagnosticsのモデル、S/N、OS、CPU、メモリ、センサーを確認。')])
 st.warning('障害と判断できない、ログと症状が矛盾、復旧操作の影響が不明なら交換へ進まずエスカレーション。')
elif page=='📥 情報の依頼':
 st.title('📥 情報の依頼方法')
 tabs(['案件情報','SSP / SG / CAS','SSLV','依頼文'],[lambda:checklist('req1',['受付番号 / ケース番号','契約番号・保守時間帯','お客様名、担当者、連絡先','設置場所、入館条件、作業希望日時','対象機モデル、10桁シリアル','障害内容と切り分け結果','ラック位置、重量物・高所作業、駐車場']),lambda:checklist('req2',['ISG Release、json-config、running config、health、applications、event-log、LAG','ISG IP/mask/gateway/DNS、Console/Enable','SG名称、タイプ、モデル、Image ID、License ID、IP、資格情報','SG config、sysinfo、秘密鍵、SSL証明書、trust_package','CAS名称、タイプ、モデル、Image ID、License ID、IP、資格情報','CASconfig.xml、C-C～C-P資料','バックアップ有無と復元条件の了承']),lambda:checklist('req3',['モデル、S/N、OS版数','Option NIC種類、枚数、slot、board S/N','管理IP/mask/gateway、GUI ID/password、Enable password','Host Categorization','Diagnostics','Full BackupまたはPolicy/PKI/Platformとrestore password','Information、Management Network、License、Host Categorization画面']),lambda:st.markdown('保守会社依頼には、案件・契約・設置・希望日時、モデル/SN、障害内容、Option NIC、選定保守機/SN/倉庫、作業内容、立会会社・作業員、キッティング資料状況を含めます。')])
elif page=='📦 保守機材の選定':
 st.title('📦 保守機材のリスト');q=st.text_input('モデル、倉庫、S/Nで検索').lower();rows=[];c=case()
 for i,(n,w,p,sn) in enumerate(INV,1):
  if q and q not in f'{n} {w} {p} {sn}'.lower():continue
  pick=st.checkbox(f'{i}. {n} | {w} | {p} | {sn}',sn in c['assets'],key='a'+sn)
  if pick and sn not in c['assets']:c['assets'].append(sn)
  if not pick and sn in c['assets']:c['assets'].remove(sn)
  rows.append({'No.':i,'品名':n,'倉庫':w,'預り数':1,'状態':'保管中 1','PFU管理番号':p,'製造番号':sn})
 st.dataframe(rows,use_container_width=True);st.warning('NIC-4X10G-LC-BPはSlot 6/7、NIC-4X1G-10G-SRD-SFP-NBPは3～7。SSP上SSLV移行ではSlot 3前提で、元Slotが異なる場合はsegment調整。')
elif page=='🧰 SSPリストア':
 st.title('🧰 SSPのリストア手順');checklist('ssp',['資料・保守機・MD・Cable・Firmware・License・Check sheet','Serial 9600/8/none/1/flow none、ログ開始','筐体S/Nとjson-config照合','health current確認','同一ISG版数選択またはsystems load','factory defaults初期化','Setup Consoleでnetwork/Console/Enable','SG/CAS license投入とID照合','承認済みall_commands.txt投入','キッティング後ISG_config比較','対象Appを最大2つ構築・復元','App停止、ISG shutdown、成果物送付']);code('show json-config\nshow running-config | nomore\nhealth-monitoring view settings\nshow applications\nevent-log view configuration\nlag view')
elif page=='🌐 SSP上のSG':
 st.title('🌐 SSP上のSG-VAリストア手順');checklist('sg',['Image ID一致imageをload','create sg','viewで各値とCreated','startしRunning','attach-console、Manual setup、network、credentials','sysinfo/eventlog取得・正常性','trust_package適用、download-pathを戻す','configuration-passwords-key復元','必要SSL秘密鍵/証明書復元','Archive ConfigurationからSGconfig','必要時Access-log','SGconfig差分確認','CLI/Web/Health/sysinfo再確認','SG shutdown、ISG stop、Stopped']);st.error('順序厳守: trust_package → configuration-passwords-key → SSL秘密鍵/証明書 → コンフィグ')
elif page=='🧪 CAS-VA':
 st.title('🧪 CAS-VAリストア手順')
 t=st.tabs(['C-1～2 作成','C-3 初期設定','C-4～7 正常性','C-8～10 Config','C-11～25 個別設定','C-26～30 検証','C-31 停止'])
 with t[0]:checklist('cas1',['CAS Image ID一致imageをload','viewでImage/Version一致','create casでName/Model/License/Image','viewでCreated','start後Running']);code('configure\nimages\nload http://<WEB_SERVER_IP>/casma_xxxx.bcsi\nview\nexit\napplications\ncreate cas <CAS_NAME> model <MODEL> license-id <LICENSE_ID> image-id <IMAGE_ID>\nview\nstart <CAS_NAME>\nview')
 with t[1]:checklist('cas2',['attach-console','Trustpackage update完了待ち','Enter×3、Setup console=2','IP/mask/gateway/DNS設定','Console/Enable password','secure serial=No、restrict workstation=No','Ctrl+]でISGへ戻る']);code('configure\napplications\nattach-console <CAS_NAME>\n# 必要時のみ\nattach-console <CAS_NAME> force')
 with t[2]:checklist('cas3',['設定したInterfaceへMD接続','https://<CAS-IP>:8082/へAdminでログイン','Utilities > System InformationをUTF-8で保守機CASsysinfo.txt','serialNumber=CAS License ID','version=CAS Image ID','Home System Status=OK'])
 with t[3]:checklist('cas4',['本編7/8/9、CAS C-1/C-3完了確認','Utilities > Configuration','Upload Entire Configuration','CASconfig.xml選択','restore errorを記録'])
 with t[4]:
  subs=st.tabs(['License','Interface','Access-list','Routes','Proxy','Users','LDAP','RADIUS','Report','SNMP','White/Black','Banner','NTP','Sandbox'])
  texts=['System > Licensing。Internet接続不可なら現地実施。Save Changes後Ctrl+F5。','CASinterface.txtを参照。autoなら不要。差分があれば全Interface。','CLIでweb-management access-listを設定。','Settings > Network Routes。GUI保存不可時はip route/no ip route。','Settings > Proxy。認証設定も復元。','Settings > Users > Local Users。保存後、新資格情報で再ログイン。','LDAP Settings上段を保存後、User/Group Role Mapping。','RADIUS Server/Alternate Server、User/Group Role Mapping。','Statistics各TabのEmail Day Report > Schedule。','Settings > Alerts > SNMP Trap。一度削除保存後、再入力。OS 2.x/3.xはCommunityが再表示されない場合あり。','Services > Whitelist/Blacklist。CSVをBulk Import。','Settings > Content Banner。Show、Text、Logoを復元。','Settings > NTP。必要に応じ一時EnableしServer追加/削除後、元状態へ。','Services > Sandboxing > Cache。Threats Cache/Clean Cache。']
  for tab,txt in zip(subs,texts):
   with tab:st.markdown(txt)
  code('show full-configuration interface\ninterface 0:0 speed ?\ninterface 0:0 speed 100 duplex full\nweb-management access-list 192.168.0.0/24\nshow full-configuration web-management\nip route 192.168.45.0 255.255.255.0 10.0.0.1 metric 10')
 with t[5]:checklist('cas5',['キッティング後CASsysinfo.txtをUTF-8保存','Get Configurationでキッティング後CASconfig.xml','顧客CASconfig.xmlと比較','差分があればエスカレーション','CLI access','Web access','System Status OK'])
 with t[6]:checklist('cas6',['ISGでApp Running確認','attach-console CAS','CAS enable > shutdown','safe to power off確認','Ctrl+]','ISG applications stop','viewでStopped']);code('configure\napplications\nview\nattach-console <CAS_NAME>\n# CAS側\nenable\nshutdown\n# ISGへ戻る\nstop <CAS_NAME>\nview')
elif page=='🔐 SSLV→SSLV':
 st.title('🔐 SSLVからSSLVへのリストア手順');checklist('sv',['DiagnosticsでOS/SN/Model/NIC','同一SV-S550 Model/NIC/Slot選定','ACL A Disabled/B same segment/C other segment分類','Serial 115200/8/none/1/none','電源OFF・抜線でNIC装着、GUIでSlot/Model','LED/LCD、CPU<60%、memory free≠0、sensor OK','同一5.x OS、3.x/4.x間upgrade/downgrade不可','License Upload、restart、状態確認','Full BackupまたはPKI→Policy→Platform','Full/PolicyでAllow policies other appliancesとEnable segment activation','Type C ACL一時disable、検証後enable','復元後Diagnostics差分','License Auto-Update Disabled、画面取得','資料とログ提出、shutdown、梱包']);st.error('Backupなしは完全復元不可。PKIなしは新CA証明書とクライアント再配布が必要。')
elif page=='🔄 SSLV→SSP':
 st.title('🔄 SSLVからSSPへのリストア手順');st.info('SSLV-550 Full BackupをSSP上SSLVへ復元するには、ISG 2.5.5.1以上とSSLV 6.2.1.1以上。');checklist('s2s',['IIS MIME .bcsi/.bctp、wwwroot','installed-systems view','段階ごとload','default確認後restart','Current running system確認','2.5.5.1以上でhealth','SSLV License投入','SSLV 6.2.1.1以上image load','sslv-netdef: 0:0 shared、通信Port passthrough','S410-20B=C32XS-3、S410-40B=C64L-3','Full Backupを2項目check付きrestore','旧Slot≠3なら末尾維持してSlot3へsegment再割当','ACLを戻す','復元後Diagnostics比較']);code('installed-systems view\ninstalled-systems load http://<WebServer>/<firmware.bcsi>\nrestart\nhealth-monitoring view current')
elif page=='🏢 現地交換・完了':
 st.title('🏢 現地交換・完了');checklist('on',['現地到着・入館・開始報告','障害機S/N照合','交換機単体起動、App Stopped確認後shutdown','お客様停止了承','Rack/配線撮影・marking、必要時seal移設','障害機shutdown、LED消灯後抜線・撤去','立会いで保守機搭載・配線復元','起動許可、ISG Health','App start、Running、CLI/Web','SG Content Filter、CAS License Active','顧客端末で業務確認','作業説明・報告書承認・障害機梱包・退館']);st.warning('SSLV交換は最初に管理Portのみ接続し、確認後に停止して通信Port接続。電源Cableは2本。')
elif page=='✅ 品質ゲート':
 st.title('✅ 品質ゲートとエスカレーション');tabs(['開始条件','出荷条件','即時停止条件'],[lambda:checklist('q1',['契約・S/N・Model確定','資料・Backup有無','保守機/NIC選定','Version/License','作業ログ開始']),lambda:checklist('q2',['Model/SN/Version/License照合','Hardware Health基準内','復元差分許容','CLI/Web','成果物/画面/log提出']),lambda:checklist('q3',['手順外操作','Health異常、Model/NIC不一致','設定差分、復元error、log異常','標準範囲外依頼','判断不能または資料矛盾'])])
elif page=='📚 資料対応表':
 st.title('📚 資料対応表')
 docs_rows=[
  {'資料':'ハードウェア障害関連対応フロー.docx','統合先':'受付、切り分け、情報依頼、エスカレーション','注意':'一次判断'},
  {'資料':'保守機リスト.xlsx','統合先':'保守機材','注意':'260730'},
  {'資料':'ハードウェア修理フォローver8 (1).pdf','統合先':'全体フロー、連絡、完了','注意':'他資料と整合'},
  {'資料':'SSP保守手順書_本編','統合先':'SSP、現地','注意':'Ver.3.1'},
  {'資料':'SG-VA構築編','統合先':'SSP上SG','注意':'順序依存'},
  {'資料':'CAS-VA構築編','統合先':'CAS','注意':'C-C～C-P'},
  {'資料':'SSLVA Ver5.x S550','統合先':'SSLV→SSLV','注意':'Ver.1.2、検証中'},
  {'資料':'SSP410で故障したSSLV','統合先':'SSLV→SSP','注意':'Slot3'},
  {'資料':'SSP-410 ISGアップグレード','統合先':'SSLV→SSP','注意':'段階upgrade'}
 ]
 st.dataframe(docs_rows,use_container_width=True)
elif page=='🕘 タイムライン':
 st.title('🕘 タイムライン');c=case()
 with st.form('tl',clear_on_submit=True):
  a,b=st.columns(2);d=a.date_input('日付');tm=b.time_input('時刻');kind=st.selectbox('種別',['顧客連絡','PFU依頼','部材発送','作業','回収','クローズ','メモ']);text=st.text_area('内容');go=st.form_submit_button('追加')
 if go and text:c['timeline'].append({'date':datetime.combine(d,tm).isoformat(),'type':kind,'text':text});st.rerun()
 for x in reversed(c['timeline']):st.markdown(f"**{x['type']}** {x['date']}  \n{x['text']}")
elif page=='💾 JSON管理':
 st.title('💾 JSON管理');D['saved_at']=datetime.now().isoformat();raw=json.dumps(D,ensure_ascii=False,indent=2).encode();st.download_button('ケースJSON保存',raw,'hardware_runbook_cases.json','application/json',type='primary');up=st.file_uploader('ケースJSON読込',type='json')
 if up and st.button('読込'):
  obj=json.load(up)
  if 'cases' in obj:st.session_state.db=obj;st.rerun()
 if st.button('＋ 新規ケース'):n=blank();D['cases'].append(n);D['current']=n['id'];st.rerun()
