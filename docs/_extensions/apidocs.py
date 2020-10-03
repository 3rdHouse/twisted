"""
Extension to trigger the pydoctor API builds as part of the Sphinx build.

This is created to have API docs created on Read the docs.
"""
import os
import sys
from io import StringIO

from sphinx.parsers import Parser
from sphinx.util import logging

from twisted.python._release import BuildAPIDocsScript


logger = logging.getLogger(__name__)


class PyDoctorParser(Parser):
   """
   Will transform the pydoctor instruction file.
   """
   supported = ('pydoctor',)

   def get_transforms(self):
      """
      """
      return []

   def parse(self, inputstring, document):
      """
      This is called when a pydoctor marker file is found.
      """
      source_path = document.attributes['source']

      # Let Sphinx know that the file should be ignored from the doctree.
      docname = self.app.env.path2doc(source_path)
      self.app.env.metadata[docname] = {'orphan': True}

      destination = os.path.join(self.app.outdir, os.path.dirname(docname))

      for line in inputstring.splitlines():
         line = line.strip()
         if not line:
            # Empty lines are ignored.
            continue

         if line.startswith('#'):
            # This is a comment and is ignored.
            continue

         # Stop as fist line and use it as source.
         source = os.path.abspath(os.path.join(
            os.path.dirname(source_path), line))
         break

      logger.info(
         'pydoctor API docs from %s to %s (this is a long process)...' % (
            source, destination))

      original_stdout = sys.stdout
      try:
         capture = StringIO()
         sys.stdout = capture
         BuildAPIDocsScript().main([source, destination])

         for line in capture.getvalue().splitlines():
            logger.warning(line)

      finally:
         sys.stdout = original_stdout

      logger.info('pydoctor API docs done.')


def setup(app):
   """
   This is called by Sphinx extension system.
   """
   app.add_source_suffix('.pydoctor', 'pydoctor')
   app.add_source_parser(PyDoctorParser)
