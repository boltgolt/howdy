if meson.is_subproject()
project('howdy-gtk', license: 'MIT', version: 'beta', meson_version: '>= 0.64.0')
endif

datadir = get_option('prefix') / get_option('datadir') / 'howdy-gtk'
py_conf = configuration_data(paths_dict)
py_conf.set('data_dir', datadir)


py_paths = configure_file(
    input: 'src/paths.py.in',
    output: 'paths.py',
    configuration: py_conf,
)

sources = files(
    'src/authsticky.py',
    'src/i18n.py',
    'src/init.py',
    'src/onboarding.py',
    'src/paths_factory.py',
    'src/tab_models.py',
    'src/tab_video.py',
    'src/window.py',
)

py = import('python').find_installation(
    modules: ['gi', 'elevate']
)
py.dependency()

if get_option('install_in_site_packages')
    pysourcesinstalldir = join_paths(py.get_install_dir(), 'howdy-gtk')
else
    pysourcesinstalldir = get_option('py_sources_dir') != '' ? get_option('py_sources_dir') : join_paths(get_option('prefix'), get_option('libdir'), 'howdy-gtk')
endif

if get_option('install_in_site_packages')
    py.install_sources(
        sources,
        py_paths,
        subdir: 'howdy-gtk',
        install_mode: 'r--r--r--',
        install_tag: 'py_sources',
    )
else
    install_data(
        sources,
        py_paths,
        install_dir: pysourcesinstalldir,
        install_mode: 'r--r--r--',
        install_tag: 'py_sources',
    )
endif

logos = files(
    'src/logo.png',
    'src/logo_about.png',
)
install_data(logos, install_dir: datadir)

interface_files = files(
    'src/main.glade',
    'src/onboarding.glade',
)
install_data(interface_files, install_dir: datadir)

cli_path = join_paths(pysourcesinstalldir, 'init.py')
conf_data = configuration_data({ 'script_path': cli_path })

bin_name = 'howdy-gtk'
bin = configure_file(
    input: 'bin/howdy-gtk.in',
    output: bin_name,
    configuration: conf_data
)
install_data(
  bin,
  install_mode: 'rwxr-xr-x',
  install_dir: get_option('prefix') / get_option('bindir'),
  install_tag: 'bin',
)