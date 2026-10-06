"""Developer quickstart for the TypeSafe SDK.

Configuration can be exported in the shell or placed in a local ``.env`` file.
"""

import os
from pathlib import Path

from typesafe_sdk import Choice, Noul, Score, TypeSafeAPIConnectionError, TypeSafeError, TypeSafeClient


def load_local_env() -> None:
    """Load missing environment variables from a simple local .env file.

    Shell environment variables take precedence, so deployment configuration is
    never overwritten. The project .env uses shell-style ``export KEY=value``
    lines, which this loader supports without another dependency.
    """
    env_file = Path(__file__).with_name(".env")
    if not env_file.is_file():
        return

    for raw_line in env_file.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line.removeprefix("export ").strip()
        if "=" not in line:
            continue

        key, value = line.split("=", maxsplit=1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def main() -> None:
    load_local_env()

    try:
        client = TypeSafeClient()
    except TypeSafeError as error:
        raise SystemExit(
            "Configuration error: set TYPESAFE_API_KEY in your shell or in .env. "
            f"Details: {error}"
        ) from error

    try:
        response = client.system_one(
            "Hi, my Stripe connection keeps failing with a 403 and we launch tomorrow.",
            {
                "department": Choice(
                    instructions="Which team should handle this",
                    criteria={
                        "billing": "Payment or subscription issues",
                        "technical": "Bugs or integration problems",
                        "sales": "Pricing or account questions",
                    },
                ),
                "frustration": Score(
                    instructions="How frustrated the customer appears",
                    criteria=[
                        "Calm, just stating facts",
                        "Frustrated but civil",
                        "Very angry, strong language",
                    ],
                ),
                "is_urgent": Noul(instructions="The message conveys urgency"),
            },
            model="openjev-latest",
        )
    except TypeSafeAPIConnectionError as error:
        raise SystemExit(
            "Could not reach the TypeSafe API. Check TYPESAFE_BASE_URL and your network connection. "
            f"Details: {error}"
        ) from error
    except TypeSafeError as error:
        raise SystemExit(f"TypeSafe API request failed: {error}") from error

    print(f"department: {response.choices['department'].choice}")
    print(f"frustration: {response.scores['frustration'].score}")
    print(f"is_urgent: {response.nouls['is_urgent'].noul}")


if __name__ == "__main__":
    main()
