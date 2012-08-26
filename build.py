#!/usr/bin/env python

import os
import sys
import urllib2
import tarfile
import time

# check python ver 2.6+

# get cpu count
import multiprocessing as mp
cpuCount = mp.cpu_count()

# native
cflagsopt = '-march=native'
# dcs24 tape2
cflagsopt = '-march=core2 -msse4.1'
# ts
#cflagsopt = '-march=corei7'

# define files
yasm = 'yasm-1.2.0'
zlib = 'zlib-1.2.7'
bzip2 = 'bzip2-1.0.6'
libpng = 'libpng-1.5.12'
openjpeg = 'openjpeg-1.5.0'
libogg = 'libogg-1.3.0'
libvorbis = 'libvorbis-1.3.2'
libtheora = 'libtheora-1.1.1'
libvpx = 'libvpx-1.1.0'
faac = 'faac-1.28'
libaacplus = 'libaacplus-2.0.2'
vo_aacenc = 'vo-aacenc-0.1.2'
speex = 'speex-1.2rc1'
lame = 'lame-3.99.5'
x264 = 'x264-d9d2288'
x264git = 'git://git.videolan.org/x264.git'
x264BitDepth = '8'
x264Chroma = 'all'
xvid = 'xvid-1.3.2'
utvideo = 'utvideo-11.1.1'
ffmpeggit = 'git://source.ffmpeg.org/ffmpeg.git'
ffmbc = 'FFmbc-0.7-rc7'

#os.environ['ENV_ROOT'] = 'pwd'
# source env.source
ENV_ROOT = '/root/tmp/v2'
TARGET_DIR = os.path.join(ENV_ROOT, 'target')
BUILD_DIR = os.path.join(ENV_ROOT, 'build')
BUILD_GIT_DIR = os.path.join(ENV_ROOT, 'sourcegit')
TAR_DIR = os.path.join(ENV_ROOT, 'sourcetar')

# setup ENV
envpath = os.getenv('PATH')
os.putenv('PATH', '%s:%s' % (os.path.join(TARGET_DIR, 'bin'), envpath))
os.putenv('PKG_CONFIG_PATH', os.path.join(TARGET_DIR, 'lib', 'pkgconfig'))
os.putenv('CFLAGS', cflagsopt)


def setupDIR():
    for item in [ENV_ROOT, TARGET_DIR, BUILD_DIR, BUILD_GIT_DIR, TAR_DIR]:
        os.system('mkdir -p %s' % item)
def cleanTARGET_DIR():
    os.system('rm -rf %s' % TARGET_DIR)
def cleanBUILD_DIR():
    os.system('rm -rf %s' % BUILD_DIR)
def cleanBUILDGIT_DIR():
    os.system('rm -rf %s' % BUILD_GIT_DIR)
def cleanTAR_DIR():
    os.system('rm -rf %s' % TAR_DIR)
def cleanALL():
    cleanTARGET_DIR()
    cleanBUILD_DIR()
    cleanTAR_DIR()

def prewarn():
    print('\nneeded packages:\ngcc glibc-static git xz\n\n')
    print('todo: add check for gcc, git xz')
    x = 3
    while x > 0:
        print(x)
        x = x - 1
        time.sleep(1)


fileList = []
for item in [
        yasm, zlib, bzip2, libpng, openjpeg, libogg, libvorbis, libtheora,
        libvpx, faac, libaacplus, vo_aacenc, speex, lame, x264, xvid, utvideo, ffmbc
        ]:
    fileList.append('%s.tar.xz' % item)


def f_getfiles():
    print('\n*** Downloading files ***\n')
    os.chdir(TAR_DIR)
    server = 'http://www.ghosttoast.com/pub/ffmpeg/libs'
    for fileName in fileList:
        if os.path.exists(os.path.join(TAR_DIR, fileName.rstrip('.xz'))) is False:
            try:
                print('%s/%s' % (server, fileName))
                response = urllib2.urlopen('%s/%s' % (server, fileName))
                data = response.read()
            except urllib2.HTTPError as e:
                print('error downloading %s/%s %s' % (server, fileName, e))
                sys.exit(1)
            f = open(fileName, 'wb')
            f.write(data)
            f.close()
        else:
            print('%s already downloaded' % fileName.rstrip('.xz'))
    f_sync()

