``carriage``: Less code, More productive
========================================

**carriage** aims to make your Python coding life easier. It includes a bunch of powerful collection classes with many practical methods you might use everyday. You can write your code faster, make your code more readable, and test your data pipeline more less painfully.

``carriage`` is a Python package `hosted on PyPI <https://pypi.org/project/carriage/>`_ and works only on Python 3.6 up.

Just like other Python package, install it by `pip <https://pip.pypa.io/en/stable/>`_ into a `virtualenv <https://hynek.me/articles/virtualenv-lives/>`_, or use  `poetry <https://poetry.eustace.io/>`_ to automatically create and manage the virtualenv.

.. code-block:: console

   $ pip install carriage

Getting Start
====================

All collection classes can be imported from the top level of this package.

.. code-block:: python

   from carriage import Row, Stream, StreamTable, X, Xcall, Map
   from carriage import Array, Optional, Some, Nothing

Row
---

:doc:`Row </row>` is a handy and more powerful `namedtuple <https://docs.python.org/3.6/library/collections.html#collections.namedtuple>`_. You can create arbitrary :doc:`Row </row>` anytime without declaring fields in advance.

   >>> row = Row(x=3, y=4)
   >>> row.x
   3
   >>> row2 = row.evolve(y=6, z=5)
   >>> row3 = row2.without('y')
   >>> row
   Row(x=3, y=4)
   >>> row2
   Row(x=3, y=6, z=5)
   >>> row3
   Row(x=3, z=5)

Stream
------

:doc:`Stream </stream>` is a very powerful wrapper type for any iterable object. You can write less code to transform, inspect, and manipulate any iterable. And with the property of lazy-evaluating, building and testing the pipeline for handling big, long sequential data are now faster, easier and painlessly.

   >>> Stream(range(5, 8)).map(X * 2).take(2).to_list()
   [10, 12]

StreamTable
-----------

:doc:`StreamTable </streamtable>` is a subclass of Stream but it assumes all elements are in Row type. This requirement allows StreamTable to provide a more refined interface.

   >>> stb = StreamTable.from_tuples(
   ...        [('joe', 170, 59), ('joy', 160, 54), ('may', 163, 55)],
   ...        fields=('name', 'height', 'weight'))
   >>> stb.show()
   | name   |   height |   weight |
   |--------+----------+----------|
   | joe    |      170 |       59 |
   | joy    |      160 |       54 |
   | may    |      163 |       55 |
   >>> stb_bmi = stb.select('name', bmi=X.weight / (X.height/100)**2)
   >>> stb_bmi.show()
   | name   |     bmi |
   |--------+---------|
   | joe    | 20.4152 |
   | joy    | 21.0937 |
   | may    | 20.7008 |
   >>> stb_bmi.where(X.bmi > 20.5).show()
   | name   |     bmi |
   |--------+---------|
   | joy    | 21.0937 |
   | may    | 20.7008 |

X, Xcall
--------
:doc:`X </lambda>` and :doc:`Xcall </lambda>` are function creators. Make your lambda function more readable and elegant. See examples above in Stream and StreamTable sections.

Map, Array
----------

:doc:`Map </map>` and :doc:`Array </array>` work just like Python primitive ``dict`` and ``list`` but enhanced with a lot of practical methods.

   >>> Map(joe=32, may=59, joy=31).remove('joy')
   Map({'joe': 32, 'may': 59})
   >>> Array([1, 2, 3, 4, 5]).filter(lambda n: n % 2 == 0)
   Array([2, 4])

Optional
--------

:doc:`Optional </optional>` is a object wrapper for handling errors. It makes ``None`` value, exceptions or other unexpected condition won't break your data processing pipeline.

Read the following API References for further information of each collection class.

API References
===============

.. toctree::
   :maxdepth: 2

   row
   stream
   streamtable
   lambda
   map
   array
   optional


To Do
==========

* A simple lambda function generating type.
* Multi-core processing.
* I/O methods for reading and writing to files.



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
