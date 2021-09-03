project('pam_howdy', 'cpp', version: '0.1.0', default_options: ['cpp_std=c++14'])

inih = subproject('inih')
inih_cpp = inih.get_variable('INIReader_dep')

libpam = meson.get_compiler('c').find_library('pam')
boost = dependency('boost', modules: ['locale'])
threads = dependency('threads')
shared_library('pam_howdy', 'main.cc', dependencies: [boost, libpam, inih_cpp, threads], install: true, install_dir: '/lib/security/')
