i18n = import('i18n')

# define GETTEXT_PACKAGE and LOCALEDIR
gettext_package = '-DGETTEXT_PACKAGE="@0@"'.format(meson.project_name())
localedir = '-DLOCALEDIR="@0@"'.format(get_option('prefix') / get_option('localedir'))
add_project_arguments(gettext_package, localedir, language: 'cpp')

i18n.gettext(meson.project_name(),
    args: [ '--directory=' + meson.source_root(), '--keyword=S:1' ]
)