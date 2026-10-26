"""A small, single-connection HTTP/HTTPS file downloader. Python 3.10+."""
import argparse
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener


class HttpRedirects(HTTPRedirectHandler):
    def redirect_request(self, request, fp, code, msg, headers, newurl):
        if urlsplit(newurl).scheme not in ("http", "https"):
            raise ValueError("Redirects must use HTTP or HTTPS")
        return super().redirect_request(request, fp, code, msg, headers, newurl)


def download(url: str, destination: Path) -> int:
    """Download to a new file; reject overwrites and remove incomplete transfers."""
    parsed = urlsplit(url)
    if parsed.scheme not in ("http", "https") or not parsed.hostname:
        raise ValueError("Use an HTTP or HTTPS URL")
    if destination.exists():
        raise FileExistsError(f"Destination already exists: {destination}")
    with build_opener(HttpRedirects()).open(Request(url, headers={"User-Agent": "DDM-Basic/1.0"}), timeout=30) as response:
        expected = response.headers.get("Content-Length")
        received = 0
        with destination.open("xb") as output:
            try:
                while chunk := response.read(64 * 1024):
                    output.write(chunk)
                    received += len(chunk)
                if expected is not None and received != int(expected):
                    raise OSError("The connection ended before the download was complete")
            except BaseException:
                # This block owns the file created with 'xb'; retain the original exception.
                output.close()
                destination.unlink()
                raise
    return received


def main() -> int:
    parser = argparse.ArgumentParser(description="Download one HTTP/HTTPS file using a single connection.")
    parser.add_argument("url")
    parser.add_argument("-o", "--output", type=Path, required=True, help="new output file path")
    args = parser.parse_args()
    try:
        size = download(args.url, args.output)
    except (ValueError, OSError, HTTPError, URLError) as error:
        parser.exit(1, f"Download failed: {error}\n")
    print(f"Saved {size} bytes to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
