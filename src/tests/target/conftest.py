from pygiftgrab import Storage


def pytest_addoption(parser):
    parser.addoption('--codec', action='store',
                     help='Codec (H265 or Xvid)')


def pytest_generate_tests(metafunc):
    if 'codec' in metafunc.fixturenames:
        codec_str = str(metafunc.config.option.codec)
        case_insensitive = codec_str.lower()
        if case_insensitive == 'h265':
            codec = Storage.File_H265
        elif case_insensitive == 'xvid':
            codec = Storage.File_XviD
        else:
            raise RuntimeError('Could not recognise codec ' +
                               codec_str)
        metafunc.parametrize('codec', [codec])