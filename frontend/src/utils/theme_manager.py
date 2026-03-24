from PyQt6.QtCore import QObject, pyqtSignal

class ThemeManager(QObject):
    theme_changed = pyqtSignal(bool)  # True for dark, False for light
    
    _dark_theme = {
        'bg_primary': '#1a1a1a',
        'bg_secondary': '#2d2d2d',
        'text_primary': '#ffffff',
        'text_secondary': '#b3b3b3',
        'accent': '#3498db',
        'accent_hover': '#2980b9',
        'card_bg': '#2d2d2d',
        'border': '#404040',
        'error': '#e74c3c',
        'success': '#2ecc71'
    }
    
    _light_theme = {
        'bg_primary': '#f5f6fa',
        'bg_secondary': '#ffffff',
        'text_primary': '#2c3e50',
        'text_secondary': '#7f8c8d',
        'accent': '#3498db',
        'accent_hover': '#2980b9',
        'card_bg': '#ffffff',
        'border': '#e0e0e0',
        'error': '#e74c3c',
        'success': '#2ecc71'
    }
    
    def __init__(self):
        super().__init__()
        self._is_dark = False
        self._current_theme = self._light_theme
    
    def toggle_theme(self):
        self._is_dark = not self._is_dark
        self._current_theme = self._dark_theme if self._is_dark else self._light_theme
        self.theme_changed.emit(self._is_dark)
    
    @property
    def current_theme(self):
        return self._current_theme
    
    @property
    def is_dark(self):
        return self._is_dark