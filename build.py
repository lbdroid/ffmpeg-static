#!/usr/bin/env python

import os
import sys
import urllib2
import tarfile
import time
import subprocess

# check python ver 2.6+
if sys.version_info < (2, 6):
    print('need python 2.6+')
    sys.exit(0)

# get cpu count
import multiprocessing as mp
cpuCount = mp.cpu_count()
del mp

# check for git
p = subprocess.Popen('which git', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
data = p.communicate()[0]
if data.count('which') > 0:
    print('unable to find git')
    sys.exit(0)

# print env
os.system('export')

# native
cflagsopt = '-march=native'
#cflagsopt = '-march=native -fPIC'
# dcs24 tape2
cflagsopt = '-march=core2 -msse4.1'
#cflagsopt = '-march=core2 -msse4.1 -fPIC'
# ts
#cflagsopt = '-march=corei7'
#clfagsopt = '-march=corei7 -fPIC'

appendopt = ''
if sys.platform.startswith('linux'):
    appendopt += ' --enable-static --disable-shared'

# define files
xz = 'xz-5.0.4'
yasm = 'yasm-1.2.0'
zlib = 'zlib-1.2.7'
bzip2 = 'bzip2-1.0.6'
ncurses = 'ncurses-5.9'
jasper = 'jasper-1.900.1'
libpng = 'libpng-1.5.13'
openjpeg = 'openjpeg-1.5.0'  # 1.5.1 works with ffmpeg, none work with 2.0.0
libtiff = 'tiff-4.0.3'
libogg = 'libogg-1.3.0'
libvorbis = 'libvorbis-1.3.3'
libtheora = 'libtheora-1.1.1'
libvpx = 'libvpx-1.1.0'
libvpxgit = 'http://git.chromium.org/webm/libvpx.git'
libxml2 = 'libxml2-2.9.0'
expat = 'expat-2.1.0'
fontconfig = 'fontconfig-2.10.2'
freetype = 'freetype-2.4.10'
faac = 'faac-1.28'
vo_aacenc = 'vo-aacenc-0.1.2'
speex = 'speex-1.2rc1'
lame = 'lame-3.99.5'
x264 = 'x264-d9d2288'
x264git = 'git://git.videolan.org/x264.git'
x264BitDepth = '8'
x264Chroma = 'all'
xvid = 'xvid-1.3.2'
utvideo = 'utvideo-11.1.1'
gpac = 'gpac-0.5.0'
ffmpeggit = 'git://source.ffmpeg.org/ffmpeg.git'
ffmbc = 'FFmbc-0.7-rc7'

#os.environ['ENV_ROOT'] = 'pwd'
# source env.source
ENV_ROOT = os.getcwd()
TARGET_DIR = os.path.join(ENV_ROOT, 'target')
BUILD_DIR = os.path.join(ENV_ROOT, 'build')
BUILD_GIT_DIR = os.path.join(ENV_ROOT, 'sourcegit')
TAR_DIR = os.path.join(ENV_ROOT, 'sourcetar')

#
try:
    BUILD_NUMBER = os.getenv['BUILD_NUMBER']
except:
    BUILD_NUMBER = '0'
print('BUILD_NUMBER: %s' % BUILD_NUMBER)
OUT_FOLDER = 'output'
OUT_DIR = os.path.join(ENV_ROOT, OUT_FOLDER)


# setup ENV
envpath = os.getenv('PATH')
addpath = os.path.join(TARGET_DIR, 'bin')
if sys.platform.startswith('darwin'):
    addpath += ':/opt/local/bin'
os.putenv('PATH', '%s:%s' % (addpath, envpath))
os.putenv('PKG_CONFIG_PATH', os.path.join(TARGET_DIR, 'lib', 'pkgconfig'))
os.putenv('CFLAGS', cflagsopt)


def setupDIR():
    for item in [ENV_ROOT, TARGET_DIR, BUILD_DIR, BUILD_GIT_DIR, TAR_DIR, OUT_DIR]:
        os.system('mkdir -p %s' % item)
def cleanTARGET_DIR():
    os.system('rm -rf %s' % TARGET_DIR)
def cleanBUILD_DIR():
    os.system('rm -rf %s' % BUILD_DIR)
def cleanBUILDGIT_DIR():
    os.system('rm -rf %s' % BUILD_GIT_DIR)
def cleanTAR_DIR():
    os.system('rm -rf %s' % TAR_DIR)
def cleanOUT_DIR():
    os.system('rm -rf %s' % OUT_DIR)
def cleanOUT_DIR_FILES():
    os.system('rm -f %s.tar' % OUT_DIR)
    os.system('rm -f %s.tar.xz' % OUT_DIR)
def cleanALL():
    cleanTARGET_DIR()
    cleanBUILD_DIR()
    cleanTAR_DIR()
    cleanOUT_DIR()
    cleanOUT_DIR_FILES()

def prewarn():
    print('\nneeded packages:\ngcc glibc-static git xz\n\n')
    x = 2
    while x > 0:
        print(x)
        x = x - 1
        time.sleep(1)


fileList = []
for item in [
        yasm, zlib, bzip2, ncurses, jasper, libtiff, libpng, openjpeg, libogg, libvorbis, libtheora,
        faac, vo_aacenc, speex, lame, xvid,
        utvideo, gpac, ffmbc
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
            os.system('%s -dv %s' % (os.path.join(TARGET_DIR, 'bin', 'xz'), os.path.join(TAR_DIR, fileName)))
        else:
            print('%s already uncompressed' % fileName)
    f_sync()
    git_libvpx()
    git_ffmpeg()
    git_x264()
    f_sync()

def f_sync():
    print('\n*** Syncinig Hard Drive ***\n')
    os.system('sync')

def build_xz():
    print('\n*** downloading xz/liblzma ***\n')
    os.chdir(TAR_DIR)
    server = 'http://www.ghosttoast.com/pub/ffmpeg/libs'
    fileName = '%s.tar.gz' % xz
    if os.path.exists(os.path.join(TAR_DIR, fileName.rstrip('.gz'))) is False:
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
        print('%s already downloaded' % fileName.rstrip('.gz'))
    f_sync()

    print('\n*** Decompressing xz/liblzma ***\n')
    os.chdir(BUILD_DIR)
    if os.path.exists(os.path.join(TAR_DIR, fileName.rstrip('.gz'))) is False:
        os.system('gunzip -v %s' % os.path.join(TAR_DIR, fileName))
    else:
        print('%s already uncompressed' % fileName)
    f_sync()

    print('\n*** Extracting xz/liblzma ***\n')
    os.chdir(BUILD_DIR)
    print(fileName.rstrip('.gz'))
    tar = tarfile.open(os.path.join(TAR_DIR, fileName.rstrip('.gz')))
    tar.extractall()
    tar.close()
    f_sync()

    print('\n*** Building xz/liblzma ***\n')
    os.chdir(os.path.join(BUILD_DIR, xz))
    os.system('./configure --prefix=%s %s' % (TARGET_DIR, appendopt))
    os.system('make -j %s && make install' % cpuCount)
    f_sync()

def git_libvpx():
    print('\n*** Cloning libvpx ***\n')
    if os.path.exists(os.path.join(BUILD_GIT_DIR, 'libvpx')):
        print('git pull')
        os.chdir(os.path.join(BUILD_GIT_DIR, 'libvpx'))
        os.system('git pull')
    else:
        os.chdir(BUILD_GIT_DIR)
        os.system('git clone %s' % libvpxgit)

def git_libvpx_deploy():
    print('\n*** Deploy libvpx git to BUILD_DIR ***\n')
    os.chdir(BUILD_GIT_DIR)
    os.system('cp -rf ./libvpx %s' % BUILD_DIR)

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
    print('\n*** Deploy ffmpeg git to BUILD_DIR ***\n')
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
        os.chdir(BUILD_GIT_DIR)
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
    git_libvpx_deploy()
    git_ffmpeg_deploy()
    git_x264_deploy()
    f_sync()

def b_yasm():
    print('\n*** Building yasm ***\n')
    os.chdir(os.path.join(BUILD_DIR, yasm))
    os.system('./configure --prefix=%s' % TARGET_DIR)
    os.system('make -j %s && make install' % cpuCount)

def b_zlib():
    print('\n*** Building zlib ***\n')
    os.chdir(os.path.join(BUILD_DIR, zlib))
    os.system('export CFLAGS="$CFLAGS -fPIC";./configure --prefix=%s --static' % TARGET_DIR)
    os.system('export CFLAGS="$CFLAGS -fPIC";make -j %s && make install' % cpuCount)

def b_bzip2():
    print('\n*** Building bzip2 ***\n')
    os.chdir(os.path.join(BUILD_DIR, bzip2))
    os.system('make CFLAGS="-Wall -Winline -O2 -g -D_FILE_OFFSET_BITS=64 -fPIC"')
    os.system('make install PREFIX=%s' % TARGET_DIR)

def b_ncurses():
    print('\n*** Building ncurses ***\n')
    os.chdir(os.path.join(BUILD_DIR, ncurses))
    os.system('./configure --with-termlib --with-ticlib --prefix=%s %s' % (TARGET_DIR, appendopt))
    os.system('make -j %s && make install' % cpuCount)

def b_jasper():
    print('\n*** Building jasper (jp2) ***\n')
    os.chdir(os.path.join(BUILD_DIR, jasper))
    os.system('./configure --enable-shared=no --enable-static=yes --prefix=%s %s' % (TARGET_DIR, appendopt))
    os.system('make -j %s && make install' % cpuCount)

def b_libpng():
    print('\n*** Building libpng ***\n')
    os.chdir(os.path.join(BUILD_DIR, libpng))
    os.system('./configure --prefix=%s %s' % (TARGET_DIR, appendopt))
    os.system('make -j %s && make install' % cpuCount)

def b_openjpeg():
    print('\n*** Building openjpeg ***\n')
    os.chdir(os.path.join(BUILD_DIR, openjpeg))
    os.system('./configure --prefix=%s %s' % (TARGET_DIR, appendopt))  # openjpeg 1.5
    #os.system('cmake . -DCMAKE_INSTALL_PREFIX=%s -DBUILD_SHARED_LIBS:bool=off' % TARGET_DIR)  # openjpeg 2.0.0
    os.system('make -j %s && make install' % cpuCount)

def b_libtiff():
    print('\n*** Building libtiff ***\n')
    os.chdir(os.path.join(BUILD_DIR, libtiff))
    os.system('export CFLAGS="--static -I%s";export LDFLAGS="-L%s -static -static-libgcc";./configure --prefix=%s --enable-shared=no --enable-static=yes %s' % (os.path.join(TARGET_DIR, 'include'), os.path.join(TARGET_DIR, 'lib'), TARGET_DIR, appendopt))
    os.system('export CFLAGS="--static -I%s";export LDFLAGS="-L%s -static -static-libgcc";make -j %s && make install' % (os.path.join(TARGET_DIR, 'include'), os.path.join(TARGET_DIR, 'lib'), cpuCount))

def b_libogg():
    print('\n*** Building libogg ***\n')
    os.chdir(os.path.join(BUILD_DIR, libogg))
    os.system('./configure --prefix=%s %s' % (TARGET_DIR, appendopt))
    os.system('make -j %s && make install' % cpuCount)

def b_libvorbis():
    print('\n*** Building libvorbis ***\n')
    os.chdir(os.path.join(BUILD_DIR, libvorbis))
    os.system('./configure --prefix=%s %s' % (TARGET_DIR, appendopt))
    os.system('make -j %s && make install' % cpuCount)

def b_libtheora():
    print('\n*** Building libtheora ***\n')
    os.chdir(os.path.join(BUILD_DIR, libtheora))
    os.system('./configure --prefix=%s --enable-static --disable-shared' % TARGET_DIR)
    os.system('make -j %s && make install' % cpuCount)

def b_libvpx():
    print('\n*** Building libvpx ***\n')
    #os.chdir(os.path.join(BUILD_DIR, libvpx))
    os.chdir(os.path.join(BUILD_DIR, 'libvpx'))
    os.system('./configure --prefix=%s --enable-static --disable-shared' % TARGET_DIR)
    os.system('make -j %s && make install' % cpuCount)

def b_expat():
    print('\n*** Building expat ***\n')
    os.chdir(os.path.join(BUILD_DIR, expat))
    os.system('./configure --prefix=%s --enable-static --disable-shared' % TARGET_DIR)
    os.system('make -j %s && make install' % cpuCount)

def b_libxml2():
    print('\n*** Building libxml2 ***\n')
    os.chdir(os.path.join(BUILD_DIR, libxml2))
    os.system('./configure --prefix=%s --enable-static --disable-shared' % TARGET_DIR)
    os.system('make -j %s && make install' % cpuCount)

def b_fontconfig():
    print('\n*** Building fontconfig ***\n')
    os.chdir(os.path.join(BUILD_DIR, fontconfig))
    os.system('./configure --prefix=%s --enable-static --disable-shared' % TARGET_DIR)
    os.system('make -j %s && make install' % cpuCount)

def b_freetype():
    print('\n*** Building freetype ***\n')
    os.chdir(os.path.join(BUILD_DIR, freetype))
    os.system('./configure --prefix=%s --enable-static --disable-shared' % TARGET_DIR)
    os.system('make -j %s && make install' % cpuCount)

def b_faac():
    print('\n*** Building faac ***\n')
    os.chdir(os.path.join(BUILD_DIR, faac))
    os.system('./configure --prefix=%s --without-mp4v2 %s' % (TARGET_DIR, appendopt))
    os.system('make -j %s && make install' % cpuCount)

def b_vo_aacenc():
    print('\n*** Building vo-aacenc ***\n')
    os.chdir(os.path.join(BUILD_DIR, vo_aacenc))
    os.system('./configure --prefix=%s %s' % (TARGET_DIR, appendopt))
    os.system('make -j %s && make install' % cpuCount)

def b_speex():
    print('\n*** Building speex ***\n')
    os.chdir(os.path.join(BUILD_DIR, speex))
    os.system('./configure --prefix=%s %s --enable-sse' % (TARGET_DIR, appendopt))
    os.system('make -j %s && make install' % cpuCount)

def b_lame():
    print('\n*** Building lame ***\n')
    os.chdir(os.path.join(BUILD_DIR, lame))
    os.system('./configure --disable-frontend --enable-shared=no --enable-static=yes --prefix=%s %s' % (TARGET_DIR, appendopt))
    os.system('make -j %s && make install' % cpuCount)

def b_x264():
    print('\n*** Building x264 ***\n')
    os.chdir(os.path.join(BUILD_DIR, 'x264'))  # for git checkout
    if appendopt == '':
        x264appendopt = '--shared'
    else:
        x264appendopt = appendopt
    os.system('./configure --prefix=%s --disable-cli --disable-swscale --disable-lavf --disable-ffms --disable-gpac --bit-depth=%s --chroma-format=%s %s' % (TARGET_DIR, x264BitDepth, x264Chroma, x264appendopt))
    os.system('make -j %s && make install' % cpuCount)

def b_x264full():
    print('\n*** Build x264 Full ***\n')
    os.chdir(os.path.join(BUILD_DIR, 'x264'))  # for git checkout
    os.system('make clean')
    os.system('./configure --prefix=%s --enable-static --bit-depth=%s --chroma-format=%s --extra-cflags=\'--static -I%s\' --extra-ldflags=\'-L%s -static -static-libgcc\'' % (TARGET_DIR, x264BitDepth, x264Chroma, os.path.join(TARGET_DIR, 'include'), os.path.join(TARGET_DIR, 'lib')))
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
    #os.system('make CXXFLAGS="-g -O2 -Wall -Wextra -Wno-multichar -Wno-unused-parameter -Wno-sign-compare -fPIC" -j %s && make prefix=%s install' % (cpuCount, TARGET_DIR))
    os.system('make -j %s && make prefix=%s install' % (cpuCount, TARGET_DIR))

def b_gpac():
    print('\n*** Building gpac ***\n')
    os.chdir(os.path.join(BUILD_DIR, 'gpac'))
    confcmd = './configure --prefix=%s --disable-ssl --disable-ipv6 --disable-wx --disable-platinum --disable-alsa --disable-oss-audio --disable-jack --disable-pulseaudio --disable-x11-shm --disable-x11-xv --use-ft=no --use-faad=no --use-jpeg=no --use-png=no --use-mad=no --use-xvid=no --use-ffmpeg=no --use-ogg=no --use-vorbis=no --use-theora=no --use-openjpeg=no --use-a52=no --enable-static-bin' % TARGET_DIR
    confcmd += ' --extra-cflags=\'--static %s -I%s\'' % (cflagsopt, os.path.join(TARGET_DIR, 'include'))
    confcmd += ' --extra-ldflags=\'-L%s -static -static-libgcc\'' % os.path.join(TARGET_DIR, 'lib')
    os.system(confcmd)
    os.system('make lib -j %s' % cpuCount)
    os.system('make install-lib')

def b_ffmpeg():
    print('\n*** Building ffmpeg ***\n')
    os.chdir(os.path.join(BUILD_DIR,'ffmpeg'))
    confcmd = './configure --prefix=%s' % TARGET_DIR
    confcmd += ' --extra-version=static'
    confcmd += ' --disable-debug'
    confcmd += ' --enable-static'
    confcmd += ' --disable-shared'
    if sys.platform.startswith('linux'):
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
    #confcmd += ' --enable-libfreetype'
    #confcmd += ' --enable-fontconfig'
    confcmd += ' --enable-libx264'
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
    if sys.platform.startswith('linux'):
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
    confcmd += ' --enable-libx264'
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

def out_pack():
    os.chdir(OUT_DIR)
    for item in ['ffmpeg', 'ffprobe', 'ffmbc', 'ffmbcprobe', 'x264', 'tiffcp', 'tiffinfo']:
        os.system('cp -f {0} ./'.format(os.path.join(TARGET_DIR, 'bin', item)))
    os.chdir(ENV_ROOT)
    os.system('tar -cvf ./{0}.tar ./{0}'.format(OUT_FOLDER))
    os.system('xz -ve9 ./{0}.tar'.format(OUT_FOLDER))

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
    b_ncurses()
    b_libtiff()
    b_libpng()
    b_openjpeg()
    b_libogg()
    b_libvorbis()
    b_libtheora()
    b_libvpx()
    #b_expat()
    #b_libxml2()
    #b_fontconfig()
    #b_freetype()
    b_faac()
    b_vo_aacenc()
    b_speex()
    b_lame()
    b_x264()
    b_xvid()
    b_utvideo()

def go_ffmpeg():
    b_ffmpeg()
    b_ffmbc()


def go_x264full():
    b_ffmpeg()
    b_gpac()
    b_x264full()

def run():
    try:
        prewarn()
        cleanOUT_DIR_FILES()
        cleanOUT_DIR()
        cleanTARGET_DIR()
        cleanBUILD_DIR()
        #cleanTAR_DIR()
        setupDIR()
        build_xz()
        go_get()
        go_main()
        go_ffmpeg()
        b_gpac()
        b_x264full()
        out_pack()
    except KeyboardInterrupt:
        print('\nBye\n')
        sys.exit(0)

if __name__ == '__main__':
    run()
    #b_x264full()
    #b_gpac()
    #b_ffmpeg()
    #b_ffmbc()


