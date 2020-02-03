from flask import jsonify, request

from flask_monitoringdashboard.controllers.profiler import get_profiler_table, get_grouped_profiler
from flask_monitoringdashboard.database import session_scope

from flask_monitoringdashboard.core.auth import secure

from flask_monitoringdashboard import blueprint
from flask_monitoringdashboard.database.count import count_profiled_requests


@blueprint.route('/api/num_profiled/<endpoint_id>')
@secure
def num_profiled(endpoint_id):
    with session_scope() as db_session:
        return jsonify(count_profiled_requests(db_session, endpoint_id))


@blueprint.route('/api/profiler_table/<endpoint_id>/<offset>/<per_page>')
@secure
def profiler_table(endpoint_id, offset, per_page):
    sort_by = request.args.get('sortby', 'latest')
    response_status = request.args.get('response_status', 'all').lower()
    with session_scope() as db_session:
        return jsonify(get_profiler_table(db_session, endpoint_id, offset, per_page, sort_by, response_status))


@blueprint.route('/api/grouped_profiler/<endpoint_id>')
@secure
def grouped_profiler(endpoint_id):
    with session_scope() as db_session:
        return jsonify(get_grouped_profiler(db_session, endpoint_id))
