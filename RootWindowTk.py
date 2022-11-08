from tkinter import *
from BusinessTripWindow import BusinessTripWindow

class RootWindowTk(Tk):

    def __init__(self):
        super().__init__()

        self.title("Расчёт нерезиденства")
        self.eval('tk::PlaceWindow . center')

        # Create business trip button
        # On click -> Create new window for view and editing business trips
        self.go_to_bt_button = Button(self, text="Мои командировки")
        self.go_to_bt_button.bind('<Button-1>', self.go_to_bt_button_click)
        self.go_to_bt_button.pack()
    
    def go_to_bt_button_click(self, event):
        self.withdraw()
        BusinessTripWindow(self)
    