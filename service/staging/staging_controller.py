import os

from flask import Blueprint, jsonify, request, send_file, abort
import logging.config


staging_controller = Blueprint('staging', __name__)

staging_dir = os.environ['STAGING_DIR']

allowed_extensions = ['xml', 'pdf', 'tif', 'tiff', 'json']


def _list_dir(dir_path):
    tree = []
    for entry in os.scandir(dir_path):
        if entry.is_file():
            tree.append({
                "type": "file",
                "name": entry.name
            })
        else:
            tree.append({
                "type": "directory",
                "name": entry.name,
                "contents": _list_dir(os.path.join(dir_path, entry.name))
            })
    return tree


@staging_controller.route('', methods=['GET'], strict_slashes=False)
def list_staging():
    """
    List files and directories in the staging area.

    Returns a complete recursive folder hierarchy.

    :return: JSON array containing objects for files and folders
    """

    tree = _list_dir(staging_dir)
    return jsonify(tree)


@staging_controller.route(
    '/<path:path>',
    methods=['GET'],
    strict_slashes=False
)
def get_path(path):
    """
    Retrieve a file from the staging folder or lists the contents of a subfolder

    Returns HTTP status code 404 if file was not found

    Return A JSON array containing all file names, it it's a direcotry

    Returns the file's content if it's a file

    :param str path: path to file
    :return:
    """
    abs_path = os.path.join(staging_dir, path)
    if os.path.isdir(abs_path):
        return jsonify(os.listdir(abs_path))
    elif os.path.isfile(abs_path):
        return send_file(abs_path)
    else:
        abort(404)


@staging_controller.route('', methods=['POST'], strict_slashes=False)
def upload_to_staging():
    """
    Uploads files to the staging area.
    If the name of a posted file contains a directory-structure in it, represented structure will be created.
    The upload endpoint is able to handle single and multiple files provided
    under any key.
    Returns HTTP status code 400 if no files were provided.
    Returns HTTP status code 200 else

    :return: A JSON object with format : {"result": {uploaded_file_name: {"result":,"error": {"code":,"message":} } }

    """

    logging.getLogger(__name__).debug(f"Uploading {len(request.files)} files")
    results = {}

    if request.files:
        for key in request.files:
            for file in request.files.getlist(key):
                results[f"{file.filename}"] = {"success": True}
                if _is_allowed_file(file.filename):
                    try:
                        _upload_file(file)
                    except Exception as e:
                        results[f"{file.filename}"] = {"success": False,
                                                       "error":
                                                           {
                                                               "message": "An unknown error occurred.",
                                                               "code": "upload_failed"
                                                           }
                                                       }

                        logging.getLogger(__name__).debug(f"Error during upload from {file.filename} : {str(e)}")
                else:
                    results[f"{file.filename}"] = \
                        {"success": False,
                         "error": {"message": f"File extension .{_get_file_extension(file.filename)} is not allowed.",
                                   "code": "extension_not_allowed"
                                   }
                         }

                    logging.getLogger(__name__).debug(
                        f"Error during upload from {file.filename} : File extension ."
                        f"{_get_file_extension(file.filename)} is not allowed.")
        return jsonify({"result": results}), 200
    return "No files provided", 400


def _upload_file(file):
    path = os.path.join(staging_dir, file.filename)
    if not os.path.exists(os.path.dirname(path)):
        os.makedirs(os.path.dirname(path))
    file.save(path)


def _is_allowed_file(filename):
    return '.' in filename and \
           _get_file_extension(filename) in allowed_extensions


def _get_file_extension(filename):
    return filename.rsplit('.', 1)[1].lower()
