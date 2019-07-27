#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import requests
import os
import sys
import subprocess
import shutil
import tempfile

ASSETS_SUBDIR = "assets"
SOURCE_SUBDIR = "crates"
DOCSET_SUBDIR = "docsets"
CRATES_API = "https://crates.io/api/v1/crates/"


def gen_docset(crate_name, checkout_target):
    """generates or updates the docset for this crate."""

    repo = get_repo_url(crate_name)
    if repo is None:
        raise Exception("no repo returned for {}".format(crate_name))
    print("generating docs for {} from {}".format(crate_name, repo))
    local_path = repo.split('/')[-1]
    if not os.path.exists(local_path):
        clone_repo(repo)
    return update_docs(local_path, crate_name, checkout_target)


def get_repo_url(crate_name):
    """gets the url for the repository associated with `crate_name` on crates.io"""

    crates_path = "https://crates.io/api/v1/crates/" + crate_name
    headers = {'user-agent': '@cmyr\'s dash docset generation, colin@cmyr.net'}
    resp = requests.get(crates_path, headers=headers)
    if resp.status_code != 200:
        raise Exception("crates.io returned %d for %s" %
                        (resp.status_code, crate_name))
    json = resp.json()
    return json["crate"]["repository"]


def clone_repo(repo_path):
    subprocess.check_call("git clone {}".format(repo_path), shell=True)
    print("cloned {}".format(repo_path))


def update_docs(crate_dir, crate_name, checkout_target):
    os.chdir(crate_dir)
    try:
        subprocess.check_call("git diff-index --quiet HEAD --", shell=True)
    except subprocess.CalledProcessError:
        raise Exception(
            "crate {} has dirty working directory, will not update".format(crate_dir))

    subprocess.check_call(
        "git fetch && git checkout {}".format(checkout_target),
        stdout=sys.stdout, shell=True)
    print("updated {} to {}".format(crate_name, checkout_target))

    subprocess.check_call("cargo doc", shell=True, stdout=sys.stdout)

    if os.path.exists("docset"):
        shutil.rmtree("docset")

    subprocess.check_call(
        "rsdocs-dashing target/doc/{} docset".format(crate_name), stdout=sys.stdout, shell=True)
    subprocess.check_call("dashing build --config docset/dashing.json --source docset/build".format(
        crate_name), stdout=sys.stdout, shell=True)
    docset_path = os.path.join(os.getcwd(), "{}.docset".format(crate_name))
    return docset_path


def main():
    parser = argparse.ArgumentParser(
        description='create or update a dash docset')
    parser.add_argument('--target', type=str,
                        help='moves all dashsets into that directory')
    parser.add_argument(
        'crate_names',
        type=str,
        nargs='+',
        help='a list of crate names to generate or update docs for, use @ to specify a tag')

    args = parser.parse_args()
    if args.target is not None:
        target_dir = args.target
        base_dir = tempfile.gettempdir()
    else:
        target_dir = None
        base_dir = os.path.dirname(os.path.realpath(__file__))
    out_dir = os.path.join(base_dir, DOCSET_SUBDIR)
    source_dir = os.path.join(base_dir, SOURCE_SUBDIR)
    assets_dir = os.path.join(os.path.dirname(
        os.path.realpath(__file__)), ASSETS_SUBDIR)

    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    if not os.path.exists(source_dir):
        os.makedirs(source_dir)

    for crate in args.crate_names:
        os.chdir(source_dir)
        print("generating docs for", crate)
        try:
            words = crate.split('@', maxsplit=1)
            crate = words[0].replace('-', '_')
            checkout_target = "origin/master"
            if len(words) == 2:
                checkout_target = words[1]
            docset_path = gen_docset(crate, checkout_target)
            dest_path = os.path.join(out_dir, os.path.split(docset_path)[-1])
            assert dest_path.endswith(".docset")
            if os.path.exists(dest_path):
                shutil.rmtree(dest_path)
            shutil.move(docset_path, dest_path)
            shutil.copy(os.path.join(assets_dir, 'icon.png'),
                        os.path.join(dest_path, 'icon.png'))
            print("updated", dest_path)
            if target_dir is not None:
                target_path = os.path.join(
                    target_dir, os.path.split(docset_path)[-1])
                if os.path.exists(target_path):
                    shutil.rmtree(target_path)
                shutil.move(dest_path, target_path)
                print("installed {a} to {b}".format(
                    a=dest_path, b=target_path))

        except Exception:
            import traceback
            print(traceback.format_exc())


if __name__ == "__main__":
    main()
