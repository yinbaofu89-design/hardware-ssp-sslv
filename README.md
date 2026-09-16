# ハードウェア修理ランブック Streamlit JSON版

元の手順書の内容を、障害切り分け、事前準備、コンソール接続、正常性確認、初期化、SG-VA、SSLV-VA、現地交換、完了・RMAの個別タブに整理しています。コマンド、確認ポイント、原画像を読み替えた見やすいMarkdown図を含みます。

## ファイル

- app.py
- requirements.txt
- README.md

3ファイルを同じ階層に配置します。

## 起動

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Streamlit Community Cloud

GitHub上のRepositoryとBranchを選択し、Main file pathへ`app.py`を指定してDeployします。

## 保存

作業終了前にJSONデータ管理から全ケースJSONを保存し、再開時にインポートしてください。

## 注意

- コマンドは原手順書で確認できたものだけを掲載しています。
- プレースホルダーは実値に置き換えてください。
- 手順書にない操作やコマンドは実行せず、担当部門へエスカレーションしてください。
- 原資料の埋め込み画像そのものは単一Pythonファイルへ複製せず、画面構成、コンソール出力、接続関係をMarkdownで再表現しています。
