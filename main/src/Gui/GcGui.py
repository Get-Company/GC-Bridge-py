import PySimpleGUI as sg


class GcGui:
    def __init__(self):
        # Vars to set
        self.title = 'GC'
        self.margins = (0,0)

        # Template
        self.layout = []
        self.cols = []
        self.theme = None

        # The window
        self.framework = None
        self.window = None
        self.layout = None

        # Functions to call
        self.set_framework(sg)  # First call necessary
        self.set_theme()  # Standard Dark. Themes https://media.geeksforgeeks.org/wp-content/uploads/20200511200254/f19.jpg

    ####
    # Framework, Window etc.
    def set_framework(self, framework: sg):
        self.framework = framework

    def get_framwork(self):
        return self.framework

    def set_window(self):
        self.window = self.get_framwork().Window(
            title=self.get_title(),
            layout=self.get_layout(),
            margins=self.get_margins()
        )
        return True

    def get_window(self):
        return self.window

    def create_window(self):
        self.set_window()
        return self.window.read()

    ####
    # Setup the window
    def set_theme(self, theme="Dark"):
        self.theme = theme
        sg.theme(theme)

    def get_theme(self):
        return self.theme

    def set_title(self, title):
        self.title = title

    def get_title(self):
        return self.title

    def set_margins(self, margins):
        self.margins = margins

    def get_margins(self):
        return self.margins


    def is_closed(self):
        return self.get_framwork().WIN_CLOSED

    def do_close(self):
        self.get_window().close()
        return True

    ####
    # Setup the layout/elements
    def set_layout(self, layout):
        self.layout = layout

    def get_layout(self):
        return self.layout

    def add_to_layout(self, layout_object):
        current_layout = self.get_layout()
        current_layout.append(layout_object)
        self.set_layout(current_layout)

    def add_button(self, text, key):
        button = [self.get_framwork().Button(text, key=key)]
        try:
            self.add_to_layout(button)
            return True
        except:
            return False

    def add_text(self, text, key):
        text_element = [self.get_framwork().Text(text, key=key)]
        try:
            self.add_to_layout(text_element)
            return True
        except:
            return False

    def add_input(self, text, value, key, size=(15, 1)):
        input_element = self.get_framwork().InputText(value, key=key)
        form_field = [self.get_framwork().Text(text, size), input_element]
        self.add_to_layout(form_field)
