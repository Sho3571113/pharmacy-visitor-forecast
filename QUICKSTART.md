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

## 4. データベースの初期設定
python init_db.py

初回実行時に必要なテーブル、管理者用アカウントとサンプル店舗が作成されます。

## 5.　起動方法
streamlit run app.py

streamlit経由で起動します。

## 6. 予測機能の動作確認
初期管理者でログインすると、初回セットアップ画面へ進みます。

初回セットアップ手順

「Browse files」ボタンからサンプルCSVファイルを選択。
 CSVファイルが表示されたら「DBへ保存」を選択。
 その後、サイドバーから「ダッシュボード」を選択。

 予測結果が登録されると、ダッシュボードに当日の状況が反映されます。

使用するサンプルCSVは `sample_data` フォルダにあります。

## 実際の運用時の想定
初期管理者でログイン後、運用用の管理者アカウントを作成してください。
運用用管理者アカウント作成後に、初期管理者adminは無効化してからの運用を想定しています。

予測の手順について
初回セットアップ後は、サイドバーの予測