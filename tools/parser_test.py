import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
    
import sys
from pprint import pprint
from tools.utils import load_parser


def main():

    if len(sys.argv) < 2:

        print(
            "Usage: python tools/parser_test.py parser_name"
        )

        return

    parser_name = sys.argv[1]

    parser = load_parser(
        parser_name
    )

    items = parser.parse()

    print()
    print(
        f"Items: {len(items)}"
    )

    print()

    for item in items[:5]:

        pprint(vars(item))
        print()


if __name__ == "__main__":
    main()
