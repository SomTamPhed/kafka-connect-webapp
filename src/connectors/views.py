from flask import Blueprint, flash, redirect, render_template, request, url_for, send_file
from flask_login import login_required
from werkzeug.utils import secure_filename
import requests
import json
from sqlalchemy import exc
from requests.exceptions import HTTPError

from src import db
from src.accounts.models import User
from src.connectors.models import Connectors

connectors_bp = Blueprint("connectors", __name__)


@connectors_bp.route("/connectors", methods=["GET", "POST"])
@login_required
def connectors():
    connector_list = Connectors.query.all()
    button_all = 0
    button_config = 0

    for connector in connector_list:
        host = connector.worker_host
        port = connector.worker_port
        name = connector.name
        connector_url = f'http://{host}:{port}/connectors/{name}'
        worker_url = f'http://{host}:{port}'
        try:
            res_worker = requests.get(worker_url)
            res_worker.raise_for_status()
            button_all = 1
        except HTTPError as http_err:
            flash(f"Worker {host}:{port} seems to be offline", "danger")
            pass
        except Exception as err:
            flash(f"Worker {host}:{port} seems to be offline", "danger")
            pass
        except requests.ConnectionError as error:
            flash(f"Worker {host}:{port} seems to be offline", "danger") 
            pass
        if button_all == 1:
            try:
                res_connector = requests.get(connector_url)
                res_connector.raise_for_status()
            except HTTPError as http_err:
                button_config = 1
                #flash(f"{name} seems not to be configured yet", "info")
                pass
            except Exception as err:
                button_config = 1
                #flash(f"{name} seems not to be configured yet", "info")
                pass
            except requests.ConnectionError as error:
                button_config = 1
                #flash(f"{name} seems not to be configured yet", "info") 
                pass
    return render_template('connectors/connectors.html', connector_list=connector_list, button_all=button_all, button_config=button_config)


@connectors_bp.route("/add_connector", methods=['GET', 'POST'])
@login_required
def add_connector():
    if request.method == 'POST':
        if request.form.get('add_connector'):
            connector_name = request.form.get('connector_name')
            connector_host = request.form.get('connector_host')
            connector_port = request.form.get('connector_port')
            if connector_name == '' or connector_host == '' or connector_port == '':
                flash("All the fields are mandatory", "danger")
            else:
                try:
                    create_connector = Connectors(name=connector_name, worker_host=connector_host, worker_port=connector_port)
                    db.session.add(create_connector)
                    db.session.commit()
                    flash("Successfully added to DB", "success")
                except exc.SQLAlchemyError as e:
                    error = str(e.__dict__['orig'])
                    flash(f"DB Error:{error}", "danger")
                    pass
        elif request.form.get('cancel_action'):
            return render_template('connectors/add_connector.html')
    return render_template('connectors/add_connector.html')


@connectors_bp.route('/get_config')
@login_required
def get_config():
    # Retrieve ID details from DB
    my_id = request.args.get('id')
    db_id = Connectors.query.get(my_id)
    db_connector_name = db_id.name
    db_connector_host = db_id.worker_host
    db_connector_port = db_id.worker_port
    try:
        base_url = f"http://{db_connector_host}:{db_connector_port}"
        res = requests.get(base_url, timeout=10)
        res.raise_for_status()
        if res.status_code == 200:
            config_url = (base_url + '/connectors/' + db_connector_name + '/config')
            res_config = requests.get(config_url)
            res_json = res_config.json()
            with open(f'src/download/{db_connector_name}.json', 'w') as json_file:
                json.dump(res_json, json_file, indent=4)
                file = f'download/{db_connector_name}.json'
    except HTTPError as http_err:
        flash(f"HTTP Error: {http_err}", "danger")
        pass
    except Exception as err:
        flash(f"Error: {err}", "danger")
        pass
    return send_file(file, as_attachment=True)


