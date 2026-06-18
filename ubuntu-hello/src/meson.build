if meson.is_subproject()
project('ubuntu-hello', 'cpp', license: 'MIT', version: '1.0.2', meson_version: '>= 0.64.0')
endif


datadir = get_option('prefix') / get_option('datadir') / 'ubuntu-hello'
py_conf = configuration_data(paths_dict)
py_conf.set('data_dir', datadir)

py = import('python').find_installation(paths_dict.get('python_path'))
py.dependency()

py_paths = configure_file(
    input: 'paths.py.in',
    output: 'paths.py',
    configuration: py_conf,
)

py_sources = [
    'cli/__init__.py',
    'cli/add.py',
    'cli/clear.py',
    'cli/config.py',
    'cli/disable.py',
    'cli/keyring.py',
    'cli/list.py',
    'cli/remove.py',
    'cli/set.py',
    'cli/snap.py',
    'cli/test.py',
    'cli.py',
    'compare.py',
    'i18n.py',
    'paths_factory.py',
    'recorders/__init__.py',
    'recorders/ffmpeg_reader.py',
    'recorders/pyv4l2_reader.py',
    'recorders/v4l2.py',
    'recorders/video_capture.py',
    'rubberstamps/__init__.py',
    'rubberstamps/hotkey.py',
    'rubberstamps/nod.py',
    'snapshot.py',
    py_paths,
]

# Include PAM module
if get_option('install_in_site_packages')
    pysourcesinstalldir = join_paths(py.get_install_dir(), 'ubuntu-hello')
else  
    pysourcesinstalldir = get_option('py_sources_dir') != '' ? get_option('py_sources_dir') / 'ubuntu-hello' : join_paths(get_option('prefix'), get_option('libdir'), 'ubuntu-hello')
endif

pam_module_conf_data = configuration_data(paths_dict)
pam_module_conf_data.set('compare_script_path', join_paths(pysourcesinstalldir, 'compare.py'))
pam_module_conf_data.set('config_file_path', config_path)
subdir('pam')
if get_option('install_pam_config')
    # pamdir is inherited from the pam subproject
    pam_config = configure_file(
        input: 'pam-config/ubuntu-hello.in',
        output: 'pam-config',
        configuration: {'pamdir': pamdir}
    )
    install_data(
        pam_config,
        install_dir: get_option('prefix') / get_option('datadir') / 'pam-configs',
        install_mode: 'rwxr-xr-x',
        install_tag: 'pam',
        rename: 'ubuntu-hello',
    )
    install_data(
        'pam-config/ubuntu-hello-verify',
        install_dir: get_option('sysconfdir') / 'pam.d',
        install_mode: 'rw-r--r--',
        install_tag: 'pam',
        rename: 'ubuntu-hello-verify',
    )
endif

if get_option('install_in_site_packages')
    py.install_sources(
        py_sources,
        subdir: 'ubuntu-hello',
        preserve_path: true,
        install_tag: 'py_sources',
    )
else
    install_data(
        py_sources,
        preserve_path: true,
        install_dir: pysourcesinstalldir,
        install_mode: 'r--r--r--',
        install_tag: 'py_sources',
    )
endif

install_data('logo.png', install_tag: 'meta')
autocomplete = configure_file(
    input: 'autocomplete/ubuntu-hello.in',
    output: 'autocomplete',
    configuration: configuration_data({ 'config_path': config_path })
)
install_data(
    autocomplete,
    install_dir: join_paths(get_option('prefix'), get_option('datadir'), 'bash-completion', 'completions'),
    install_mode: 'rwxr--r--',
    install_tag: 'bash_completion',
    rename: 'ubuntu-hello',
)

meson.add_install_script('install_config.py', meson.current_source_dir() / 'config.ini', confdir)

install_data('dlib-data/install.sh', 'dlib-data/Readme.md', install_dir: dlibdatadir, install_mode: 'rwxr--r--')

install_man('../ubuntu-hello.1')

# if get_option('fetch_dlib_data')
#     downloader = find_program('wget')
#     bunzip2 = find_program('bunzip2')

#     links = [ 
#         'https://github.com/davisking/dlib-models/raw/master/dlib_face_recognition_resnet_model_v1.dat.bz2',
#         'https://github.com/davisking/dlib-models/raw/master/mmod_human_face_detector.dat.bz2',
#         'https://github.com/davisking/dlib-models/raw/master/shape_predictor_5_face_landmarks.dat.bz2'
#     ]

#     archived_model_files = [
#         'dlib_face_recognition_resnet_model_v1.dat.bz2',
#         'shape_predictor_5_face_landmarks.dat.bz2',
#         'mmod_human_face_detector.dat.bz2'
#     ]

#     download = run_command(
#         'download',
#         links,
#         output: archived_model_files,
#         command: [downloader, '-O', '@OUTPUT@', '@INPUT@']
#     )

#     model_files = [
#         'dlib_face_recognition_resnet_model_v1.dat',
#         'shape_predictor_5_face_landmarks.dat',
#         'mmod_human_face_detector.dat'
#     ]

#     models = custom_target(
#         'models',
#         input: archived_model_files,
#         output: model_files,
#         command: [bunzip2, '-k', '@INPUT@'],
#     )

#     install_data(
#         model_files,
#         install_dir: join_paths(get_option('prefix'), get_option('libdir'), 'dlib_models'),
#     )

# endif

cli_path = join_paths(pysourcesinstalldir, 'cli.py')
conf_data = configuration_data({ 'script_path': cli_path, 'python_path': py.full_path() })

bin_name = 'ubuntu-hello'
bin = configure_file(
    input: 'bin/ubuntu-hello.in',
    output: bin_name,
    configuration: conf_data
)
install_data(
  bin,
  install_mode: 'rwxr-xr-x',
  install_dir: get_option('bindir'),
  install_tag: 'bin',
)
if get_option('fetch_dlib_data')
    meson.add_install_script('download_models.py', dlibdatadir)
endif
