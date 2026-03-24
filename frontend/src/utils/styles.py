class Styles:
    @staticmethod
    def get_login_style(theme):
        return f"""
            QMainWindow {{
                background-color: {theme['bg_primary']};
            }}
            QLabel {{
                color: {theme['text_primary']};
            }}
            /* ... rest of the styles ... */
        """
    
    @staticmethod
    def get_main_window_style(theme):
        return f"""
            /* Main window styles */
        """ 