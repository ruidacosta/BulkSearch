# BulkSearch
Search strings multiple files.

## Usage
```
$ ./BulkSearch.py -h

usage: BulkSearch.py [-h] [-v] [-l LOG] [-i INPUT_FILE | -p PATH] [-r] [-o OUTPUT] [-f {json,xml,txt}] string

Search a string (or regex string) inside multiple files.

positional arguments:
  string

optional arguments:
  -h, --help            show this help message and exit
  -v, --version         show version
  -l LOG, --log LOG     log execution to file. Default: No log file
  -i INPUT_FILE, --in INPUT_FILE
                        input file with paths to search for
  -p PATH, --path PATH  specify the path to search for
  -r, --recursive       using recursive search for folders
  -o OUTPUT, --output OUTPUT
                        save output into file. Default: stdout
  -f {json,xml,txt}, --format {json,xml,txt}
                        output format. One of the follow: json, xml or txt. Default: txt

```
