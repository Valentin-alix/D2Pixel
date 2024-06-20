import sys

from src.gui.app import Application, MainWindow
from src.gui.components.loaders import SplashScreen
from src.gui.signals.app_signals import AppSignals

if __name__ == "__main__":
    app_signals = AppSignals()
    app = Application(sys.argv)

    splash = SplashScreen()
    splash.show()

    main_window = MainWindow(app_signals=app_signals)

    splash.finish(main_window)

    sys.exit(app.exec_())
