"""Run the local app on the loopback interface."""
import os

import uvicorn
from .app import create_app


def main():
    port = int(os.environ.get('EAW_PORT', '8766'))
    uvicorn.run(create_app(),host='127.0.0.1',port=port,access_log=False,server_header=False)

if __name__=='__main__': main()
