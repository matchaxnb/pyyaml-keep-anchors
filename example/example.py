#!/usr/bin/env python
# -*- encoding: utf-8
import yaml
from yaml_keep_anchors.yaml_anchor_parser import AliasResolverYamlLoader

with open('example/example.yaml', 'r') as fh:
    data = yaml.load(fh, Loader=AliasResolverYamlLoader)

assert data['key_three'].anchor_name == 'anchor'
assert data['key_two']['sub_key'].anchor_name == 'anchor_val'

print('key_one', data['key_one'].anchor_name)
print('key_two', data['key_two'].anchor_name)
print('key_two.sub_key', data['key_two']['sub_key'].anchor_name)
print('key_three', data['key_three'].anchor_name)

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