@connectors_bp.route('/pause_connector')
@login_required
def pause_connector():
    # Retrieve ID details from DB
    my_id = request.args.get('id')
    db_id = Connectors.query.get(my_id)
    db_connector_name = db_id.name
    db_connector_host = db_id.worker_host
    db_connector_port = db_id.worker_port
    try:
        base_url = f"http://{db_connector_host}:{db_connector_port}"
        res = requests.get(base_url, timeout=10)
        res.raise_for_status()
        if res.status_code == 200:
            pause_url = (base_url + "/connectors/" + db_connector_name + "/pause")
            requests.put(pause_url)
            flash("Successfully paused.", "success")
    except HTTPError as http_err:
        flash(f"HTTP Error: {http_err}", "danger")
        pass
    except Exception as err:
        flash(f"Error: {err}", "danger")
        pass
    return redirect(url_for('connectors.connectors'))


@connectors_bp.route('/resume_connector')
@login_required
def resume_connector():
    # Retrieve ID details from DB
    my_id = request.args.get('id')
    db_id = Connectors.query.get(my_id)
    db_connector_name = db_id.name
    db_connector_host = db_id.worker_host
    db_connector_port = db_id.worker_port
    try:
        base_url = f"http://{db_connector_host}:{db_connector_port}"
        res = requests.get(base_url, timeout=10)
        res.raise_for_status()
        if res.status_code == 200:
            resume_url = (base_url + "/connectors/" + db_connector_name + '/resume')
            requests.put(resume_url)
            flash("Successfully resumed.", "success")
    except HTTPError as http_err:
        flash(f"HTTP Error: {http_err}", "danger")
        pass
    except Exception as err:
        flash(f"Error: {err}", "danger")
        pass
    return redirect(url_for('connectors.connectors'))


@connectors_bp.route('/get_status')
@login_required
def get_status():
    status_json = {}
    # Retrieve ID details from DB
    my_id = request.args.get('id')
    db_id = Connectors.query.get(my_id)
    db_connector_name = db_id.name
    db_connector_host = db_id.worker_host
    db_connector_port = db_id.worker_port
    try:
        base_url = f"http://{db_connector_host}:{db_connector_port}"
        res = requests.get(base_url, timeout=10)
        res.raise_for_status()
        if res.status_code == 200:
            status_url = (base_url + "/connectors/" + db_connector_name + "/status")
            connector_status = requests.get(status_url)
            status_json = connector_status.json()
            name = status_json['name']
            state = status_json['connector']['state']
            worker_id = status_json['connector']['worker_id']
            task_elements = status_json['tasks']
            return render_template('connectors/status_connector.html', name=name, state=state, worker_id=worker_id, task_elements=task_elements, db_connector_name=db_connector_name,
                                    db_connector_host=db_connector_host, db_connector_port=db_connector_port)
    except HTTPError as http_err:
        flash(f"HTTP Error: {http_err}", "danger")
        pass
    except Exception as err:
        flash(f"Error: {err}", "danger")
        pass
    return redirect(url_for('connectors.connectors'))


@connectors_bp.route('/get_task_detail')
@login_required
def get_task_detail():
    task_id = request.args.get('task_id')
    connector_host = request.args.get('connector_host')
    connector_port = request.args.get('connector_port')
    connector_name = request.args.get('connector_name')
    trace_on = 0
    try:
        url = f"http://{connector_host}:{connector_port}/connectors/{connector_name}/tasks/{task_id}/status"
        res = requests.get(url, timeout=10)
        res.raise_for_status()
        if res.status_code == 200:
            connector_status = requests.get(url)
            status_json = connector_status.json()
            state = status_json['state']
            worker_id = status_json['worker_id']
            if state == 'ERROR':
                trace = status_json['trace']
                trace_on = 1
                return render_template('connectors/status_task.html', task=task_id, state=state, worker_id=worker_id, trace=trace, trace_on=trace_on)
    except HTTPError as http_err:
        flash(f"HTTP Error: {http_err}", "danger")
        pass
    except Exception as err:
        flash(f"Error: {err}", "danger")
        pass
    return render_template('connectors/status_task.html', task=task_id, state=state, worker_id=worker_id, trace_on=trace_on)


