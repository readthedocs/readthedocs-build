import re
import os
import sys
import codecs
from glob import glob
import logging
import zipfile
from importlib import import_module

from doc_builder.base import BaseBuilder
from doc_builder.utils import run, safe_write, obj_to_json, Capturing
from doc_builder import render
from doc_builder.constants import BuildException, TEMPLATE_DIR

import sphinx_rtd_theme

log = logging.getLogger(__name__)

PDF_RE = re.compile('Output written on (.*?)')

sphinx_application = import_module('sphinx.application')


# Monkeypatch this so we don't emit builder-inited signal twice.
def monkeypatch(self, buildername):
    builderclass = self.builderclasses[buildername]
    if isinstance(builderclass, tuple):
        # builtin builder
        mod, cls = builderclass
        builderclass = getattr(
            __import__('sphinx.builders.' + mod, None, None, [cls]), cls)
    self.builder = builderclass(self)

sphinx_application.Sphinx._init_builder = monkeypatch
sphinx_application.CONFIG_FILENAME = 'readthedocs-conf.py'


class BaseSphinx(BaseBuilder):

    """
    The parent for most sphinx builders.
    """

    def build(self, **kwargs):
        app = sphinx_application.Sphinx(
            srcdir=self.state.conf_dir,
            confdir=self.state.conf_dir,
            outdir=self.state.output_path,
            doctreedir=os.path.join(self.state.output_path, '.doctrees'),
            buildername='html',
        )
        app.rtd_state = self.state
        app.setup_extension('readthedocs_ext.readthedocs')
        app._init_builder(self.sphinx_builder)
        app.emit('builder-inited')

        app.config.init_values(app.warn)
        app._init_env(False)
        app.build(force_all=True)
        return True

    def _write_config(self):
        """
        Create ``conf.py`` if it doesn't exist.
        """
        docs_dir = self.docs_dir()
        conf_template = render.render_to_string('sphinx/conf.py.conf',
                                                project=self.state.project,
                                                version=self.state.version,
                                                template_dir=TEMPLATE_DIR,
                                                )
        conf_file = os.path.join(docs_dir, 'conf.py')
        safe_write(conf_file, conf_template)

    def append_conf(self, **kwargs):
        """Modify the given ``conf.py`` file from a whitelisted user's project.
        """

        # Pull config data
        try:
            self.state.conf_file
        except BuildException:
            self._write_config()
            # self.create_index(extension='rst')

        # # Open file for appending.
        json_file = codecs.open(self.state.rtd_json_file, encoding='utf-8', mode='w+')
        json_file.write(obj_to_json(self.state))
        json_file.close()

        outfile = codecs.open(self.state.rtd_conf_file, encoding='utf-8', mode='w+')
        rtd_string = render.render_to_string('doc_builder/conf.py.tmpl', state=self.state)
        outfile.write(rtd_string)
        outfile.close()

    def clean_conf(self):
        print "Cleaning written config files"
        os.remove(self.state.rtd_json_file)
        os.remove(self.state.rtd_conf_file)









        # rtd_ctx = Context({
            #'state': self.state,
            # 'versions': project.api_versions(),
            # 'downloads': self.version.get_downloads(pretty=True),
            # 'current_version': self.version.slug,
            # 'project': project,
            # 'settings': settings,
            # 'static_path': STATIC_DIR,
            # 'template_path': TEMPLATE_DIR,
            # 'conf_py_path': conf_py_path,
            # 'downloads': apiv2.version(self.version.pk).downloads.get()['downloads'],
            # 'api_host': getattr(settings, 'SLUMBER_API_HOST', 'https://readthedocs.org'),
            # GitHub
            # 'github_user': github_info[0],
            # 'github_repo': github_info[1],
            # 'github_version':  remote_version,
            # 'display_github': display_github,
            # BitBucket
            # 'bitbucket_user': bitbucket_info[0],
            # 'bitbucket_repo': bitbucket_info[1],
            # 'bitbucket_version':  remote_version,
            # 'display_bitbucket': display_bitbucket,
        # })

        # Avoid hitting database and API if using Docker build environment
        # if getattr(settings, 'DONT_HIT_API', False):
        #     rtd_ctx['versions'] = project.active_versions()
        #     rtd_ctx['downloads'] = self.version.get_downloads(pretty=True)
        # else:
        #     rtd_ctx['versions'] = project.api_versions()
        #     rtd_ctx['downloads'] = (apiv2.version(self.version.pk)
        #                             .downloads.get()['downloads'])

    # def __init__(self, *args, **kwargs):
    #     super(BaseSphinx, self).__init__(*args, **kwargs)
    #     try:
    #         self.old_artifact_path = os.path.join(self.state.fs.conf_dir, self.sphinx_build_dir)
    #     except BuildException:
    #         docs_dir = self.docs_dir()
    #         self.old_artifact_path = os.path.join(docs_dir, self.sphinx_build_dir)

    # def setup_config(self, app):
    #     app.config.templates_path.insert(0, self.state.TEMPLATE_PATH)
    #     app.config.html_static_path.append(self.state.STATIC_PATH)
    #     app.config.html_theme_path.append(self.state.TEMPLATE_PATH)

    #     # Add RTD Theme only if they aren't overriding it already
    #     using_rtd_theme = False

    #     if app.config.html_theme:
    #         if app.config.html_theme in ['default']:
    #             # Allow people to bail with a hack of having an html_style
    #             if not app.config.html_style:
    #                 app.config.html_theme = 'sphinx_rtd_theme'
    #                 using_rtd_theme = True
    #                 app.config.html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]
    #     else:
    #         app.config.html_theme = 'sphinx_rtd_theme'
    #         using_rtd_theme = True
    #         app.config.html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]

    #     state = self.state

    #     # Add project information to the template context.
    #     context = {
    #         'READTHEDOCS': True,

    #         'using_theme': using_rtd_theme,
    #         'html_theme': app.config.html_theme,
    #         'using_theme': (app.config.html_theme == "default"),
    #         'new_theme': (app.config.html_theme == "sphinx_rtd_theme"),
    #         'source_suffix': globals().get('source_suffix', '.rst'),

    #         'current_version': state.version,
    #         'MEDIA_URL': state.MEDIA_URL,
    #         'PRODUCTION_DOMAIN': state.PRODUCTION_DOMAIN,
    #         'versions': [],
    #         'downloads': [],
    #         'slug': state.version,
    #         'name': state.project,
    #         'rtd_language': state.language,
    #         'canonical_url': state.clean_canonical_url,
    #         'analytics_code': state.analytics_code,
    #         'single_version': state.single_version,
    #         'conf_py_path': state.conf_file,
    #         'api_host': state.API_HOST,
    #         'user_analytics_code': state.analytics_code or '',
    #         'global_analytics_code': state.analytics_code,
    #         'commit': state.commit,
    #     }

    #     for version in state.versions:
    #         context['versions'].append(
    #             (state.version, "/{language}/{slug}/".format(language=state.language, slug=state.version))
    #         )

    #     for key, val in state.downloads.items():
    #         context['downloads'].append(
    #             (key, val)
    #         )

    #     if self.state.display_github:
    #         context['github_user'] = state.vcs.username
    #         context['github_repo'] = state.vcs.repo
    #         context['github_version'] = state.vcs.branch
    #         context['display_github'] = state.vcs.display_github

    #     if self.state.display_bitbucket:
    #         context['bitbucket_user'] = state.vcs.username
    #         context['bitbucket_repo'] = state.vcs.repo
    #         context['bitbucket_version'] = state.vcs.branch
    #         context['display_bitbucket'] = state.vcs.display_bitbucket

    #     app.config.html_context.update(context)


