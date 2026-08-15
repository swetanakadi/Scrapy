# Email Scraper

## What it does

Scrapes email addresses from the career pages of websites provided through the command line.

The scraper supports two input modes:

- **Comma-separated URLs** passed directly as a string.
- **File path** pointing to a `.txt` file containing URLs, one per line. By default, `urls.txt` in the repository is used.

## Inspiration

To approach the right team building products or services that interest me.

## How to run

### 1. Docker

#### i. Build image

```bash
docker build -t <image_name> .
```

#### ii. Run container

```bash
docker run -it --env OUTPUT_FILE=emails.csv --name <container-name> <image-name>
```

#### iii. Copy CSV file to host

```bash
docker cp <container_name>:/app/emails.csv .
```

#### iv. Remove container

```bash
docker rm <container_name>
```

### 2. Locally

#### Installation

The local setup requires Python 3.12+, `uv`, and Playwright with its Chromium browser.

#### i. Clone the repository

```bash
git clone <repository-url>
cd <repository-directory>
```

#### ii. Verify Python

Check that Python 3.12 or newer is installed:

```bash
python3 --version
```

#### iii. Install `uv`

If `uv` is not already installed, install it using the official installation method for your operating system.

After installation, verify it:

```bash
uv --version
```

#### iv. Install project dependencies

The repository contains `pyproject.toml` and `uv.lock`. Install the locked dependencies with:

```bash
uv sync --frozen --no-dev
```

This creates the project's virtual environment under `.venv`.

#### v. Install Playwright browsers

Install the Playwright browser binaries required by the scraper:

```bash
uv run playwright install chromium
```

If Playwright reports missing system dependencies on Linux, install them with:

```bash
uv run playwright install --with-deps chromium
```

You can verify the Playwright installation with:

```bash
uv run python -c "from playwright.sync_api import sync_playwright; print('Playwright installed successfully')"
```

#### vi. Run the scraper locally

You can run the scraper through `uv` so that the project's `.venv` is automatically used:

```bash
uv run python scrapper.py -u 'https://xyz.com, https://example.com'
```

Or use a text file:

```bash
uv run python scrapper.py -f <your .txt file path>
```

If no file path is supplied, `urls.txt` in the repository is used by default.

If you prefer to activate the virtual environment first:

```bash
source .venv/bin/activate
python3 scrapper.py -u 'https://xyz.com, https://example.com'
```

For a file:

```bash
python3 scrapper.py -f urls.txt
```

#### vii. Output file

Application supports `OUTPUT_FILE` as an environment variable, you can configure the output filename locally:

```bash
OUTPUT_FILE=emails.csv uv run python scrapper.py -u 'https://xyz.com, https://example.com'
```

On Linux/macOS, you can also export it first:

```bash
export OUTPUT_FILE=emails.csv
uv run python scrapper.py -u 'https://xyz.com, https://example.com'
```

## Examples / Usage

### Local run

Scrape URLs supplied directly through the `-u` flag:

```bash
python3 scrapper.py -u 'https://xyz.com, https://example/com'
```

Scrape URLs from a text file:

```bash
python3 scrapper.py -f <your .txt file path>
```

By default, `urls.txt` will be picked if no file path is supplied.

When using `uv` without activating the virtual environment, use:

```bash
uv run python scrapper.py -u 'https://xyz.com, https://example.com'
```

or:

```bash
uv run python scrapper.py -f <your .txt file path>
```

### Docker run

To scrape URLs with the `-u` flag, update the `CMD` in the Dockerfile to:

```dockerfile
CMD ["/app/.venv/bin/python", "scrapper.py", "-u", "https://xyz.com, https://example.com"]
```

To scrape URLs with the `-f` flag, update the `CMD` if the file path is other than `urls.txt`:

```dockerfile
CMD ["/app/.venv/bin/python", "scrapper.py", "-f", "<your txt file path>"]
```

## Input file format

When using the `-f` option, provide a plain text file with one URL per line.

Example:

```text
https://xyz.com
https://example.com
```

Blank lines can be omitted.

## Output

The scraper generates a CSV file containing the emails discovered from the career pages.

For Docker execution, the output file is created inside the container under `/app`. Use `docker cp` to copy it to the host.

## Project structure

```text
.
├── src/
├── tests/
├── scrapper.py
├── urls.txt
├── pyproject.toml
├── uv.lock
├── Dockerfile
└── README.md
```

## Development

Run the test suite locally with:

```bash
uv run pytest
```

For coverage:

```bash
uv run pytest --cov
```

## Notes

- The scraper uses Playwright/Chromium for website navigation.
- For local Linux execution, Playwright may require system browser dependencies.
- Docker runs the application using the non-root application user configured in the Dockerfile.
- The Docker workflow described above intentionally uses `docker cp` to retrieve the generated CSV rather than mounting a host volume.
