import argparse

from poller import Poller
from printer import Printer

class Main:
    """ Parse command line options and perform the download. """
    def __init__(self):
        self.parse_arguments()

    def parse_arguments(self):
        ''' parse arguments, which include '-p' for port '''
        parser = argparse.ArgumentParser(prog='Echo Server', description='A simple echo server that handles one client at a time', add_help=True)
        parser.add_argument('-p', '--port', type=int, action='store', help='port the server will bind to',default=3000)
        parser.add_argument("-d", "--debugMode", action="store_true",default=False, help="shows debuggin messages")
        self.args = parser.parse_args()

    def run(self):
        if(self.args.debugMode):
            Printer.debugging = True
        p = Poller(self.args.port)
        p.run()

if __name__ == "__main__":
    m = Main()
    m.parse_arguments()
    try:
        m.run()
    except KeyboardInterrupt:
        pass