class HtmlBuilder(BaseSphinx):
    type = 'sphinx'
    sphinx_build_dir = '_readthedocs_build/html'

    def __init__(self, *args, **kwargs):
        super(HtmlBuilder, self).__init__(*args, **kwargs)
        if self.state.allow_comments:
            self.sphinx_builder = 'readthedocs-comments'
        else:
            self.sphinx_builder = 'readthedocs'


class HtmlDirBuilder(HtmlBuilder):
    type = 'sphinx_htmldir'

    def __init__(self, *args, **kwargs):
        super(HtmlDirBuilder, self).__init__(*args, **kwargs)
        if self.version.project.allow_comments:
            self.sphinx_builder = 'readthedocsdirhtml-comments'
        else:
            self.sphinx_builder = 'readthedocsdirhtml'


class SingleHtmlBuilder(HtmlBuilder):
    type = 'sphinx_singlehtml'
    sphinx_builder = 'readthedocssinglehtml'


class SearchBuilder(BaseSphinx):
    type = 'sphinx_search'
    sphinx_builder = 'json'
    sphinx_build_dir = '_build/json'


class LocalMediaBuilder(BaseSphinx):
    type = 'sphinx_localmedia'
    sphinx_builder = 'readthedocssinglehtmllocalmedia'
    sphinx_build_dir = '_readthedocs_build/localmedia'

    def move(self, **kwargs):
        log.info("Creating zip file from %s" % self.old_artifact_path)
        target_file = os.path.join(self.target, '%s.zip' % self.state.project)
        if not os.path.exists(self.target):
            os.makedirs(self.target)
        if os.path.exists(target_file):
            os.remove(target_file)

        # Create a <slug>.zip file
        os.chdir(self.old_artifact_path)
        archive = zipfile.ZipFile(target_file, 'w')
        for root, subfolders, files in os.walk('.'):
            for file in files:
                to_write = os.path.join(root, file)
                archive.write(
                    filename=to_write,
                    arcname=os.path.join("%s-%s" % (self.state.project,
                                                    self.state.version),
                                         to_write)
                )
        archive.close()


