import os
from .settings import PROMPT_PATH

SYSTEM_PROMPT = ""

def load_system_prompt():
    """システムプロンプトをファイルから読み込む"""
    global SYSTEM_PROMPT
    try:
        # プロジェクトルートからの絶対パスでconfig/persona.mdを指定
        # os.path.abspath(__file__) は現在のファイルの絶対パス
        # os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', PROMPT_PATH) はプロジェクトルートからのパスを構築
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        config_path = os.path.join(project_root, PROMPT_PATH)
        with open(config_path, "r", encoding="utf-8") as f:
            SYSTEM_PROMPT = f.read()
        print(f"システムプロンプトを '{config_path}' から読み込みました。")
    except FileNotFoundError:
        print(f"エラー: プロンプトファイル '{PROMPT_PATH}' が見つかりません。デフォルトのプロンプトを使用します。")
        SYSTEM_PROMPT = "あなたは親切で少しユーモアのあるアシスタントです。"
    except Exception as e:
        print(f"プロンプトファイルの読み込み中にエラーが発生しました: {e}。デフォルトのプロンプトを使用します。")
        SYSTEM_PROMPT = "あなたは親切で少しユーモアのあるアシスタントです。"