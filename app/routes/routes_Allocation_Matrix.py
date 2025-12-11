from flask import Blueprint, current_app,jsonify,make_response, request
from .Allocation_Matrix_service import build_dashboard_payload, get_graph_details
from werkzeug.exceptions import InternalServerError
import os
from .routes_helper import apply_etag

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
        return apply_etag(payload)
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
        return apply_etag(payload)
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise InternalServerError(description=str(e))

@Allocation_Matrix_bp.route("/details", methods=["GET"])
def details():
    """
    グラフ詳細データを返すエンドポイント
    Query Params:
      - graph_id: グラフID (例: liquidity_horizon)
      - sub_type: 資産サブタイプ (例: Domestic Equity) ※フィルタ用
    """
    try:
        graph_id = request.args.get("graph_id")
        sub_type = request.args.get("sub_type")
        
        params = {}
        if sub_type:
            params["sub_type"] = sub_type
            
        result = get_graph_details(graph_id, params)

        return apply_etag(result)
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise InternalServerError(description=str(e))

