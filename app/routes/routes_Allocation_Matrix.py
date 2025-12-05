from flask import Blueprint, current_app,jsonify,make_response
from .Allocation_Matrix_service import build_dashboard_payload
from werkzeug.exceptions import InternalServerError
import os

Allocation_Matrix_bp = Blueprint("Allocation_Matrix", __name__, url_prefix="/api/Allocation_Matrix")

# API 用ルート
@Allocation_Matrix_bp.route("/", methods=["GET"])
def index():
    """
    API root: 簡単なメタ情報を返す
    """
    payload = {
        "service": "Portfolio_Command_Center",
        "version": "1.0",
        "endpoints": {
            "graphs": "/api/Allocation_Matrix/graphs",
            "summary": "/api/Allocation_Matrix/summary"
        }
    }
    return jsonify(payload)

@Allocation_Matrix_bp.route("/graphs", methods=["GET"])
def graphs():
    """
    グラフ用データを返すエンドポイント。
    フロントはここから時系列データ・メタ情報を受け取り描画する。
    """
    try:
        payload = build_dashboard_payload(include_graphs=True, include_summary=False)
        # 200 OK
        resp = make_response(jsonify(payload), 200)
        # キャッシュ挙動(必要に応じ調整)
        resp.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        return resp
    except Exception as e:
        import traceback
        traceback.print_exc()
        # ログはアプリ側で出している想定
        raise InternalServerError(description=str(e))


@Allocation_Matrix_bp.route("/summary", methods=["GET"])
def summary():
    """
    サマリ（軽量）だけほしいフロントのための簡易エンドポイント。
    """
    try:
        payload = build_dashboard_payload(include_graphs=False, include_summary=True)
        resp = make_response(jsonify(payload), 200)
        resp.headers["Cache-Control"] = "no-cache"
        return resp
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise InternalServerError(description=str(e))
