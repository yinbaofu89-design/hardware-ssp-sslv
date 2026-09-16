# Symantec ハードウェア修理 統合ランブック

HTML完全版をベースに、Streamlit標準テーマ、CAS-VA C-1～C-31相当、ケース管理、タイムライン、JSON保存を統合した版です。

## ログイン

- ユーザー名: `baofu`
- パスワード: `Oosaka197982$`

## 起動

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Streamlit Community Cloud

`app.py`、`requirements.txt`、`README.md`を同じ階層に置き、Main file pathへ`app.py`を指定します。

## 固定バージョン

```text
streamlit==1.49.1
```

## 修正点

- Streamlit標準テーマを使用
- `st.datetime_input`を使用しない
- `st.dataframe`の未対応な`columns`引数を使用しない
- `hide_index`を使用しない
- 資料対応表は辞書行のリストとして表示
- CAS-VA C-1～C-31相当を維持

## 保存

作業終了前に「JSON管理」からケースJSONをダウンロードしてください。
