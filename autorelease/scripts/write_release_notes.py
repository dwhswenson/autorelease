#!/usr/bin/env python
import argparse
from autorelease import ReleaseNoteWriter, AutoreleaseParsingHelper

def make_parser():
    parser = argparse.ArgumentParser()
    auto_parser = AutoreleaseParsingHelper(parser)
    auto_parser.add_github_parsing()
    auto_parser.add_project_parsing()
    auto_parser.parser.add_argument("--conf", type=str)
    auto_parser.parser.add_argument("-o", "--output", type=str)
    return auto_parser

def main():
    auto_parser = make_parser()
    auto_parser.parse_args()
    writer = ReleaseNoteWriter(config=auto_parser.opts.conf,
                               project=auto_parser.project,
                               github_user=auto_parser.github_user)
    writer.write_release_notes(outfile=auto_parser.opts.output)

if __name__ == "__main__":
    main()
