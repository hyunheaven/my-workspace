"""Run the local app on the loopback interface."""
import uvicorn
from .app import create_app


def main():
    uvicorn.run(create_app(),host='127.0.0.1',port=8765,access_log=False,server_header=False)

if __name__=='__main__': main()
