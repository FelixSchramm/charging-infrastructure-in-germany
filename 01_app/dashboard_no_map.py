"""Entry-Point für das Streamlit-Cloud-Deployment.

Die eigentliche App liegt in ``app.py`` (zusammen mit ``config.py``,
``data_loading.py``, ``filters.py`` und ``sections/``). Diese Datei existiert
nur, weil der Main-File-Pfad in den Streamlit-Cloud-App-Settings auf
``01_app/dashboard_no_map.py`` zeigt und sich dort nicht nachträglich ändern
lässt. Sie führt schlicht ``app.py`` aus.

Lokal lieber direkt starten:  uv run streamlit run 01_app/app.py
"""

import runpy
from pathlib import Path

runpy.run_path(str(Path(__file__).with_name("app.py")), run_name="__main__")
