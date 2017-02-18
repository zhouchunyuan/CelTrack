from CelTrackLib import Capframe,TrkPanel,App,DoCapture,DoMacro
import thread
import sys
    
def main():
    thread.start_new_thread(DoMacro,())
    thread.start_new_thread(DoCapture,())

    app = App(sys.argv)
    app.run()

if __name__ == '__main__':
    main()

