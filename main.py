from __future__ import annotations

import sys

from launchpad.app import LaunchpadApp


def main() -> int:
    app = LaunchpadApp(sys.argv)
    return app.run()


if __name__ == "__main__":
    raise SystemExit(main())