class EpubBuilder(BaseSphinx):
    type = 'sphinx_epub'
    sphinx_builder = 'epub'
    sphinx_build_dir = '_readthedocs_build/epub'

    def move(self, **kwargs):
        from_globs = glob(os.path.join(self.old_artifact_path, "*.epub"))
        if not os.path.exists(self.target):
            os.makedirs(self.target)
        if from_globs:
            from_file = from_globs[0]
            to_file = os.path.join(self.target, "%s.epub" % self.state.project)
            run('mv -f %s %s' % (from_file, to_file))


class PdfBuilder(BaseSphinx):
    type = 'sphinx_pdf'
    sphinx_build_dir = '_readthedocs_build/latex'
    pdf_file_name = None

    def build(self, **kwargs):
        self.clean()
        os.chdir(self.state.conf_dir)
        # Default to this so we can return it always.
        results = {}
        latex_results = run('%s -b latex -D language=%s -d _build/doctrees . _build/latex'
                            % ('sphinx-build', self.state.language))

        if latex_results[0] == 0:
            os.chdir(self.sphinx_build_dir)
            tex_files = glob('*.tex')

            if tex_files:
                # Run LaTeX -> PDF conversions
                pdflatex_cmds = [('pdflatex -interaction=nonstopmode %s'
                                  % tex_file) for tex_file in tex_files]
                makeindex_cmds = [('makeindex -s python.ist %s.idx'
                                   % os.path.splitext(tex_file)[0]) for tex_file in tex_files]
                pdf_results = run(*pdflatex_cmds)
                ind_results = run(*makeindex_cmds)
                pdf_results = run(*pdflatex_cmds)
            else:
                pdf_results = (0, "No tex files found", "No tex files found")
                ind_results = (0, "No tex files found", "No tex files found")

            results = [
                latex_results[0] + ind_results[0] + pdf_results[0],
                latex_results[1] + ind_results[1] + pdf_results[1],
                latex_results[2] + ind_results[2] + pdf_results[2],
            ]
            pdf_match = PDF_RE.search(results[1])
            if pdf_match:
                self.pdf_file_name = pdf_match.group(1).strip()
        else:
            results = latex_results
        return results

    def move(self, **kwargs):
        if not os.path.exists(self.target):
            os.makedirs(self.target)

        exact = os.path.join(self.old_artifact_path, "%s.pdf" % self.state.project)
        exact_upper = os.path.join(self.old_artifact_path, "%s.pdf" % self.state.project.capitalize())

        if self.pdf_file_name and os.path.exists(self.pdf_file_name):
            from_file = self.pdf_file_name
        if os.path.exists(exact):
            from_file = exact
        elif os.path.exists(exact_upper):
            from_file = exact_upper
        else:
            from_globs = glob(os.path.join(self.old_artifact_path, "*.pdf"))
            if from_globs:
                from_file = from_globs[0]
            else:
                from_file = None
        if from_file:
            to_file = os.path.join(self.target, "%s.pdf" % self.state.project)
            run('mv -f %s %s' % (from_file, to_file))
