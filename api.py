from fastapi import APIRouter, Request
from logger import logger
import subprocess
import json
import time
import os
from pydantic import BaseModel

api = APIRouter()

PATH_TO_JANUS = r'C:\path\to\janus' # gotta update this later
PROTOCOL_FILE_EXTENSION = '.mpt' # this is the file format that WinPREP protocols use

@api.get('/protocol-names')
def getProtocolNames():
    mpt_files = []
    for path, _, files in os.walk(PATH_TO_JANUS):
        for fname in files:
            if fname.lower().endswith(PROTOCOL_FILE_EXTENSION):
                fpath = os.path.join(path, fname)
                mpt_files.append(fpath)
    return mpt_files

@api.post('/run-protocol')
def postRunProtocol(protocol_name: str):
    command = f"{PATH_TO_JANUS} /r {protocol_name}"
    print("Running:", command)
    result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    msg = f"""Ran "{command}" with return code {result.returncode} and stdout {result.stdout}"""
    if result.returncode == 0:
        logger.info(msg)
        return msg, 200
    else:
        logger.error(msg)
        return msg, 500

@api.get('/parameters')
def getParameters():
    return ''

@api.patch('/parameters')
def updateParameters():
    return ''
