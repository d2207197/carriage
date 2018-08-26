import pytest
from carriage import Nothing, NothingAttrError, Optional, Some


def test_from_value_init():
    nothing = Optional.from_value(None)
    assert nothing is Nothing
    with pytest.raises(NothingAttrError):
        Nothing.value

    some = Optional.from_value(30)
    assert type(some) is Some
    assert some.value == 30

    some = Optional.from_value("hello")
    assert type(some) is Some
    assert some.value == "hello"

    adict = {'apple': 1, 'orange': 2}
    some = Optional.from_value(adict)
    assert type(some) is Some
    assert some.value == {'apple': 1, 'orange': 2}
    assert some.value is adict


def test_call_exceptable():
    def raise_exception():
        raise Exception
    assert Optional.from_call(raise_exception) is Nothing

    def raise_typeerror():
        raise TypeError
    assert Optional.from_call(raise_typeerror, TypeError) is Nothing

    with pytest.raises(TypeError):
        Optional.from_call(raise_typeerror, errors=ValueError)

    def identity(x):
        return x

    assert Optional.from_call(identity, 10).value == 10

    def raise_error(error):
        raise error

    with pytest.raises(TypeError):
        Optional.from_call(raise_error, TypeError, errors=ValueError)

    assert Optional.from_call(raise_error, AttributeError,
                              errors=AttributeError) is Nothing


def test_some_value():
    assert Some(30).value == 30
    assert Some(None).value is None
    assert Some(None).value is None
    assert Some([1, 2, 3]).value == [1, 2, 3]
    alist = [4, 5, 6]
    assert Some(alist).value is alist
    assert Some({'apple': 1, 'orange': 2}).value == {'apple': 1, 'orange': 2}
    adict = {'apple': 1, 'orange': 2}
    assert Some(adict).value is adict


def test_get_or():
    assert Some(30).get_or(None) == 30
    assert Some(None).get_or(None) is None
    assert Some(None).get_or(True) is None
    assert Some([1, 2, 3]).get_or(True) == [1, 2, 3]

    assert Nothing.get_or(0) == 0
    assert Nothing.get_or(None) is None
    assert Nothing.get_or(False) is False
    assert Nothing.get_or(True) is True
    assert Nothing.get_or("A string") == "A string"


def test_map():
    def multiply_2(n):
        return n * 2
    res = Some(100).map(multiply_2)
    assert res.value == 200

    res = Some(100).fmap(multiply_2)
    assert res.value == 200

    res = Nothing.map(multiply_2)
    assert res is Nothing

    res = Nothing.fmap(multiply_2)
    assert res is Nothing

    def append_1_no_return(alist):
        alist.append(1)

    res = Some([1, 2, 3]).map(append_1_no_return)
    assert res.value is None

    def append_1_return(alist):
        alist.append(1)
        return alist

    res = Some([1, 2, 3]).map(append_1_return)
    assert res.value == [1, 2, 3, 1]

    alist = [1, 2, 3]
    res = Some(alist).map(append_1_return)
    assert res.value is alist


def test_flat_map():
    def get_foo_option(adict):
        key = 'foo'
        if key in adict:
            return Some(adict[key])
        return Nothing

    foo_adict = {'foo': 'value of foo', 'bar': 'value of bar'}
    nofoo_adict = {'no_foo': 'value of foo', 'bar': 'value of bar'}

    res = Some(foo_adict).flat_map(get_foo_option)
    assert res.value == 'value of foo'

    res = Nothing.flat_map(get_foo_option)
    assert res is Nothing

    res = Some(nofoo_adict).flat_map(get_foo_option)
    assert res is Nothing

    res = (Some(nofoo_adict)
           .map(lambda d: d.get('foo'))
           .flat_map(Optional.from_value))
    assert res is Nothing

    res = (Some(nofoo_adict)
           .map(lambda d: Optional.from_value(d.get('foo')))
           .join())
    assert res is Nothing

    res = (Some(nofoo_adict)
           .map(lambda d: Optional.from_value(d.get('foo')))
           .flatten())
    assert res is Nothing

    res = (Some(nofoo_adict)
           .map(lambda d: d.get('foo'))
           .join_noneable())
    assert res is Nothing

    res = (Some(nofoo_adict)
           .map(lambda d: d.get('bar'))
           .join_noneable())
    assert res.value == 'value of bar'


def test_comparator():
    some_hello = Some("hello")
    some_hello_2 = Some("hello")
    some_world = Some("world")

    assert some_hello == some_hello_2
    with pytest.raises(TypeError):
        assert some_hello == "hello"

    assert some_hello != some_world
    with pytest.raises(TypeError):
        assert some_hello != "world"

    some_100 = Some(100)
    some_100_2 = Some(100)
    some_200 = Some(200)
    assert some_100 < some_200
    assert some_200 > some_100
    assert some_100.value < 200
    assert some_200.value > 100
    assert some_100 <= some_200
    assert some_200 >= some_100
    assert some_100 <= some_100_2
    assert some_100 >= some_100_2
    with pytest.raises(TypeError):
        assert some_200 < 100
    with pytest.raises(TypeError):
        assert some_200 > 100


