# Quick Start

## 1.　必要環境
- Python 3.13
- pip

## 2. 仮想環境の作成

### macOS / Linux
```bash
python3 -m venv env
source env/bin/activate
```
### Windows
python -m venv env
env\Scripts\activate

## 3. ライブラリのインストール
pip install -r requirements.txt

## 4. アカウントの初期設定
プロジェクト直下で `.env.example` をコピーして `.env` を作成し、
初期管理者の情報を設定します。

```bash
cp .env.example .env
```
.envの中身

INITIAL_ADMIN_USERNAME=123admin
INITIAL_ADMIN_PASSWORD=admin123

※ 上記はポートフォリオ用の初期値です。
実運用では変更してください。

## ５. データベースの初期設定
python init_db.py

初回実行時に必要なテーブル、管理者用アカウントとサンプル店舗が作成されます。

## ６.　起動方法
streamlit run app.py

streamlit経由で起動します。

## ７. 予測機能の動作確認

初期管理者でログインすると、初回セットアップ画面へ進みます。

従業員番号　123admin
パスワード　admin123

※ 上記はポートフォリオ用の初期値です。
実運用では変更してください

### 初回セットアップ手順

1. 「Browse files」ボタンからサンプルCSVファイルを選択。
2. CSVファイルの内容を確認。
3. 「予測を実行」を選択。
4. 来局データがDBへ登録され、初回予測が実行されます。
5. 予測結果が登録されると、ダッシュボードに当日の状況が反映されます。

使用するサンプルCSVは `sample_data` フォルダにあります。

### 2回目以降の予測

2回目以降は、来局データを登録前に確認できるように、
「DBへ保存」と「予測を実行」の2段階で操作します。

1. 「Browse files」からCSVファイルを選択。
2. CSVファイルの内容を確認。
3. 「DBへ保存」を選択して、来局データをDBへ保存。
4. DBへの登録内容を確認。
5. 「予測を実行」を選択して予測を実行。

## 実際の運用時の想定
初期管理者でログイン後、運用用の管理者アカウントを作成してください。
運用用管理者アカウント作成後に、初期管理者adminは無効化してからの運用を想定しています。