def f_decompressfiles():
    print('\n*** Decompressing xz files ***\n')
    os.chdir(BUILD_DIR)
    for fileName in fileList:
        if os.path.exists(os.path.join(TAR_DIR, fileName.rstrip('.xz'))) is False:
            os.system('xz -dv %s' % os.path.join(TAR_DIR, fileName))
        else:
            print('%s already uncompressed' % fileName)
    f_sync()
    git_ffmpeg()
    #git_x264()
    f_sync()

def f_sync():
    print('\n*** Syncinig Hard Drive ***\n')
    os.system('sync')

def git_ffmpeg():
    print('\n*** Cloning ffmpeg ***\n')
    if os.path.exists(os.path.join(BUILD_GIT_DIR, 'ffmpeg')):
        print('git pull')
        os.chdir(os.path.join(BUILD_GIT_DIR, 'ffmpeg'))
        os.system('git pull')
    else:
        os.chdir(BUILD_GIT_DIR)
        os.system('git clone %s' % ffmpeggit)

def git_ffmpeg_deploy():
    print('\n*** Deploy ffmpeg git to BUILD_DIR***\n')
    if os.path.exists(os.path.join(BUILD_GIT_DIR, 'ffmpeg')):
        os.chdir(BUILD_GIT_DIR)
        os.system('cp -rf ./ffmpeg %s' % BUILD_DIR)

def git_x264():
    print('\n*** Cloning x264 ***\n')
    if os.path.exists(os.path.join(BUILD_GIT_DIR, 'x264')):
        print('git pull')
        os.chdir(os.path.join(BUILD_GIT_DIR, 'x264'))
        os.system('git pull')
    else:
        os.chdir(BUILD_DIR)
        os.system('git clone %s' % x264git)

def git_x264_deploy():
    print('\n*** Deploy x264 git to BUILD_DIR ***\n')
    if os.path.exists(os.path.join(BUILD_GIT_DIR, 'x264')):
        os.chdir(BUILD_GIT_DIR)
        os.system('cp -rf ./x264 %s' % BUILD_DIR)

def f_extractfiles():
    global fileList
    print('\n*** Extracting tar files ***\n')
    os.chdir(BUILD_DIR)
    for fileName in fileList:
        print(fileName.rstrip('.xz'))
        tar = tarfile.open(os.path.join(TAR_DIR, fileName.rstrip('.xz')))
        tar.extractall()
        tar.close()
    git_ffmpeg_deploy()
    #git_x264_deploy()
    f_sync()

def b_yasm():
    print('\n*** Building yasm ***\n')
    os.chdir(os.path.join(BUILD_DIR, yasm))
    os.system('./configure --prefix=%s' % TARGET_DIR)
    os.system('make -j %s && make install' % cpuCount)

def b_zlib():
    print('\n*** Building zlib ***\n')
    os.chdir(os.path.join(BUILD_DIR, zlib))
    os.system('./configure --prefix=%s --static' % TARGET_DIR)
    os.system('make -j %s && make install' % cpuCount)

def b_bzip2():
    print('\n*** Building bzip2 ***\n')
    os.chdir(os.path.join(BUILD_DIR, bzip2))
    os.system('make')
    os.system('make install PREFIX=%s' % TARGET_DIR)

def b_libpng():
    print('\n*** Building libpng ***\n')
    os.chdir(os.path.join(BUILD_DIR, libpng))
    os.system('./configure --prefix=%s --enable-static --disable-shared' % TARGET_DIR)
    os.system('make -j %s && make install' % cpuCount)

def b_openjpeg():
    print('\n*** Building openjpeg ***\n')
    os.chdir(os.path.join(BUILD_DIR, openjpeg))
    os.system('./configure --prefix=%s --enable-static --disable-shared' % TARGET_DIR)
    os.system('make -j %s && make install' % cpuCount)

def b_libogg():
    print('\n*** Building libogg ***\n')
    os.chdir(os.path.join(BUILD_DIR, libogg))
    os.system('./configure --prefix=%s --enable-static --disable-shared' % TARGET_DIR)
    os.system('make -j %s && make install' % cpuCount)

