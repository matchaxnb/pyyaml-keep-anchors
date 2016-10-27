# pyyaml-keep-anchors
Keep anchor references when parsing yaml files

# Purpose

This YAML utils allow to parse YAML while keeping track of alias resolutions.
Since aliases contain useful meta-infos we want to expose them
For the moment we support only keeping anchor names on sequences and mappings.
If you need to solve other anchors feel free to extend. You just need to add
methods co AliasResolverYamlConstructor

Contribute at https://github.com/ChloeTigre/pyyaml-keep-anchors

# Example

python -m example.example # :-)
