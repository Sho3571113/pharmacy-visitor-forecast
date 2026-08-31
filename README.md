# Pharmacy Visit Forecast System

## 概要
　本システムは、調剤薬局向けの来局者予測システムです。過去の来局者数データからLightGBMで来局者数を予測し適切に薬剤師(ヘルプ要員を含む)を配置することを支援するシステムである。

## システム構成
```
CSV
　↓
SQLite
　↓
LightGBM 学習
　↓
予測
　↓
推奨薬剤師数算出
　↓
Streamlit画面表示
```

## 使用技術
- Python 3.13
- Streamlit
- LightGBM
- Pandas
- Plotly
- SQLite
- SQLAlchemy
- pytest
- Git / GitHub

## 主な機能
- ユーザー管理(ユーザー追加)
- ユーザー認証
- ユーザーアクセス制御
- 店舗管理(店舗追加)
- 店舗ごとのデータ管理
- CSVアップロード、SQLiteへの保存
- LightGBMによる学習
- 来局者数予測
- 推奨薬剤師人数の算出
- 予測結果の保存と表示

## ディレクトリ構成
```
project/
├──tests/
├── add_store.py                                  
├── app.py                         
├── authentication.py                              
├── check_stores.py                       
├── check_users.py
├── create_admin.py
├── db_config.py
├── db_service.py
├── forecast_service.py
├── init_db.py
├── lgbforecast.py
├── models.py
├── pharmacy.db
├── register_user.py
├── staffing_service.py
└── requirements.txt

```
## セットアップ方法
```bash
git clone <repository>

cd project

pip install -r requirements.txt
```

## 実行方法
```bash
streamlit run app.py
```

## テスト
pytestによるテスト実施

対象
・認証機能
・DB操作
・予測処理
・人員配置処理
・アプリ共通処理
　
結果
　38件PASS


## 今後の改善予定
・感染症流行データの特徴量追加
・AWS EC2へのデプロイ

## 開発の流れ
```
生成AIを使う際には

```
