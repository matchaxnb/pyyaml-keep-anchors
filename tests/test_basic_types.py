import pytest
import yaml
import datetime
from yaml_keep_anchors.yaml_anchor_parser import AliasResolverYamlLoader


def load_yaml(yaml_string):
    return yaml.load(yaml_string, Loader=AliasResolverYamlLoader)


def test_anchor():
    result = load_yaml('''
        value-anchor: &anchor VALUE
        value-alias: *anchor
    ''')
    assert 'value-anchor' in result
    assert result['value-anchor'] == 'VALUE'
    assert result['value-anchor'].anchor_name == 'anchor'
    assert 'value-alias' in result
    assert result['value-alias'] == 'VALUE'
    assert result['value-alias'].anchor_name == 'anchor'


def test_alias_undefined_exception():
    with pytest.raises(yaml.composer.ComposerError, message="found undefined alias 'undefined-anchor'"):
        load_yaml('''
            undefined-value-alias: *undefined-anchor
        ''')


def test_anchorable_dict():
    result = load_yaml('''
        dict-anchor: &anchor
            key: VALUE
        dict-alias: *anchor
    ''')

    assert 'dict-anchor' in result
    assert result['dict-anchor'].anchor_name == 'anchor'
    assert 'dict-alias' in result
    assert 'key' in result['dict-alias']
    assert result['dict-alias']['key'] == 'VALUE'


def test_anchorable_list():
    result = load_yaml('''
        list-anchor: &anchor
          - one
          - two
          - three
        list-alias: *anchor
    ''')
    assert 'list-anchor' in result
    assert result['list-anchor'].anchor_name == 'anchor'
    assert result['list-anchor'] == ['one', 'two', 'three']
    assert 'list-alias' in result
    assert result['list-alias'].anchor_name == 'anchor'
    assert result['list-alias'] == ['one', 'two', 'three']


def test_basic_type_int():
    result = load_yaml('''
        int-positive: 1
        int-negative: -1
        int-anchor: &anchor 2
        int-alias: *anchor
    ''')
    assert 'int-positive' in result
    assert result['int-positive'] == 1
    assert 'int-negative' in result
    assert result['int-negative'] == -1
    assert 'int-anchor' in result
    assert result['int-anchor'].anchor_name == 'anchor'
    assert result['int-anchor'] == 2
    assert 'int-alias' in result
    assert result['int-alias'].anchor_name == 'anchor'
    assert result['int-alias'] == 2


def test_basic_type_float():
    result = load_yaml('''
        float-positive: 0.1
        float-negative: -0.1
    ''')
    assert 'float-positive' in result
    assert result['float-positive'] == 0.1
    assert 'float-negative' in result
    assert result['float-negative'] == -0.1


def test_basic_type_binary():
    result = load_yaml('''
        binary: !!binary "U09NRSBWQUxVRQ=="
        binary-multiline: !!binary "\
         U09NRSBMT05\
         HIE1VTFRJTE\
         lORSBWQUxVRQ=="

    ''')
    assert 'binary' in result
    assert result['binary'] == b'SOME VALUE'
    assert 'binary-multiline' in result
    assert result['binary-multiline'] == b'SOME LONG MULTILINE VALUE'


def test_basic_type_boolean():
    result = load_yaml('''
        boolean-true: true
        boolean-false: false
        boolean-anchor: &anchor true
        boolean-alias: *anchor
    ''')
    assert 'boolean-true' in result
    assert result['boolean-true'] is True
    assert 'boolean-false' in result
    assert result['boolean-false'] is False
    assert 'boolean-anchor' in result
    # TODO currently doesnt work
    #  assert result['boolean-anchor'].anchor_name == 'anchor'
    assert result['boolean-anchor'] is True
    assert 'boolean-alias' in result
    # TODO currently doesnt work
    #  assert result['boolean-alias'].anchor_name == 'anchor'
    assert result['boolean-alias'] is True


def test_basic_type_date():
    result = load_yaml('''
        date: &anchor 2019-03-13
        date-alias: *anchor
    ''')
    assert 'date' in result
    # TODO currently doesnt work
    #  assert result['date'].anchor_name == 'anchor'
    assert result['date'] == datetime.date(2019, 3, 13)
    assert 'date-alias' in result
    # TODO currently doesnt work
    #  assert result['date-alias'].anchor_name == 'anchor'
    assert result['date-alias'] == datetime.date(2019, 3, 13)


def test_basic_type_datetime():
    result = load_yaml('''
        datetime: &anchor 2018-01-02T12:30:45.0Z
        datetime-alias: *anchor
    ''')
    assert 'datetime' in result
    assert result['datetime'] == datetime.datetime(2018, 1, 2, 12, 30, 45, 0)
    assert 'datetime-alias' in result
    assert result['datetime-alias'] == datetime.datetime(2018, 1, 2, 12, 30, 45, 0)
