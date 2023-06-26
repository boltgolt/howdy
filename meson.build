project('howdy', 'cpp', license: 'MIT', version: 'beta', meson_version: '>= 0.64.0')

confdir = get_option('config_dir') != '' ? get_option('config_dir') : join_paths(get_option('sysconfdir'), 'howdy')
dlibdatadir = get_option('dlib_data_dir') != '' ? get_option('dlib_data_dir') : join_paths(confdir, 'dlib-data')
usermodelsdir = get_option('user_models_dir') != '' ? get_option('user_models_dir') : join_paths(confdir, 'models')
datadir = get_option('data_dir') != '' ? get_option('data_dir') : join_paths(get_option('prefix'), get_option('datadir'), 'howdy')
logpath = get_option('log_path')

config_path = join_paths(confdir, 'config.ini')

paths_dict = {
    'config_dir': confdir,
    'dlib_data_dir': dlibdatadir,
    'user_models_dir': usermodelsdir,
    'data_dir': datadir,
    'log_path': logpath,
}

# We need to keep this order beause howdy-gtk defines the gtk script path
subdir('howdy-gtk')
subdir('howdy')