def b_libvorbis():
    print('\n*** Building libvorbis ***\n')
    os.chdir(os.path.join(BUILD_DIR, libvorbis))
    os.system('./configure --prefix=%s --enable-static --disable-shared' % TARGET_DIR)
    os.system('make -j %s && make install' % cpuCount)

def b_libtheora():
    print('\n*** Building libtheora ***\n')
    os.chdir(os.path.join(BUILD_DIR, libtheora))
    os.system('./configure --prefix=%s --enable-static --disable-shared' % TARGET_DIR)
    os.system('make -j %s && make install' % cpuCount)

def b_libvpx():
    print('\n*** Building libvpx ***\n')
    os.chdir(os.path.join(BUILD_DIR, libvpx))
    os.system('./configure --prefix=%s --enable-static --disable-shared' % TARGET_DIR)
    os.system('make -j %s && make install' % cpuCount)

def b_faac():
    print('\n*** Building faac ***\n')
    os.chdir(os.path.join(BUILD_DIR, faac))
    os.system('./configure --prefix=%s --enable-static --disable-shared --without-mp4v2' % TARGET_DIR)
    os.system('make -j %s && make install' % cpuCount)

def b_libaacplus():
    print('\n*** Building libaacplus ***\n')
    os.chdir(os.path.join(BUILD_DIR, libaacplus))
    # need to generate 'configure'
    os.system('./autogen.sh')
    os.system('./configure --prefix=%s --enable-static --disable-shared' % TARGET_DIR)
    # don't multithread, I don't think it works with this library
    os.system('make && make install')

def b_vo_aacenc():
    print('\n*** Building vo-aacenc ***\n')
    os.chdir(os.path.join(BUILD_DIR, vo_aacenc))
    os.system('./configure --prefix=%s --enable-static --disable-shared' % TARGET_DIR)
    os.system('make -j %s && make install' % cpuCount)

def b_speex():
    print('\n*** Building speex ***\n')
    os.chdir(os.path.join(BUILD_DIR, speex))
    os.system('./configure --prefix=%s --enable-static --disable-shared --enable-sse' % TARGET_DIR)
    os.system('make -j %s && make install' % cpuCount)

def b_lame():
    print('\n*** Building lame ***\n')
    os.chdir(os.path.join(BUILD_DIR, lame))
    os.system('./configure --prefix=%s --enable-static --disable-shared' % TARGET_DIR)
    os.system('make -j %s && make install' % cpuCount)

def b_x264():
    print('\n*** Building x264 ***\n')
    os.chdir(os.path.join(BUILD_DIR, x264))
    os.system('./configure --prefix=%s --enable-static --disable-shared --disable-cli --disable-swscale --disable-lavf --disable-ffms --disable-gpac --bit-depth=%s --chroma-format=%s' % (TARGET_DIR, x264BitDepth, x264Chroma))
    os.system('make -j %s && make install' % cpuCount)

def b_xvid():
    print('\n*** Building xvid ***\n')
    os.chdir(os.path.join(BUILD_DIR, xvid, 'build', 'generic'))
    os.system('./configure --prefix=%s --enable-static --disable-shared' % TARGET_DIR)
    os.system('make -j %s && make install' % cpuCount)
    #os.system('rm -f %s' % os.path.join(TARGET_DIR, 'lib', 'libxvidcore.so.*'))

def b_utvideo():
    print('\n*** Building utvideo ***\n')
    os.chdir(os.path.join(BUILD_DIR, utvideo))
    #os.system('./configure --prefix=%s --enable-static --disable-shared' % TARGET_DIR)
    os.system('make -j %s && make prefix=%s install' % (cpuCount, TARGET_DIR))

