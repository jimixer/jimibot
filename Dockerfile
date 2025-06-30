# ベースイメージとして Python 3.11-slim を使用
FROM python:3.11-slim

# 環境変数を設定
ENV PYTHONUNBUFFERED=1

# ワーキングディレクトリを設定
WORKDIR /app

# requirements.txt をコピーしてライブラリをインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# src ディレクトリをコンテナにコピー
COPY src/ ./src/
COPY config/ ./config/

# コンテナ起動時のコマンド
CMD ["python", "-u", "src/main.py"]