from PyQt5.QtWidgets import QMainWindow
from pyqttoast import Toast, ToastPreset


def show_toast(
    parent: QMainWindow, text: str, preset: ToastPreset = ToastPreset.INFORMATION_DARK
):
    toast = Toast(parent)
    toast.setDuration(3000)
    toast.setText("  " + text)
    toast.applyPreset(preset)
    toast.setShowIcon(False)
    toast.show()
