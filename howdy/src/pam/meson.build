inih_cpp = dependency('INIReader', fallback: ['inih', 'INIReader_dep'])
libevdev = dependency('libevdev')
libpam = meson.get_compiler('cpp').find_library('pam')
threads = dependency('threads')

# Translations
subdir('po')

# Paths
paths_h = configure_file(
	input: 'paths.hh.in',
	output: 'paths.hh',
	configuration: pam_module_conf_data,
	install_dir: get_option('pam_dir')
)

pamdir = get_option('pam_dir') != '' ? get_option('pam_dir') : join_paths(get_option('libdir'), 'security')

shared_library(
	'pam_howdy',
	'main.cc',
	'enter_device.cc',
	dependencies: [
		libpam,
		inih_cpp,
		threads,
		libevdev,
	],
	link_depends: [
		paths_h,
	],
	install: true,
	install_dir: pamdir,
	install_tag: 'pam_module',
	name_prefix: ''
)