@connectors_bp.route('/restart_task')
@login_required
def restart_task():
    trace_on = 0
    task_id = request.args.get('task_id')
    connector_host = request.args.get('connector_host')
    connector_port = request.args.get('connector_port')
    connector_name = request.args.get('connector_name')
    base_url = f"http://{connector_host}:{connector_port}/connectors/{connector_name}/tasks/{task_id}/status"
    restart_url = f"http://{connector_host}:{connector_port}/connectors/{connector_name}/tasks/{task_id}/restart"
    try:
        res = requests.get(base_url, timeout=10)
        res.raise_for_status()
        if res.status_code == 200:
            status_json = res.json()
            state = status_json['state']
            worker_id = status_json['worker_id']
            requests.post(restart_url)
            flash("Task has been successfully restarted", "success")
            if state == 'ERROR':
                trace = status_json['trace']
                trace_on = 1
                return render_template('connectors/status_task.html', task=task_id, state=state, worker_id=worker_id, trace=trace, trace_on=trace_on)
    except HTTPError as http_err:
        flash(f"HTTP Error: {http_err}", "danger")
        pass
    except Exception as err:
        flash(f"Error: {err}", "danger")
        pass
    return render_template('connectors/status_task.html', task=task_id, state=state, worker_id=worker_id, trace_on=trace_on)


@connectors_bp.route('/upload_config', methods=['POST', 'GET'])
@login_required
def upload_config():
    connector_id = request.args.get('id')
    if request.method == 'POST':
        f = request.files['file']
        filename = secure_filename(f.filename)
        if filename == '':
            flash("Please choose a json file first.", "danger")
        else:
            f.save('src/upload/' + filename)
            return redirect(url_for('connectors.update_config', connector_id=connector_id, filename=filename))
    return render_template('connectors/update_connector.html')


@connectors_bp.route('/update_config', methods=['POST', 'GET'])
@login_required
def update_config():
    filename = request.args.get('filename')
    connector_id = request.args.get('connector_id')
    db_id = Connectors.query.get(connector_id)
    db_connector_name = db_id.name
    db_connector_host = db_id.worker_host
    db_connector_port = db_id.worker_port
    current_dir = 'src/upload/'
    file_path = f'{current_dir}{filename}'
    with open(file_path) as json_object:
        json_data = json.load(json_object)
    try:
        base_url = f'http://{db_connector_host}:{db_connector_port}'
        res = requests.get(base_url, timeout=10)
        res.raise_for_status()
        if res.status_code == 200:
            update_config = (base_url + '/connectors/' + db_connector_name + '/config')
            requests.put(update_config, json=json_data)
    except HTTPError as http_err:
        flash(f"HTTP Error: {http_err}")
        pass
    except Exception as err:
        flash(f"Error: {err}")
        pass
    return redirect(url_for('connectors.connectors'))


@connectors_bp.route('/delete_connector')
@login_required
def delete_connector():
    # Retrieve ID details from DB
    my_id = request.args.get('id')
    db_id = Connectors.query.get(my_id)
    db_connector_name = db_id.name
    db_connector_host = db_id.worker_host
    db_connector_port = db_id.worker_port
    try:
        base_url = f"http://{db_connector_host}:{db_connector_port}"
        res = requests.get(base_url, timeout=10)
        res.raise_for_status()
        if res.status_code == 200:
            delete_url = (base_url + "/connectors/" + db_connector_name)
            requests.delete(delete_url)
            flash("Successfully deleted.", "success")
            # I do not want to remove the connector from DB yet
            # db_id = Connectors.query.get(my_id)
            # db.session.delete(db_id)
            # try:
            #     db.session.commit()
            # except exc.SQLAlchemyError as e:
            #     error = str(e.__dict__['orig'])
            #     return error
    except HTTPError as http_err:
        flash(f"HTTP Error: {http_err}")
        pass
    except Exception as err:
        flash(f"Error: {err}")
        pass
    return redirect(url_for('connectors.connectors'))


@connectors_bp.route('/remove_fromdb')
@login_required
def remove_fromdb():
    # Retrieve ID details from DB
    my_id = request.args.get('id')
    db_id = Connectors.query.get(my_id)
    db.session.delete(db_id)
    try:
        db.session.commit()
        connector_list = Connectors.query.all()
        flash("Successfully removed from DB.", "success")
    except exc.SQLAlchemyError as e:
        error = str(e.__dict__['orig'])
        flash(f"DB Error: {error}", "danger")
    return render_template('connectors/connectors.html', connector_list=connector_list)