import os
import json
import hashlib

MANIFEST_PATH = "data/manifest.json"


def create_manifest():

    os.makedirs("data", exist_ok=True)

    if not os.path.exists(MANIFEST_PATH):

        with open(MANIFEST_PATH, "w") as f:
            json.dump({}, f, indent=4)


def load_manifest():

    create_manifest()

    with open(MANIFEST_PATH, "r") as f:

        return json.load(f)


def save_manifest(data):

    with open(MANIFEST_PATH, "w") as f:

        json.dump(data, f, indent=4)


def file_hash(filepath):

    sha = hashlib.sha256()

    with open(filepath, "rb") as f:

        while True:

            chunk = f.read(8192)

            if not chunk:
                break

            sha.update(chunk)

    return sha.hexdigest()


def already_indexed(filepath):

    manifest = load_manifest()

    filename = os.path.basename(filepath)

    if filename not in manifest:

        return False

    return manifest[filename]["hash"] == file_hash(filepath)


def add_document(filepath, pages, chunks):

    manifest = load_manifest()

    filename = os.path.basename(filepath)

    manifest[filename] = {

        "hash": file_hash(filepath),

        "pages": pages,

        "chunks": chunks

    }

    save_manifest(manifest)