main.py                                 # entry point
launchpad/
  app.py                                # QApplication + controller
  config.py                             # user settings (future hotkey/startup go here)
  ui/                                   # window, search bar, result list, theme
  modes/                                # SearchMode ABC + ModeManager + AppsMode
  discovery/                            # Start Menu enumeration (Windows‑aware but isolated)
  platform_win/                         # pure Windows helpers: .lnk resolver, shell icons
  models/                               # ResultItem, Launcher
  workers/                              # QThread discovery, QThreadPool icon loading
tests/                                  # filtering, modes, shortcut errors, launcher




launchpad-app/
├── README.md
├── requirements.txt
├── main.py
├── launchpad/
│   ├── __init__.py
│   ├── app.py
│   ├── config.py
│   ├── ui/
│   │   ├── __init__.py
│   │   ├── window.py
│   │   ├── search_bar.py
│   │   ├── result_list.py
│   │   └── theme.py
│   ├── modes/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── manager.py
│   │   └── apps_mode.py
│   ├── discovery/
│   │   ├── __init__.py
│   │   └── start_menu.py
│   ├── platform_win/
│   │   ├── __init__.py
│   │   ├── lnk.py
│   │   └── shell.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── result.py
│   │   └── launcher.py
│   └── workers/
│       ├── __init__.py
│       ├── discovery_worker.py
│       └── icon_pool.py
└── tests/
    ├── __init__.py
    ├── conftest.py
    ├── test_filtering.py
    ├── test_modes.py
    ├── test_shortcuts.py
    └── test_launcher.py
