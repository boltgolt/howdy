project('pam_howdy', 'cpp', version: '0.1.0', default_options: ['cpp_std=c++11'])

inih = subproject('inih')
inih_cpp = inih.get_variable('INIReader_dep')

libpam = meson.get_compiler('c').find_library('pam')
boost = dependency('boost', modules: ['filesystem'])
threads = dependency('threads')
shared_library('pam_howdy', 'main.cc', dependencies: [boost, libpam, inih_cpp, threads], install: true, install_dir: '/lib/security/')
