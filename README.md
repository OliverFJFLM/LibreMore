# LibreMore

LibreMore は、宮崎市内の図書館に所蔵されている蔵書のみを対象に、ユーザーの読書目的から推薦リストを生成し、在架状況やOPAC予約導線まで提示するフルスタックアプリケーションです。

## ディレクトリ構成

- `backend/` FastAPI ベースの API。認証、推薦生成、在架確認、目的・読書進捗管理を提供します。
- `frontend/` Next.js (App Router) による Web UI。目的入力から推薦閲覧、マイページでの進捗管理が可能です。
- `backend/alembic/versions/0001_init.sql` 初期スキーマ。

## セットアップ

1. ルートで `.env` を `.env.example` からコピーし、必要な環境変数を設定します。
2. バックエンド: `cd backend` して `poetry install` 後 `poetry run uvicorn app.main:app --reload`。
3. フロントエンド: `cd frontend` して `npm install` 後 `npm run dev`。

## テスト

- バックエンド: `poetry run pytest`
- フロントエンド: `npm run lint` など必要に応じて実行してください。
