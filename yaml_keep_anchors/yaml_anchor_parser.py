# encoding: utf-8
# yaml_anchor_parser - © 2016 NBS System - by Chloé Desoutter <chloe.desoutter@nbs-system.com>
"""yaml_anchor_parser: parse YAML keeping trace of anchors.

This YAML utils allow to parse YAML while keeping track of alias resolutions.
Since aliases contain useful meta-infos we want to expose them
For the moment we support only keeping anchor names on sequences and mappings.
If you need to solve other anchors feel free to extend. You just need to add
methods co AliasResolverYamlConstructor

Contribute at https://github.com/ChloeTigre/pyyaml-keep-anchors
"""

__author__ = 'Chloé Desoutter, NBS System <chloe.desoutter@nbs-system.com>'

from yaml.reader import *
from yaml.scanner import *
from yaml.parser import *
from yaml.composer import *
from yaml.resolver import *
from yaml.constructor import *
from yaml.nodes import *
from yaml.events import *
import collections


class anchorable_dict(dict):
    """A dict with has_anchor and anchor_name properties"""
    @property
    def has_anchor(self):
        return hasattr(self, '_anchor')

    @property
    def anchor_name(self):
        return getattr(self, '_anchor', None)

    @anchor_name.setter
    def anchor_name(self, value):
        self._anchor = value

    def __repr__(self):
        return "anchorable_dict({})".format(super().__repr__())


class anchorable_list(list):
    """A list with has_anchor and anchor_name properties"""
    @property
    def has_anchor(self):
        return hasattr(self, '_anchor')

    @property
    def anchor_name(self):
        return getattr(self, '_anchor', None)

    @anchor_name.setter
    def anchor_name(self, value):
        self._anchor = value

    def __repr__(self):
        return "anchorable_list({})".format(super().__repr__())


def build_proxy_from_base(base):
    global anchorable_types
    class Prox(type(base)):
        @property
        def has_anchor(self):
            return hasattr(self, '_anchor')

        @property
        def anchor_name(self):
            return getattr(self, '_anchor', None)

        @anchor_name.setter
        def anchor_name(self, value):
            self._anchor = value

        def __init__(self, wrapped):
            self._wrapped = wrapped

        def __getattr__(self, a):
            return getattr(self._wrapped, a)
    anchorable_types = tuple([a for a in anchorable_types] + [Prox])
    return Prox(base)


anchorable_types = (anchorable_dict, anchorable_list, )
"""tuple of all types with support for anchors.

Useful for if isinstance(my_field, anchorable_types):…"""


class AnchorKeeperComposer(Composer):
    def compose_node(self, parent, index):
        if self.check_event(AliasEvent):
            event = self.get_event()
            anchor = event.anchor
            if anchor not in self.anchors:
                raise ComposerError(None, None, "found undefined alias %r"
                                    % anchor, event.start_mark)
            # this is the only change from the canonical Composer
            setattr(self.anchors[anchor], 'anchor_name', anchor)
            return self.anchors[anchor]
        event = self.peek_event()
        anchor = event.anchor
        if anchor is not None:
            if anchor in self.anchors:
                raise ComposerError("found duplicate anchor %r; first occurence"
                                    % anchor, self.anchors[anchor].start_mark,
                                    "second occurence", event.start_mark)
        self.descend_resolver(parent, index)
        if self.check_event(ScalarEvent):
            node = self.compose_scalar_node(anchor)
        elif self.check_event(SequenceStartEvent):
            node = self.compose_sequence_node(anchor)
        elif self.check_event(MappingStartEvent):
            node = self.compose_mapping_node(anchor)
        self.ascend_resolver()
        return node



class AliasResolverYamlConstructor(BaseConstructor):
    """This keeps the aliases """
    def construct_object(self, node, deep=False):
        anchor_name = getattr(node, 'anchor_name', None)
        res = super(AliasResolverYamlConstructor, self).construct_object(node, deep)
        if anchor_name and isinstance(res, anchorable_types):
            res.anchor_name = anchor_name
        return res

    def construct_mapping(self, node, deep=False):
        if not isinstance(node, MappingNode):
            raise ConstructorError(None, None,
                                   "expected a mapping node, but found %s" % node.id,
                                   node.start_mark)
        mapping = anchorable_dict()
        for key_node, value_node in node.value:
            key = self.construct_object(key_node, deep=deep)
            if not isinstance(key, collections.Hashable):
                raise ConstructorError("while constructing a mapping", node.start_mark,
                                       "found unhashable key", key_node.start_mark)
            value = self.construct_object(value_node, deep=deep)
            mapping[key] = value
        return mapping

    def construct_sequence(self, node, deep=False):

        if not isinstance(node, SequenceNode):
            raise ConstructorError(None, None,
                                   "expected a sequence node, but found %s" % node.id,
                                   node.start_mark)
        res = anchorable_list(self.construct_object(child, deep=deep)
                               for child in node.value)

        return res

    def construct_scalar(self, node):
        if not isinstance(node, ScalarNode):
            raise ConstructorError(None, None,
                    "expected a scalar node, but found %s" % node.id,
                    node.start_mark)
        value = SafeConstructor().construct_object(node)
        # the following types currently dont work with build_proxy_from_base
        if node.tag in (
            'tag:yaml.org,2002:bool',
            'tag:yaml.org,2002:timestamp'
        ):
            return value
        return build_proxy_from_base(value)


class AliasResolverYamlLoader(Reader, Scanner, Parser, AnchorKeeperComposer, AliasResolverYamlConstructor, Resolver):
    """Loader that keeps track of the anchors populating them with types from anchorable_types"""
    def __init__(self, stream):
        Reader.__init__(self, stream)
        Scanner.__init__(self)
        Parser.__init__(self)
        AnchorKeeperComposer.__init__(self)
        AliasResolverYamlConstructor.__init__(self)
        Resolver.__init__(self)
__all__ = ('AliasResolverYamlLoader', 'anchorable_types')
