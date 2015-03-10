import socket
from functools import wraps
import os
import logging
import shutil


from doc_builder.constants import LOG_TEMPLATE
from doc_builder import signals
from doc_builder.utils import run

from vcs_support.utils import NonBlockingLock


log = logging.getLogger(__name__)


def restoring_chdir(fn):
    # XXX:dc: This would be better off in a neutral module
    @wraps(fn)
    def decorator(*args, **kw):
        try:
            path = os.getcwd()
            return fn(*args, **kw)
        finally:
            os.chdir(path)
    return decorator


class BaseBuilder(object):

    """
    The Base for all Builders. Defines the API for subclasses.

    Expects subclasses to define ``old_artifact_path``,
    which points at the directory where artifacts should be copied from.
    """

    _force = False
    # old_artifact_path = ..

    def __init__(self, state):
        self.state = state
        self.target = self.state.fs.project.get_artifact_path(version=self.state.core.version, type=self.type)

    def run_build(self, force=False):
        """
        This handles the actual building of the documentation
        """

        from doc_builder.loader import loading as builder_loading
        from projects.tasks import move_files

        results = {}

        if signals.USE_SIGNALS:
            signals.before_build.send(sender=self.state)

        with NonBlockingLock(version=self.state.core.version, project=self.state.core.project, doc_path=self.state.fs.project.doc_path, max_lock_age=self.state.settings.REPO_LOCK_SECONDS):

            html_builder = builder_loading.get(self.state.core.documentation_type)(self.state)
            if force:
                html_builder.force()
            html_builder.append_conf()
            results['html'] = html_builder.build()
            if results['html'][0] == 0:
                html_builder.move()

            # Gracefully attempt to move files via task on web workers.
            try:
                move_files.delay(
                    state=self.state,
                    html=True,
                    hostname=socket.gethostname(),
                )
            except socket.error:
                pass

            fake_results = (999, "Project Skipped, Didn't build",
                            "Project Skipped, Didn't build")
            if 'mkdocs' in self.state.core.documentation_type:
                if 'search' in self.state.core.build_types:
                    try:
                        search_builder = builder_loading.get('mkdocs_json')(self.state)
                        results['search'] = search_builder.build()
                        if results['search'][0] == 0:
                            search_builder.move()
                    except:
                        log.error(LOG_TEMPLATE.format(
                            project=self.state.core.project, version=self.state.core.version, msg="JSON Build Error"), exc_info=True)

            if 'sphinx' in self.state.core.documentation_type:
                # Search builder. Creates JSON from docs and sends it to the
                # server.
                if 'search' in self.state.core.build_types:
                    try:
                        search_builder = builder_loading.get('sphinx_search')(self.state)
                        results['search'] = search_builder.build()
                        if results['search'][0] == 0:
                            # Copy json for safe keeping
                            search_builder.move()
                    except:
                        log.error(LOG_TEMPLATE.format(
                            project=self.state.core.project, version=self.state.core.version, msg="JSON Build Error"), exc_info=True)
                # Local media builder for singlepage HTML download archive
                if 'localmedia' in self.state.core.build_types:
                    try:
                        localmedia_builder = builder_loading.get('sphinx_singlehtmllocalmedia')(self.state)
                        results['localmedia'] = localmedia_builder.build()
                        if results['localmedia'][0] == 0:
                            localmedia_builder.move()
                    except:
                        log.error(LOG_TEMPLATE.format(
                            project=self.state.core.project, version=self.state.core.version, msg="Local Media HTML Build Error"), exc_info=True)

                # Optional build steps
                if self.state.core.name not in self.state.settings.HTML_ONLY:
                    if 'pdf' in self.state.core.build_types:
                        pdf_builder = builder_loading.get('sphinx_pdf')(self.state)
                        results['pdf'] = pdf_builder.build()
                        # Always move pdf results even when there's an error.
                        # if pdf_results[0] == 0:
                        pdf_builder.move()
                    else:
                        results['pdf'] = fake_results
                    if 'epub' in self.state.core.build_types:
                        epub_builder = builder_loading.get('sphinx_epub')(self.state)
                        results['epub'] = epub_builder.build()
                        if results['epub'][0] == 0:
                            epub_builder.move()
                    else:
                        results['epub'] = fake_results

        if signals.USE_SIGNALS:
            signals.after_build.send(sender=self.state)

        return results

    def setup_environment(self):
        """
        Build the virtualenv and install the project into it.
        """
        ret_dict = {}
        if self.state.core.virtualenv:
            # Clean up from possible old builds
            build_dir = os.path.join(self.state.fs.project.env_path, 'build')
            if os.path.exists(build_dir):
                log.info(LOG_TEMPLATE.format(project=self.state.core.project, version=self.state.core.version, msg='Removing existing build dir'))
                shutil.rmtree(build_dir)

            if self.state.core.system_packages:
                site_packages = '--system-site-packages'
            else:
                site_packages = '--no-site-packages'

            venv_cmd = 'virtualenv-2.7 -p %s' % self.state.core.interpreter
            ret_dict['env'] = run(
                '{cmd} {site_packages} {path}'.format(
                    cmd=venv_cmd,
                    site_packages=site_packages,
                    path=self.state.fs.project.env_path)
            )
            # Other code expects sphinx-build to be installed inside the
            # virtualenv.  Using the -I option makes sure it gets installed
            # even if it is already installed system-wide (and
            # --system-site-packages is used)
            if self.state.core.system_packages:
                ignore_option = '-I'
            else:
                ignore_option = ''
            ret_dict['sphinx'] = run(
                ('{cmd} install -U {ignore_option} '
                 'sphinx_rtd_theme sphinx==1.2.2 '
                 'virtualenv==1.9.1 docutils==0.11 '
                 'git+git://github.com/ericholscher/readthedocs-sphinx-ext#egg=readthedocs_ext').format(
                    cmd=self.state.fs.env_bin('pip'),
                    ignore_option=ignore_option))

            if self.state.core.requirements_file:
                os.chdir(self.state.fs.checkout_path)
                ret_dict['requirements'] = run(
                    '{cmd} install --exists-action=w -r {requirements}'.format(
                        cmd=self.state.fs.env_bin('pip'),
                        requirements=self.state.core.requirements_file))

            os.chdir(self.state.fs.checkout_path)
            if os.path.isfile("setup.py"):
                ret_dict['install'] = run(
                    '{cmd} setup.py install --force'.format(
                        cmd=self.state.fs.env_bin('python')))
        return ret_dict

    def force(self, **kwargs):
        """
        An optional step to force a build even when nothing has changed.
        """
        log.info("Forcing a build")
        self._force = True

    def build(self, id=None, **kwargs):
        """
        Do the actual building of the documentation.
        """
        raise NotImplementedError

    def move(self, **kwargs):
        """
        Move the documentation from it's generated place to its artifact directory.
        """
        if os.path.exists(self.old_artifact_path):
            if os.path.exists(self.target):
                shutil.rmtree(self.target)
            log.info("Copying %s on the local filesystem" % self.type)
            shutil.copytree(self.old_artifact_path, self.target)
        else:
            log.warning("Not moving docs, because the build dir is unknown.")

    def clean(self, **kwargs):
        """
        Clean the path where documentation will be built
        """
        if os.path.exists(self.old_artifact_path):
            shutil.rmtree(self.old_artifact_path)
            log.info("Removing old artifact path: %s" % self.old_artifact_path)

    def docs_dir(self, docs_dir=None, **kwargs):
        """
        Handle creating a custom docs_dir if it doesn't exist.
        """

        if not docs_dir:
            checkout_path = self.version.project.checkout_path(self.self.state.core.version)
            for possible_path in ['docs', 'doc', 'Doc', 'book']:
                if os.path.exists(os.path.join(checkout_path, '%s' % possible_path)):
                    docs_dir = possible_path
                    break

        if not docs_dir:
            # Fallback to defaulting to '.'
            docs_dir = '.'

        return docs_dir

    def create_index(self, extension='md', **kwargs):
        """
        Create an index file if it needs it.
        """

        docs_dir = self.docs_dir()

        index_filename = os.path.join(docs_dir, 'index.{ext}'.format(ext=extension))
        if not os.path.exists(index_filename):
            readme_filename = os.path.join(docs_dir, 'README.{ext}'.format(ext=extension))
            if os.path.exists(readme_filename):
                os.system('cp {readme} {index}'.format(index=index_filename, readme=readme_filename))
            else:
                index_file = open(index_filename, 'w+')
                index_text = """

Welcome to Read the Docs
------------------------

This is an autogenerated index file.

Please create a ``{dir}/index.{ext}`` or ``{dir}/README.{ext}`` file with your own content.

If you want to use another markup, choose a different builder in your settings.
                """

                index_file.write(index_text.format(dir=docs_dir, ext=extension))
                index_file.close()
