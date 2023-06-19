project('howdy', 'cpp', license: 'MIT', license_files: '../LICENSE', version: 'beta', meson_version: '>= 1.1.0')

py = import('python').find_installation()
py.dependency()

confdir = join_paths(get_option('sysconfdir'), 'howdy')
dlibdatadir = join_paths(confdir, 'dlib-data')
usermodelsdir = join_paths(confdir, 'models')
logpath = '/var/log/howdy'

py_conf = configuration_data({
    'config_dir': confdir,
    'dlib_data_dir': dlibdatadir,
    'user_models_dir': usermodelsdir,
    'log_path': logpath,
})

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
    'cli/list.py',
    'cli/remove.py',
    'cli/set.py',
    'cli/snap.py',
    'cli/test.py',
    'cli.py',
    'compare.py',
    'i18n.py',
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
compare_script_path = join_paths(py.get_install_dir(), 'howdy', 'compare.py')
subdir('pam')

py.install_sources(
    py_sources,
    subdir: 'howdy',
    preserve_path: true,
)

install_data('logo.png', install_tag: 'meta')

install_data('config.ini', install_dir: confdir, install_mode: 'rwxr--r--', install_tag: 'config')

install_data('dlib-data/install.sh', install_dir: dlibdatadir, install_mode: 'rwxr--r--')

install_data('dlib-data/Readme.md', install_dir: dlibdatadir, install_mode: 'r--r--r--', install_tag: 'docs')
install_man('../howdy.1')

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

py_path = py.get_install_dir()
cli_path = join_paths(py_path, 'howdy', 'cli.py')

conf_data = configuration_data({ 'script_path': cli_path })

bin_name = 'howdy'

bin = configure_file(
    input: 'bin/howdy.in',
    output: bin_name,
    configuration: conf_data
)

install_data(
  bin,
  install_mode: 'rwxr-xr-x',
  install_dir: get_option('bindir'),
)