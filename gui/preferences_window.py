# gui/preferences_window.py

# Update imports
# Update imports
from utils.gui_utils import create_tooltip
from gui.audio_device_preview import AudioDevicePreview
from gui.log_level_updater import LogLevelUpdater
from config.config_manager import ConfigManager
from audio.audio_devices import get_input_devices
from utils.logging_utils import sanitize_message


logger = logging.getLogger(__name__)

class PreferencesWindow:
    def __init__(self, parent, config, on_save_callback, set_log_level_callback, correlation_id, trace_id):
        self.parent = parent
        self.config = config
        self.on_save_callback = on_save_callback
        self.set_log_level_callback = set_log_level_callback
        self.correlation_id = correlation_id
        self.trace_id = trace_id
        self.window = tk.Toplevel(parent)
        self.window.title("Preferences")
        self.window.geometry("600x700")
        self.window.resizable(False, False)
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)
        self.create_widgets()
        self.ensure_on_top()

    def ensure_on_top(self):
        self.window.transient(self.parent)
        self.window.grab_set()
        self.parent.wait_window(self.window)

    def create_widgets(self):
        notebook = ttk.Notebook(self.window)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)

        # Models Tab
        self.create_models_tab(notebook)

        # Key Listener Tab
        self.create_key_listener_tab(notebook)

        # GUI Preferences Tab
        self.create_gui_tab(notebook)

        # Logging Settings Tab
        self.create_logging_tab(notebook)

        # Audio Settings Tab
        self.create_audio_tab(notebook)

        # Save and Cancel Buttons
        self.create_buttons()

    # Define create_models_tab, create_key_listener_tab, create_gui_tab,
    # create_logging_tab, create_audio_tab, create_buttons methods here.
    # Each method handles the creation of widgets for its respective tab.

    def update_log_level(self):
        updater = LogLevelUpdater(self.log_level_var.get(), self.set_log_level_callback, self.correlation_id, self.trace_id)
        updater.update_log_level()

    def preview_audio_device(self):
        previewer = AudioDevicePreview(self.device_var.get(), self.input_devices, self.correlation_id, self.trace_id)
        previewer.preview_audio_device()

    def save_preferences(self):
        try:
            config_manager = ConfigManager(self.config)
            config_manager.update_preferences(
                model_var=self.model_var,
                noise_reduction_var=self.noise_reduction_var,
                key_combination_vars=self.key_combination_vars,
                key_listener_sleep_var=self.key_listener_sleep_var,
                always_on_top_var=self.always_on_top_var,
                gui_theme_var=self.gui_theme_var,
                log_level_var=self.log_level_var,
                device_var=self.device_var,
                input_devices=self.input_devices
            )
            self.on_save_callback()
            self.on_close()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def on_close(self):
        self.window.grab_release()
        self.window.destroy()
