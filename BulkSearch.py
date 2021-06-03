#!/usr/bin/python
# -*- coding: utf-8 -*-

import argparse
import json
import logging
import os
import os.path
import re
import sys
import time
import xml.etree.ElementTree as XML
from datetime import datetime

__version__ = '0.1'


def process_arguments():
    parser = argparse.ArgumentParser(description='Search a string (or regex string) inside multiple files.')
    parser.add_argument('-v', '--version', action='version', version='%(prog)s ' + __version__, help='show version')
    parser.add_argument('-l', '--log', action='store', dest='log', help='log execution to file. Default: No log file')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-i', '--in', action='store', dest='input_file', type=check_path,
                       help='input file with paths to search for')
    group.add_argument('-p', '--path', action='store', dest='path', type=check_path,
                       help='specify the path to search for')
    parser.add_argument('-r', '--recursive', action='store_true', dest='recursive',
                        help='using recursive search for folders')
    parser.add_argument('-o', '--output', action='store', dest='output',
                        help='save output into file. Default: stdout')
    parser.add_argument('-f', '--format', action='store', dest='format', choices=['json', 'xml', 'txt'], default='txt',
                        help='output format. One of the follow: json, xml or txt. Default: txt')
    parser.add_argument('string', nargs=1, action='store')
    args = parser.parse_args()
    return vars(args)


def check_path(value: str) -> str:
    if os.path.exists(os.path.abspath(value)):
        return value
    else:
        raise Exception(f"{value} doesn't exist")


def logging_init(log_name: str):
    date = datetime.now()
    date_string = date.strftime('%Y%m%d')
    name, ext = os.path.splitext(log_name)
    filename = f'{name}_{date_string}{ext}'
    logging.basicConfig(
        filename=filename,
        format='%(asctime)s.%(msecs)d[%(levelname)s]::%(message)s',
        datefmt='%d-%m-%Y %H:%M:%S',
        level=logging.INFO)


def get_all_files(path: str, recursive: bool = True) -> list[str]:
    path_abs = os.path.abspath(path)
    result: list[str] = []
    paths = []
    if os.path.isfile(path_abs):
        # read input file
        if os.path.exists(path_abs):
            with open(path_abs, 'r') as fd:
                for line in fd:
                    paths += os.path.abspath(line)
    else:
        paths = [os.path.abspath(path)]

    if recursive:
        for path_to_search in paths:
            for root, dirs, files in os.walk(path_to_search):
                for file in files:
                    temp_file = root + os.sep + file
                    result.append(os.path.abspath(temp_file))
    else:
        for path_to_search in paths:
            for item in os.listdir(path_to_search):
                abs_item = path_to_search + os.sep + item
                if os.path.isfile(abs_item):
                    result.append(abs_item)
    return result


def search_on_file(file_abs: str, string: str) -> list[tuple[int, str]]:
    result: list[tuple[int, str]] = []
    line_counter = 0
    with open(file_abs, 'r') as fd:
        try:
            for line in fd:
                line_counter += 1
                if re.search(string, line):
                    result.append((line_counter, line))
        except UnicodeDecodeError as ex:
            logging.info('UnicodeDecodeError on file ' + file_abs + '('+str(ex.reason)+')')
    return result


def process_search(args: dict[str, str]) -> dict[str, list[tuple[int, str]]]:
    result: dict[str, list[tuple[int, str]]] = {}
    if args['input_file'] is not None:
        # process using input_file
        files = get_all_files(args['input_file'], bool(args['recursive']))
    elif args['path'] is not None:
        # process using the path
        files = get_all_files(args['path'], bool(args['recursive']))
    else:
        # process using current folder
        files = get_all_files(os.path.abspath('.'), bool(args['recursive']))
    # print(files)
    for file in files:
        temp = search_on_file(file, args['string'])
        if temp:
            result[file] = search_on_file(file, args['string'])
    return result


def process_output(data: dict[str, list[tuple[int, str]]], output: str, output_format: str, string: str):
    if output_format == 'txt':
        msg = output_to_txt(data)
    elif output_format == 'xml':
        msg = output_to_xml(data, string)
    elif output_format == 'json':
        msg = output_to_json(data, string)
    else:
        msg = None

    if msg is None:
        sys.stderr.write(f'No output was generated.')

    if output is None:
        # write to stdout
        print(msg)
    else:
        # write to file
        with open(output, 'w') as fd:
            fd.write(msg)


def output_to_txt(data: dict[str, list[tuple[int, str]]]) -> str:
    msg = ''
    for file, matchs in data.items():
        msg += f'{file}\n'
        for line_count, line_str in matchs:
            msg += f'Line {line_count}: {line_str}\n'
        msg += '\n'
    return msg


def output_to_xml(data: dict[str, list[tuple[int, str]]], string: str) -> str:
    root = XML.Element('search')
    string_node = XML.SubElement(root, 'string')
    string_node.text = string
    files = XML.SubElement(root, 'files')
    for file, matchs in data.items():
        file_node = XML.SubElement(files, 'file')
        name = XML.SubElement(file_node, 'name')
        name.text = file
        matchs_node = XML.SubElement(files, 'matchs')
        for line_count, line_string in matchs:
            match = XML.SubElement(matchs_node, 'match')
            line_count_node = XML.SubElement(match, 'line_number')
            line_count_node.text = str(line_count)
            line_string_node = XML.SubElement(match, 'line_string')
            line_string_node.text = line_string
    return XML.tostring(root).decode("utf-8")


def output_to_json(data: dict[str, list[tuple[int, str]]], string: str) -> str:
    data_fix = {'string': string, 'data': data}
    return json.dumps(data_fix)


def main():
    start_time = time.time()
    args = process_arguments()
    args['string'] = args['string'][0]
    # print(args)
    if args['log'] is not None:
        logging_init(args['log'])

    logging.info('Starting...')
    result = process_search(args)
    process_output(result, args['output'], args['format'], args['string'])
    logging.info('Done')
    logging.info(f'Execution time: {(time.time() - start_time):.2f} seconds')


if __name__ == '__main__':
    main()
