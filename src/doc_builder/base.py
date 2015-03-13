import sys
import socket
import os
import logging
import shutil

from sphinx.util.osutil import cd

from doc_builder.constants import LOG_TEMPLATE, BuildException
from doc_builder import signals
from doc_builder.utils import run

from vcs_support.utils import NonBlockingLock


log = logging.getLogger(__name__)


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

    def info(self, msg):
        log.info(
            LOG_TEMPLATE.format(
                project=self.state.project,
                version=self.state.version,
                msg=msg,
            )
        )

    def checkout_code(self):
        """
        Check out or update the given project's repository.
        """

        with NonBlockingLock(version=self.state.version, project=self.state.project, doc_path=self.state.root, max_lock_age=self.state.REPO_LOCK_SECONDS):

            if signals.USE_SIGNALS:
                signals.before_vcs.send(sender=self.state)

            # Get the actual code on disk
            self.info(
                msg='Checking out version {slug}: {identifier}'.format(
                    slug=self.state.project,
                    identifier=self.state.commit,
                )
            )
            with cd(self.state.root):
                version_repo = self.state.vcs_repo(self.state.project, self.state.root)
                checkout_ret = version_repo.checkout(
                    self.state.commit
                )

            if signals.USE_SIGNALS:
                signals.after_vcs.send(sender=self.state)

            # Update tags/version

            # version_post_data = {'repo': version_repo.repo_url}

            # if version_repo.supports_tags:
            #     version_post_data['tags'] = [
            #         {'identifier': v.identifier,
            #          'verbose_name': v.verbose_name,
            #          } for v in version_repo.tags
            #     ]

            # if version_repo.supports_branches:
            #     version_post_data['branches'] = [
            #         {'identifier': v.identifier,
            #          'verbose_name': v.verbose_name,
            #          } for v in version_repo.branches
            #     ]

            # try:
            #     apiv2.project(project.pk).sync_versions.post(version_post_data)
            # except Exception, e:
            #     print "Sync Versions Exception: %s" % e.message

        return checkout_ret

    def setup_environment(self):
        """
        Build the virtualenv and install the project into it.
        """
        ret_dict = {}
        print "Setting up env in " + self.state.env_path

        # Clean up from possible old builds
        build_dir = os.path.join(self.state.env_path, 'build')
        if os.path.exists(build_dir):
            log.info(LOG_TEMPLATE.format(project=self.state.project, version=self.state.version, msg='Removing existing build dir'))
            shutil.rmtree(build_dir)

        ret_dict['env'] = run(
            '{cmd} {path}'.format(
                cmd='virtualenv -p %s' % self.state.interpreter,
                path=self.state.env_path),
            stdout=sys.stdout,
            stderr=sys.stderr,
        )

        # Other code expects sphinx-build to be installed inside the
        # virtualenv.  Using the -I option makes sure it gets installed
        # even if it is already installed system-wide (and
        # --system-site-packages is used)
        if self.state.use_system_packages:
            ignore_option = '-I'
        else:
            ignore_option = ''

        ret_dict['sphinx'] = run(
            ('{cmd} install -U -I '
             'sphinx_rtd_theme sphinx==1.2.2 '
             'virtualenv==1.9.1 docutils==0.11 '
             'git+git://github.com/ericholscher/readthedocs-sphinx-ext#egg=readthedocs_ext').format(
                cmd=self.state.env_bin('pip'),),
            stdout=sys.stdout,
            stderr=sys.stderr,
        )

        requirements_file_path = self.state.requirements_file
        if not requirements_file_path:
            for path in [self.docs_dir(), '']:
                for req_file in ['pip_requirements.txt', 'requirements.txt']:
                    test_path = os.path.join(self.state.root, path, req_file)
                    print('Testing %s' % test_path)
                    if os.path.exists(test_path):
                        requirements_file_path = test_path
                        break

        if requirements_file_path:
            os.chdir(self.state.root)
            ret_dict['requirements'] = run(
                '{cmd} install --exists-action=w -r {requirements}'.format(
                    cmd=self.state.env_bin('pip'),
                    requirements=requirements_file_path),
                stdout=sys.stdout,
                stderr=sys.stderr,
            )

        os.chdir(self.state.root)
        if os.path.isfile("setup.py"):
            ret_dict['install'] = run(
                '{cmd} setup.py install --force'.format(
                    cmd=self.state.env_bin('python')
                ),
                stdout=sys.stdout,
                stderr=sys.stderr,
            )
        return ret_dict

    def run_build(self, force=False):
        """
        This handles the actual building of the documentation
        """

        from doc_builder.loader import loading as builder_loading
        from projects.tasks import move_files

        results = {}

        if signals.USE_SIGNALS:
            signals.before_build.send(sender=self.state)

        with NonBlockingLock(version=self.state.version, project=self.state.project, doc_path=self.state.root, max_lock_age=self.state.REPO_LOCK_SECONDS):

            html_builder = builder_loading.get(self.state.documentation_type)(self.state)
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
            if 'mkdocs' in self.state.documentation_type:
                if 'search' in self.state.build_types:
                    try:
                        search_builder = builder_loading.get('mkdocs_json')(self.state)
                        results['search'] = search_builder.build()
                        if results['search'][0] == 0:
                            search_builder.move()
                    except:
                        log.error(LOG_TEMPLATE.format(
                            project=self.state.project, version=self.state.version, msg="JSON Build Error"), exc_info=True)

            if 'sphinx' in self.state.documentation_type:
                # Search builder. Creates JSON from docs and sends it to the
                # server.
                if 'search' in self.state.build_types:
                    try:
                        search_builder = builder_loading.get('sphinx_search')(self.state)
                        results['search'] = search_builder.build()
                        if results['search'][0] == 0:
                            # Copy json for safe keeping
                            search_builder.move()
                    except:
                        log.error(LOG_TEMPLATE.format(
                            project=self.state.project, version=self.state.version, msg="JSON Build Error"), exc_info=True)
                # Local media builder for singlepage HTML download archive
                if 'localmedia' in self.state.build_types:
                    try:
                        localmedia_builder = builder_loading.get('sphinx_singlehtmllocalmedia')(self.state)
                        results['localmedia'] = localmedia_builder.build()
                        if results['localmedia'][0] == 0:
                            localmedia_builder.move()
                    except:
                        log.error(LOG_TEMPLATE.format(
                            project=self.state.project, version=self.state.version, msg="Local Media HTML Build Error"), exc_info=True)

                # Optional build steps
                if self.state.project not in self.state.HTML_ONLY:
                    if 'pdf' in self.state.build_types:
                        pdf_builder = builder_loading.get('sphinx_pdf')(self.state)
                        results['pdf'] = pdf_builder.build()
                        # Always move pdf results even when there's an error.
                        # if pdf_results[0] == 0:
                        pdf_builder.move()
                    else:
                        results['pdf'] = fake_results
                    if 'epub' in self.state.build_types:
                        epub_builder = builder_loading.get('sphinx_epub')(self.state)
                        results['epub'] = epub_builder.build()
                        if results['epub'][0] == 0:
                            epub_builder.move()
                    else:
                        results['epub'] = fake_results

        if signals.USE_SIGNALS:
            signals.after_build.send(sender=self.state)

        return results

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
            for possible_path in ['docs', 'doc', 'Doc', 'book']:
                if os.path.exists(os.path.join(self.state.root, '%s' % possible_path)):
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