def b_ffmpeg():
    print('\n*** Building ffmpeg ***\n')
    os.chdir(os.path.join(BUILD_DIR,'ffmpeg'))
    confcmd = './configure --prefix=%s' % TARGET_DIR
    confcmd += ' --extra-version=static'
    confcmd += ' --disable-debug'
    confcmd += ' --enable-static'
    confcmd += ' --disable-shared'
    confcmd += ' --extra-cflags=\'--static %s -I%s\'' % (cflagsopt, os.path.join(TARGET_DIR, 'include'))
    confcmd += ' --extra-ldflags=\'-L%s -static -static-libgcc\'' % os.path.join(TARGET_DIR, 'lib')
    confcmd += ' --enable-gpl'
    confcmd += ' --enable-version3'
    confcmd += ' --enable-nonfree'
    confcmd += ' --disable-doc'
    confcmd += ' --disable-ffplay'
    confcmd += ' --disable-ffserver'
    confcmd += ' --enable-bzlib'
    confcmd += ' --enable-zlib'
    confcmd += ' --enable-libfaac'
    confcmd += ' --enable-libmp3lame'
    confcmd += ' --enable-libopenjpeg'
    confcmd += ' --enable-libvorbis'
    confcmd += ' --enable-libtheora'
    confcmd += ' --enable-libvpx'
    confcmd += ' --enable-libutvideo'
    confcmd += ' --enable-libvo-aacenc'
    confcmd += ' --enable-libspeex'
    confcmd += ' --enable-libaacplus'
    confcmd += ' --disable-devices'

    os.system('make distclean')
    os.system(confcmd)
    os.system('make -j %s && make install' % cpuCount)

def b_ffmbc():
    print('\n*** Building ffmbc ***\n')
    os.chdir(os.path.join(BUILD_DIR, ffmbc))
    confcmd = './configure --prefix=%s' % TARGET_DIR
    confcmd += ' --extra-version=static'
    confcmd += ' --disable-debug'
    confcmd += ' --enable-static'
    confcmd += ' --disable-shared'
    confcmd += ' --extra-cflags=\'--static %s -I%s\'' % (cflagsopt, os.path.join(TARGET_DIR, 'include'))
    confcmd += ' --extra-ldflags=\'-L%s -static -static-libgcc\'' % os.path.join(TARGET_DIR, 'lib')
    confcmd += ' --enable-gpl'
    confcmd += ' --enable-nonfree'
    confcmd += ' --disable-doc'
    confcmd += ' --disable-ffplay'
    confcmd += ' --enable-bzlib'
    confcmd += ' --enable-zlib'
    confcmd += ' --enable-libfaac'
    confcmd += ' --enable-libmp3lame'
    confcmd += ' --enable-libopenjpeg'
    confcmd += ' --enable-libvorbis'
    confcmd += ' --enable-libtheora'
    confcmd += ' --enable-libvpx'
    confcmd += ' --enable-libspeex'
    confcmd += ' --disable-devices'

    os.system('make distclean')
    os.system(confcmd)
    #os.system('make -j %s && make install' % cpuCount)
    os.system('make -j %s' % cpuCount)
    # auto "install"
    #os.system('make install')
    # manual "install"
    os.system('cp -f ffmbc %s' % os.path.join(TARGET_DIR, 'bin', 'ffmbc'))
    os.system('cp -f ffprobe %s' % os.path.join(TARGET_DIR, 'bin', 'ffmbcprobe'))

def u_striplibs():
    os.system('strip %s/*' % os.path.join(TARGET_DIR, 'lib'))

def go_get():
    f_getfiles()
    f_decompressfiles()

def go_main():
    f_extractfiles()
    b_yasm()
    b_zlib()
    b_bzip2()
    b_libpng()
    b_openjpeg()
    b_libogg()
    b_libvorbis()
    b_libtheora()
    b_libvpx()
    b_faac()
    b_libaacplus()
    b_vo_aacenc()
    b_speex()
    b_lame()
    b_x264()
    b_xvid()
    b_utvideo()

def go_ffmpeg():
    b_ffmpeg()
    #b_ffmbc()
    #b_libav()

def run():
    try:
        prewarn()
        cleanTARGET_DIR()
        cleanBUILD_DIR()
        #cleanTAR_DIR()
        setupDIR()
        go_get()
        go_main()
        go_ffmpeg()
    except KeyboardInterrupt:
        print('\nBye\n')
        sys.exit(0)

#cleanALL()
#setupDIR()
#f_getfiles()
#f_extractfiles()
run()

