#!/usr/bin/env python

from os.path import join, abspath
from pkg_resources import resource_filename
from pytest import main


epiphan_dvi2pcieduo_working_dir = abspath(
    resource_filename('giftgrab.tests',
                      join('epiphan', 'dvi2pcieduo')))
epiphan_dvi2pcieduo_config_dir = abspath(
    resource_filename('giftgrab.tests',
                      join('epiphan', 'dvi2pcieduo', 'data')))


def test_hevc():
    working_dir = abspath(resource_filename('giftgrab.tests', 'target'))
    ret = main(['--codec=HEVC', working_dir])
    if ret: exit(ret)


def test_xvid():
    working_dir = abspath(resource_filename('giftgrab.tests', 'target'))
    ret = main(['--codec=XviD', working_dir])
    if ret: exit(ret)


def test_vp9():
    working_dir = abspath(resource_filename('giftgrab.tests', 'target'))
    ret = main(['--codec=VP9', working_dir])
    if ret: exit(ret)


def __run_epiphan_tests(colour_space):
    for port in ['SDI', 'DVI']:
        ret = main(['--colour-space=%s' % (colour_space),
                    '--port=%s' % (port),
                    epiphan_dvi2pcieduo_working_dir, '-m', 'unit'])
        if ret: exit(ret)

    ret = main(['--colour-space=%s' % (colour_space),
                '--config-dir=%s' % (epiphan_dvi2pcieduo_config_dir),
                epiphan_dvi2pcieduo_working_dir, '-m', 'real_time'])
    if ret: exit(ret)


def test_epiphan_dvi2pcieduo_bgr24():
    __run_epiphan_tests('BGR24')


def test_epiphan_dvi2pcieduo_i420():
    __run_epiphan_tests('I420')