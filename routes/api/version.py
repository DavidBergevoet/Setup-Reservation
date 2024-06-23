from flask import jsonify
from handlers import version_handler

def version():
    git_hash = version_handler.retrieve_hash()
    return jsonify({"version": git_hash})