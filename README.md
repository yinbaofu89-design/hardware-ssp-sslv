# Symantec ハードウェア修理 統合ランブック Streamlit版

アップロードされた完成版HTMLの全セクションをStreamlitへ再整理し、既存のJSONケース管理、テンプレート、タイムラインと統合しています。

## ファイル

- app.py
- requirements.txt
- README.md

## 起動

```bash
pip install -r requirements.txt
streamlit run app.py
```

## 修正内容

- `st.datetime_input`を廃止し、対応範囲の広い`st.date_input`と`st.time_input`の組み合わせへ変更
- 全体の流れ
- 情報依頼
- SSPリストア
- SG-VA
- CAS-VA
- SSLVからSSLV
- SSLVからSSP
- 現地交換
- 品質ゲート
- 保守機材リスト32件
- 障害切り分け、コマンド、Markdown図
- JSON保存とインポート
- メールテンプレート

## Streamlit Community Cloud

RepositoryとBranchを選択し、Main file pathを`app.py`にしてDeployします。requirements.txtはapp.pyと同じ階層に置きます。

## 注意

- 作業終了前に全ケースJSONを保存してください。
- 手順書にないコマンドは実行せず、担当部門へエスカレーションしてください。
- 保守機材リストはアップロードHTMLに含まれていたスナップショットです。実際の出庫前に最新在庫を確認してください。
