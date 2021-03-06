from flask import Blueprint
from flask import flash
from flask import g
from flask import redirect
from flask import render_template, current_app
from flask import request
from flask import url_for
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

import os
import urllib.request
from flask import Flask
from werkzeug.utils import secure_filename

from .classes.dfClass import DF #file upload instance
from .classes.preProcessClass import PreProcess

import pandas as pd
import numpy as np

bp = Blueprint("preprocess", __name__, url_prefix="/pre")

ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'pkl'])

ROOT_PATH = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = ROOT_PATH + "\\upload\\"
ANNOTATION_TBL = UPLOAD_FOLDER + "AnnotationTbls\\GPL570-55999.csv"

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bp.route("/")
def index():
    print(current_app.config['APP_ALZ'].df)
    return render_template("preprocess/index.html", posts="")

@bp.route("/view")
def view():

    if(current_app.config['APP_ALZ'].df != ''):
        df = PreProcess.mergeDF(current_app.config['APP_ALZ'].df.path , ANNOTATION_TBL)
        # df = PreProcess.getDF(current_app.config['APP_ALZ'].df.path)
        current_app.config['APP_ALZ'].df.setMergeDF(df) #merge df

        return render_template("preprocess/tableView.html", tables=[df.head().to_html(classes='data')], titles=df.head().columns.values)

    else:
        return redirect('/pre')

@bp.route("/3")
def norm():
    x = current_app.config['APP_ALZ'].df
    if(x != ''):
        df = PreProcess.step3(x.merge_df)
        x.setSymbolDF(df)
        return render_template("preprocess/tableView.html", tables=[df.head().to_html(classes='data')], titles=df.head().columns.values)
    else:
        return redirect('/pre')

@bp.route("/probe2symbol")
def probe2symbol():
    x = current_app.config['APP_ALZ'].df
    if(x != ''):
        df = PreProcess.probe2Symbol(x.symbol_df)
        x.setAvgSymbolDF(df)
        return render_template("preprocess/tableView.html", tables=[df.head().to_html(classes='data')], titles=df.head().columns.values)
    else:
        return redirect('/pre')

@bp.route('/', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No file selected for uploading')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            anno_tbl = request.form["anno_tbl"]
            column_selection = request.form["column_selection"]
            filename = secure_filename(file.filename)
            df_obj = DF(os.path.join(UPLOAD_FOLDER, filename), anno_tbl, column_selection)
            current_app.config['APP_ALZ'].df = df_obj
            file.save(df_obj.path)
            flash('File successfully uploaded')
            return redirect('/pre/view')
        else:
            flash('Allowed file types are txt, pdf, png, jpg, jpeg, gif')
            return redirect(request.url)
