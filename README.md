# Generating Dash docsets for third party rust crates

This repo contains a fork of a simple script for quickly generating Dash compatible docsets for third-party Rust crates. The original can be found [here.](https://github.com/cmyr/rust-dash-docset-gen)

## Changes

- Added default icon (Thanks to [Icons8](https://icons8.com))
- Added `--target` parameter for auto installing docsets
- Added dependency script

## Requirements

- python3
- the requests library
- Go >=1.4
- [dashing](https://github.com/technosophos/dashing)
- [rsdocs-dashing](https://github.com/hobofan/rsdocs-dashing)

## Usage

`./cargo-docsets.py serde crossbeam rand log regex`

This will clone the repos for these crates (assuming the name passed is used on [crates.io](https://crates.io),
generate the docsets, and copy them into the `docsets` subdir if the target parameter is not set. These `.docset` files can be added to Dash in
dash's preferences.
