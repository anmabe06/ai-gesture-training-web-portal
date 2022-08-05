import os
import time

from typing import List

from flask import (
    Flask,
    jsonify,
    redirect,
    render_template,
    request,
)
from flask_navigation import Navigation

from src import config
from src.gesture_manager.gesture_manager import GestureManager
from src.gesture_manager.gesture import Gesture


app = Flask(__name__, template_folder='.')
app.config["JSONIFY_PRETTYPRINT_REGULAR"] = True

# navigation bar
nav = Navigation(app)
nav.Bar('top', [
    nav.Item('Collect', 'collect'),
    nav.Item('Train', 'train'),
    nav.Item('Play', 'play'),
])

gm = GestureManager(config.LOCAL_DATA_PATH)


@app.route('/')
def index():
    return redirect('/train')


@app.route("/collect")
def collect():
    namespace_selected = request.args.get('namespace', None)
    gesture_selected = request.args.get('gesture', None)
    step_number = request.args.get('sn', None)

    csv_filepath = os.path.join(config.ROOT_DIR, 'gestures_list.csv')
    gestures: List[Gesture] = gm.get_gestures_from_csv_file(csv_filepath)
    namespaces = list(set([g.namespace for g in gestures]))
    gestures = [g.name for g in gestures if g.namespace == namespace_selected]

    if namespace_selected and gesture_selected:
        g = Gesture(namespace_selected, gesture_selected, gm)
        gesture = dict(
            name=gesture_selected,
            sample_video=g.create_sample_video_link()
        )
    else:
        gesture = None

    return render_template(
        'collect.html',
        namespaces=namespaces,
        namespace_selected=namespace_selected,
        gesture_selected=gesture_selected,
        gesture=gesture,
        gestures=gestures,
        step_number=step_number
    )


@app.route("/train")
def train():
    # todo: wip
    namespace_selected = request.args.get('namespace', None)
    namespace_data = gm.get_samples_data_from_s3_namespace(namespace_selected) \
        if namespace_selected else None

    return render_template(
        'train.html',
        namespaces=gm.s3_namespaces,
        namespace_selected=namespace_selected,
        namespace_data=namespace_data
    )


@app.route("/play")
def play():
    # todo: wip
    return '<p>Under construction</p>'


@app.route('/upload',methods=['post'])
def upload():
    "Uploads a sample video file to s3"
    files = request.files
    file = files.get('file')
    namespace = request.form.get('namespace')
    gesture = request.form.get('gesture')
    if file:
        timestr = time.strftime("%Y%m%d_%H%M%S")
        file.filename = f'{timestr}.webm'
        gm.upload_sample_file(file, namespace, gesture)

    response = jsonify("File received and saved!")
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


if __name__ == '__main__':
    app.run()
