Data flow:
AppController starts a DiscoveryWorker (QThread) that enumerates Start Menu folders.
For each .lnk, platform_win.lnk.resolve_lnk returns target/args/cwd/icon location. Duplicates (same target+args) are dropped. Broken shortcuts are swallowed.
The worker emits AppEntry objects; the UI appends them progressively.
Icons are loaded off the UI thread via IconPool (QThreadPool) using SHGetFileInfo → QPixmap.fromWinHICON.
Typing in the search box calls ModeManager.current.search(query) → list[ResultItem]. The list widget re‑renders.
Enter → Launcher.launch(result) → QProcess.startDetached for executables, QDesktopServices for documents/URLs.
