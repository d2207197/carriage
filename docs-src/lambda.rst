``X, Xcall``: Elegant Lambda Function Builder
======================================================


.. role:: py(code)
   :language: python


:code:`getitem`
^^^^^^^^^^^^^^^

- :code:`X['key']` equals to :code:`lambda obj: obj['key']`

.. code:: python

   >>> from carriage import X, Stream
   >>> stm = Stream([{'first name': 'John', 'last name': 'Doe', 'height': 180},
   ...               {'first name': 'Richard', 'last name': 'Roe', 'height': 190}])
   >>> stm.map(X['first name']).to_list()
   ['John', 'Richard']

:code:`getattr`
^^^^^^^^^^^^^^^

- :code:`X.attr` equals to :code:`lambda obj: obj.attr`

.. code:: python

   >>> from carriage import X, Stream, Row
   >>> stm = Stream([Row(first_name='John', last_name='Doe', height=180),
   ...               Row(first_name='Richard', last_name='Roe', height=190)])
   >>> stm.map(X.last_name).to_list()
   ['Doe', 'Roe']
   
Comparison operators
^^^^^^^^^^^^^^^^^^^^

All comparison operators are supported: :code:`==`,  :code:`!=`,  :code:`>`,  :code:`<`, :code:`>=`,  :code:`<=`

- :code:`X > 3` equals to :code:`lambda _: _ > 3`
- :code:`'something' != X` equals to :code:`lambda _: 'something' != _`

.. code:: python

   >>> from carriage import X, Stream, Row
   >>> stm = Stream([Row(first_name='John', last_name='Doe', height=180),
   ...               Row(first_name='Richard', last_name='Roe', height=190),
   ...               Row(first_name='Jane', last_name='Doe', height=170)])
   >>> stm.filter(X.height >= 180).to_list()
   [Row(first_name='John', last_name='Doe', height=180),
    Row(first_name='Richard', last_name='Roe', height=190)]

   
Math operators
^^^^^^^^^^^^^^

All math and reflected math operators are supported: :code:`X + Y`,  :code:`X - Y`,  :code:`X * Y`,  :code:`X / Y`, :code:`X // Y`,  :code:`X % Y`, :code:`divmod(X, Y)`, :code:`X**Y`, :code:`pow(X, Y)`, :code:`abs(X)`, :code:`+X`, :code:`-X`


- :code:`X + 3` equals to :code:`lambda num: num + 3`
- :code:`5 // X` equals to :code:`lambda num: 5 // num`
- :code:`pow(2, X)` equals to :code:`lambda num: pow(2, num)`
- :code:`divmod(X, 3)` equals to :code:`lambda num: divmod(num, 2)`


.. code:: python

   >>> from carriage import X, Stream, Row
   >>> stm = Stream([Row(x=5, y=3),
   ...               Row(x=9, y=3),
   ...               Row(x=3, y=8)])
   >>> stm.map(X.x - X.y).to_list()
   [-2, 6, -5]
   
Method/Function calling
^^^^^^^^^^^^^^^^^^^^^^^

- :code:`X.startswith.call('https')` equals to :code:`lambda url: url.startswith('https')`

>>> stm = Stream(['Callum', 'Reuben', 'Taylor', 'Lucas', 'Charles', 'Kylan', 'Camren', 'Edison', 'Raul'])
>>> stm.filter(X.startswith.call('C')).to_list()
['Callum', 'Charles', 'Camren']


As function arguments
^^^^^^^^^^^^^^^^^^^^^

- :code:`Xcall(isinstance)(X, int)` equals to :code:`lambda obj: isinstance(obj, int)`

>>> import math
>>> from carriage import X, Stream, Row
>>> stm = Stream([Row(x=5, y=3),
...               Row(x=9, y=3),
...               Row(x=3, y=8)])
>>> stm.map(Xcall(math.sqrt)(X.x**2 + X.y**2)).to_list()
[5.830951894845301, 9.486832980505138, 8.54400374531753]


Multiple X
^^^^^^^^^^

- :code:`X.height + X.width` equals to :code:`lambda obj: obj.height + obj.width`



In collection
^^^^^^^^^^^^^

- :code:`X.in_((1,2))` equals to :code:`lambda elem: elem in (1, 2)`
- :code:`X.has(1)` equals to :code:`lambda coll: 1 in coll` 