class Person:
    def __init__(self, name, age, father=None, mother=None):
        self.name = name
        self.age = age
        self.father = father
        self.mother = mother

    def get_father(self):
        return self.father

    def get_mother(self):
        return self.mother

    def __repr__(self):
        return f'Person({self.name!r}, {self.father!r}, {self.mother!r})'

    def __eq__(self, other):
        return (self.name, self.father, self.mother) == (
            other.name, other.father, other.mother)


def test_pluck():
    d = {'a': 1, 'b': 2}

    assert Some(d).pluck('a') == Some(1)
    with pytest.raises(KeyError):
        Some(d).pluck('c')

    assert Some(d).pluck_opt('c') is Nothing
    johnny = Person('Johnny', 18)
    assert Some(johnny).pluck_attr('name') == Some('Johnny')


def test_value_do():

    papa = Person('Papa', 45)
    mama = Person('Mama', 40)
    johnny = Person('Johnny', 18, papa, mama)

    # assert Some(johnny).value_do.mother == Some(mama)
    # assert Some(johnny).value_do.mother.value is mama
    # assert Some(johnny).value_do.age == Some(18)
    # assert Some(johnny).value_do.age < Some(
    #     johnny).value_do.mother.value_do.age

    # assert maybe_obj.get_data().v == 30
    # assert maybe_obj.get_none().v is None
    # assert maybe_obj.get_none() == Some(None)
    # assert maybe_obj.get_none() is not Nothing
    # assert maybe_obj.fmap_one.get_none().v is None
    # assert maybe_obj.n.get_none() is Nothing
    # assert maybe_obj.get_none.n() is Nothing
    # assert maybe_obj.join()


def test_general():
    class TreeNode:
        def __init__(self, value, left=None, right=None):
            self.value = value
            self.left = left
            self.right = right

            return None

    class TreeNodeOpt:
        def __init__(self, name, left=Nothing, right=Nothing):
            self.name = name
            self.left = left
            self.right = right

    n = TreeNode(30)
    # get left left right left right value and times 2
    # or get 0

    result = 0
    if n.left is not None:
        if n.left.left is not None:
            if n.left.left.right is not None:
                if n.left.left.right.left is not None:
                    if n.left.left.right.left.right is not None:
                        result = n.left.left.right.left.right.value * 2

    assert result == 0

    n = TreeNodeOpt(30)
    result = (n.left
              .and_then(lambda n: n.left)
              .and_then(lambda n: n.right)
              .and_then(lambda n: n.left)
              .and_then(lambda n: n.right)
              .map(lambda n: n.value * 2)
              .get_or(0)
              )
    assert result == 0

    n = TreeNode(30)
    result = (Optional.from_value(n.left)
              .and_then(lambda n: n.left).join_noneable()
              .and_then(lambda n: n.right).join_noneable()
              .and_then(lambda n: n.left).join_noneable()
              .and_then(lambda n: n.right).join_noneable()
              .map(lambda n: n.value * 2)
              .get_or(0)
              )
    assert result == 0


def test_first_elem_is_odd():

    contacts = {
        'John Doe': {
            'phone': '0911-222-333',
            'address': {'city': 'hsinchu',
                        'street': '185 Somewhere St.'}},
        'Richard Roe': {
            'phone': '0933-444-555',
            'address': {'city': None,
                        'street': None}},
        'Mark Moe': {
            'address': None},
        'Larry Loe': None
    }

    def get_city(name):
        contact = contacts.get(name)
        if contact is not None:
            address = contact.get('address')
            if address is not None:
                city = address.get('city')
                if city is not None:
                    return f'City: {city}'

        return 'No city available'

    def getitem_opt(obj, key):
        try:
            return Some(obj[key])
        except (KeyError, TypeError) as e:
            return Nothing

    def get_city2(name):
        return (getitem_opt(contacts, name)
                .and_then(lambda contact: getitem_opt(contact, 'address'))
                .and_then(lambda address: getitem_opt(address, 'city'))
                .filter(lambda city: city is not None)
                .map(lambda city: f'City: {city}')
                .get_or('No city available')
                )

    assert get_city('John Doe') == 'City: hsinchu'
    assert get_city('Richard Roe') == 'No city available'
    assert get_city('Mark Moe') == 'No city available'
    assert get_city('Larray Loe') == 'No city available'

    assert get_city2('John Doe') == 'City: hsinchu'
    assert get_city2('Richard Roe') == 'No city available'
    assert get_city2('Mark Moe') == 'No city available'
    assert get_city2('Larray Loe') == 'No city available'
