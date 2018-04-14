``carriage``: Less code, More productive
========================================

**carriage** aims at making your Python coding life easier by providing a bunch of collection classes. You can process data, write your code, test your code more fluently.

:doc:`Map </map>` and :doc:`Array </array>` work just like Python primitive ``dict`` and ``list`` 
but enhanced with a lot of practical methods.

:doc:`Row </row>` is a handy and more powerful `namedtuple <https://docs.python.org/3.6/library/collections.html>`_. You can create arbitrary :doc:`Row </row>` anytime without declaring fields in advance. It also provides some useful methods for transforming itself. 

:doc:`Stream </stream>` is a very powerful wrapper for any iterable object. You can transform, inspect, manipulate an iterable much easier. And with the property of lazy-evaluating, building and testing the pipeline for handling big, long data are faster and easier.

:doc:`Optional </optional>` is a object wrapper for handling errors. It makes ``None`` value, exceptions or other unexpected condition won't break your data processing pipeline.

Getting Start
====================

``carriage`` is a Python package `hosted on PyPI <https://pypi.org/project/carriage/>`_ and works only on Python 3.6 up.

Just like other Python package, install it by `pip <https://pip.pypa.io/en/stable/>`_ into a `virtualenv <https://hynek.me/articles/virtualenv-lives/>`_, or use `pipenev <https://docs.pipenv.org/>`_ to automatically create and manage the virtualenv.

.. code-block:: console

   $ pip install carriage



All collection classes can be imported from the top level of this package.

.. doctest::

   >>> from carriage import Row, Map, Stream, Array, Optional, Some, Nothing
   >>> Row(x=3, y=4).evolve(z=5)
   Row(x=3, y=4, z=5)
   >>> Map(joe=32, may=59, joy=31).remove('joy')
   Map({'joe': 32, 'may': 59)
   >>> Array([1, 2, 3, 4, 5]).filter(lambda n: n % 2 == 0)
   Array([2, 4])
   >>> Stream(range(5, 8)).map(lambda n: n * 2).take(2).to_list()
   [10, 12]

Read the following API References for further information of each collection class.

API References
===============

.. toctree::
   :maxdepth: 2

   row
   map
   stream
   array
   optional
   
   




Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
