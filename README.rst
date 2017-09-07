=======================
Lifeograph DB converter
=======================

Lifeograph diary database converter

Overview
========

Lifeograph diary database converter provides conversion between native lifeograph database formats
of different versions like v110 or v1040 plus generic formats like JSON, YAML or plain text.

Usage
=====

Converter is available as in-place script ``./convert.py`` or system-installed script ``lifeograph_db_converter`` of your choice.

.. code-block:: bash

    ./convert.py -sf my.diary -ff lifeog110 -tf json -p 1111

Arguments are:

- ``-h`` Show help message.
- ``-sf`` Source file. If not defined, stdin will be used.
- ``-df`` Destination file. If not defined, stdout will be used.
- ``-ff`` Source format. Can be ``lifeog110`` (native v110 format) or ``json``.
- ``-tf`` Destination format. Only ``json`` is currently supported.
- ``-p`` Password. Only for encrypted lifeograph native formats (src or dst).
