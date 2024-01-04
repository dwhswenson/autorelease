#!/usr/bin/env python
import argparse
import yaml
from autorelease import ReleaseNoteWriter, AutoreleaseParsingHelper
from autorelease.gh_api4.notes4 import NotesWriter, prs_since_latest_release

def make_parser():
    parser = argparse.ArgumentParser()
    auto_parser = AutoreleaseParsingHelper(parser)
    auto_parser.add_github_parsing()
    auto_parser.add_project_parsing()
    auto_parser.parser.add_argument("--conf", type=str)
    # auto_parser.parser.add_argument("-o", "--output", type=str)
    # auto_parser.parser.add_argument("--since-release", type=str)
    return auto_parser

def main():
    auto_parser = make_parser()
    opts = auto_parser.parse_args()
    with open(opts.conf, mode='r') as f:
        config = yaml.load(f.read(), Loader=yaml.SafeLoader)


    token = None
    if auto_parser.github_user is not None:
        token = auto_parser.github_user.token
    elif tok :

    notes_conf = config['notes']
    category_labels = {
        lab['label']: lab['heading'] for lab in notes_conf['labels']
    }
    topics = {}
    for label in notes_conf['labels']:
        if tops := label.get('topics'):
            topic_dict = {top['label']: top['name'] for top in tops}
            topics[label['label']] = topic_dict

    writer = NotesWriter(
        category_labels=category_labels,
        topics=topics,
        standard_contributors=notes_conf['standard_contributors']
    )
    import pdb; pdb.set_trace()

    new_prs = prs_since_latest_release(
        owner=config['project']['repo_owner'],
        repo=config['project']['repo_name'],
        auth=opts.github_user
    )
    print(writer_write(new_prs))

    writer = ReleaseNoteWriter(config=opts.conf,
                               since_release=opts.since_release,
                               project=opts.project,
                               github_user=opts.github_user)
    writer.write_release_notes(outfile=opts.output)

if __name__ == "__main__":
    main()
