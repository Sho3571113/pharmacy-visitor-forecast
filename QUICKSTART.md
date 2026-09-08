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
初期管理者でログインし、サイドバーの「来局者予測」ページへ進んでください。

使用するサンプルCSVは `sample_data` フォルダにあります。

以下の手順で予測を実行できます。

①「Browse files」ボタンからサンプルCSVファイルを選択。
②CSVファイルが表示されたら「DBへ登録」を選択。
③一番上の「予測を実行」を選択。
④来局者予測グラフと予測結果が表示されたら成功です。

予測結果が登録されると、ダッシュボードに当日の状況が反映されます。

## 実際の運用時の想定
初期管理者でログイン後、運用用の管理者アカウントを作成してください。
運用用管理者アカウント作成後に、初期管理者adminは無効化してからの運用を想定しています。