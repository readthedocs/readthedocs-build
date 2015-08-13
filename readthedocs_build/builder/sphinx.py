from .base import BaseBuilder


class SphinxBuilder(BaseBuilder):
    """
    TODO:

    - Build HTML in dirhtml format
    - Build HTML in singlehtml format + local media build
    - Build PDF
    - Build ePUB
    """

    python_dependencies = BaseBuilder.python_dependencies + (
        'Sphinx==1.3.1',
    )

    def _run_sphinx_build(self, format, out_dir):
        source_dir = self.get_source_directory()
        self.venv.python_run(
            'sphinx-build', [
                '-b',
                format,
                source_dir,
                out_dir,
            ])

    def build_html(self):
        out_dir = self.get_output_directory('html')
        self._run_sphinx_build('html', out_dir)

    def build_search_data(self):
        out_dir = self.get_output_directory('search_data')
        self._run_sphinx_build('json', out_dir)
