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

初回実行時に必要なテーブルと管理者用アカウントが作成されます。

## 5. 初回ログイン後の設定
初期管理者でログイン後、運用用の管理者アカウントを作成してください。
運用用管理者アカウント作成後に、初期管理者adminは無効化してください。