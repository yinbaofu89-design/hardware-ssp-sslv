# Symantec ハードウェア修理 統合ランブック

アップロードされたHTML版の内容をStreamlitへ統合し、背景色と文字色はStreamlit標準テーマへ戻した版です。

## ログイン

- ユーザー名: `baofu`
- パスワード: `Oosaka197982$`

## 起動

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Streamlit Community Cloud

`app.py`、`requirements.txt`、`README.md`を同じ階層に配置し、Main file pathへ`app.py`を指定します。

## 表示テーマ

アプリ側では背景色、文字色、サイドバー色、タブ色、ボタン色を上書きしていません。Streamlitの標準テーマ、またはユーザーがStreamlitで選択したテーマに追従します。

## 保存

作業終了前に「JSON管理」からケースJSONをダウンロードしてください。
