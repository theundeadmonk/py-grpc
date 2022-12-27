import argparse
import os
import shutil
import subprocess
import sys

from distutils.spawn import find_executable

PROTO_FILES_PATH = "./protobufs"
PROTOC_GEN_PATH = "./types"

if "PROTOC" in os.environ and os.path.exists(os.environ["PROTOC"]):
    protoc = os.environ["PROTOC"]
else:
    protoc = find_executable("protoc")


def build() -> None:
    _no_proto_files_check(PROTO_FILES_PATH)
    proto_files = ",".join(
        [
            f
            for f in os.listdir(PROTO_FILES_PATH)
            if os.path.isfile(os.path.join(PROTO_FILES_PATH, f))
        ]
    )

    if os.path.exists(PROTOC_GEN_PATH):
        _empty_directory(PROTOC_GEN_PATH)
    else:
        _create_directory(PROTOC_GEN_PATH)

    protoc_command = [
        "python",
        "-m",
        "grpc_tools.protoc",
        f"--proto_path={PROTO_FILES_PATH}",
        f"--python_out={PROTOC_GEN_PATH}",
        f"--mypy_out={PROTOC_GEN_PATH}",
        f"--grpc_python_out={PROTOC_GEN_PATH}",
        f"--mypy_grpc_out={PROTOC_GEN_PATH}",
        "--fatal_warnings",
        proto_files,
    ]
    if subprocess.call(protoc_command) != 0:
        sys.exit(1)


def _create_directory(dirname) -> None:
    if not os.path.exists(dirname):
        os.makedirs(dirname)


def _no_proto_files_check(dirname) -> None:
    dir = os.listdir(dirname)

    if len(dir) == 0:
        sys.exit("Error: No Proto files present.")


def _empty_directory(folder) -> None:
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if filename == "__init__.py":
                next
            elif os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print("Failed to delete %s. Reason: %s" % (file_path, e))
