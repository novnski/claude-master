from textual.app import App
from textual.widgets import Static

class ClaudeDashboard(App):
    def on_mount(self):
        self.mount(Static("Claude Master Dashboard - Coming Soon"))

def main():
    app = ClaudeDashboard()
    app.run()

if __name__ == "__main__":
    main()
