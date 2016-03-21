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
os.system('export 2>/dev/null')

cflagsopt = ''
# native
#cflagsopt = '-march=native'
#cflagsopt = '-march=native -fPIC'
# dcs24 tape2
#cflagsopt = '-march=core2 -msse4.1'
#cflagsopt = '-march=core2 -msse4.1 -fPIC'
# ts
#cflagsopt = '-march=corei7'
#clfagsopt = '-march=corei7 -fPIC'

appendopt = ''
if sys.platform.startswith('linux'):
    appendopt += ' --enable-static --disable-shared'

# define files
downloadList = []
downloadAuxList = []
gitList = []

xz = 'xz-5.2.2'
downloadList.append(xz)

yasm = 'yasm-1.3.0'
downloadList.append(yasm)

zlib = 'zlib-1.2.8'
downloadList.append(zlib)

bzip2 = 'bzip2-1.0.6'
downloadList.append(bzip2)

ncurses = 'ncurses-6.0'
downloadList.append(ncurses)

openssl = 'openssl-1.0.2g'
downloadList.append(openssl)

snappy = 'snappy-1.1.3'
downloadList.append(snappy)

libpng = 'libpng-1.6.21'
downloadList.append(libpng)

openjpeg = 'openjpeg-1.5.2'  # 1.5.1 works with ffmpeg, none work with 2.0.0
downloadList.append(openjpeg)

libtiff = 'tiff-4.0.3'
downloadList.append(libtiff)

libogg = 'libogg-1.3.2'
downloadList.append(libogg)

libvorbis = 'libvorbis-1.3.5'
downloadList.append(libvorbis)

libtheora = 'libtheora-1.1.1'
downloadList.append(libtheora)

libvpx = 'libvpx-1.5.0'
downloadList.append(libvpx)

speex = 'speex-1.2rc2'
downloadList.append(speex)

lame = 'lame-3.99.5'
downloadList.append(lame)

twolame = 'twolame-0.3.13'
downloadList.append(twolame)

soxr = 'soxr-0.1.2'
downloadList.append(soxr)

wavpack = 'wavpack-4.75.2'
downloadList.append(wavpack)

fdkaac = 'fdk-aac-0.1.4'
downloadList.append(fdkaac)

x264 = 'https://git.videolan.org/git/x264.git'
gitList.append(['x264', x264])
x264BitDepth = '8'
x264Chroma = 'all'

x265 = 'https://github.com/videolan/x265.git'
gitList.append(['x265', x265])

xvid = 'xvid-1.3.4'
downloadList.append(xvid)
downloadAuxList.append('xvid_Makefile.patch')

dcadec = 'dcadec-0.2.0'
downloadList.append(dcadec)

nvenc = 'nvidia_video_sdk_6.0.1'
downloadList.append(nvenc)

blackmagic = 'Blackmagic_DeckLink_SDK_10.6.1'
downloadList.append(blackmagic)

ffmpeg = 'git://source.ffmpeg.org/ffmpeg.git'
gitList.append(['ffmpeg', ffmpeg])


#os.environ['ENV_ROOT'] = 'pwd'
# source env.source
ENV_ROOT = os.getcwd()
TARGET_DIR = os.path.join(ENV_ROOT, 'target')
BUILD_DIR = os.path.join(ENV_ROOT, 'build')
BUILD_GIT_DIR = os.path.join(ENV_ROOT, 'sourcegit')
TAR_DIR = os.path.join(ENV_ROOT, 'sourcetar')

OUT_FOLDER = 'output'
OUT_DIR = os.path.join(ENV_ROOT, OUT_FOLDER)


# setup ENV
ENV_PATH_ORIG = os.getenv('PATH')
ENV_LD_ORIG = os.getenv('LD_LIBRARY_PATH')
if sys.platform.startswith('darwin'):
    addpath += ':/opt/local/bin'
os.putenv('PATH', '%s:%s' % (os.path.join(TARGET_DIR, 'bin'), ENV_PATH_ORIG))
os.putenv('LD_LIBRARY_PATH', '%s:%s' % (os.path.join(TARGET_DIR, 'lib'), ENV_LD_ORIG))
os.putenv('PKG_CONFIG_PATH', os.path.join(TARGET_DIR, 'lib', 'pkgconfig'))
ENV_CFLAGS = '-I%s' % os.path.join(TARGET_DIR, 'include')
os.putenv('CFLAGS', ENV_CFLAGS)
ENV_LDFLAGS = '-L%s -static -static-libgcc -static-libstdc++' % os.path.join(TARGET_DIR, 'lib')
os.putenv('LDFLAGS', ENV_LDFLAGS)
os.system('export')


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
    print('\nneeded packages:\ngcc glibc-static git cmake\n\n')
    x = 2
    while x > 0:
        print(x)
        x = x - 1
        time.sleep(1)


fileList = []
for item in downloadList:
    fileList.append('%s.tar.xz' % item)
for item in downloadAuxList:
    fileList.append('%s.xz' % item)


def f_getfiles():
    print('\n*** Downloading files ***\n')
    os.chdir(TAR_DIR)
    server = 'http://www.ghosttoast.com/pub/ffmpeg'
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
    for item in gitList:
        git_clone(item[0], item[1])
    f_sync()

def f_sync():
    print('\n*** Syncinig Hard Drive ***\n')
    os.system('sync')

def build_yasm():
    print('\n*** downloading yasm ***\n')
    os.chdir(TAR_DIR)
    server = 'http://www.ghosttoast.com/pub/ffmpeg'
    fileName = '%s.tar.gz' % yasm
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

    print('\n*** Decompressing yasm ***\n')
    os.chdir(BUILD_DIR)
    if os.path.exists(os.path.join(TAR_DIR, fileName.rstrip('.gz'))) is False:
        os.system('gunzip -v %s' % os.path.join(TAR_DIR, fileName))
    else:
        print('%s already uncompressed' % fileName)
    f_sync()

    print('\n*** Extracting yasm ***\n')
    os.chdir(BUILD_DIR)
    print(fileName.rstrip('.gz'))
    tar = tarfile.open(os.path.join(TAR_DIR, fileName.rstrip('.gz')))
    tar.extractall()
    tar.close()
    f_sync()

    print('\n*** Building yasm ***\n')
    os.chdir(os.path.join(BUILD_DIR, yasm))
    os.system('./configure --prefix=%s' % TARGET_DIR)
    os.system('make -j %s && make install' % cpuCount)
    f_sync()


def build_xz():
    print('\n*** downloading xz/liblzma ***\n')
    os.chdir(TAR_DIR)
    server = 'http://www.ghosttoast.com/pub/ffmpeg'
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

def git_clone(name, url):
    print('\n*** Cloning %s ***\n' % name)
    if os.path.exists(os.path.join(BUILD_GIT_DIR, name)):
        print('git pull')
        os.chdir(os.path.join(BUILD_GIT_DIR, name))
        os.system('git pull')
    else:
        print('git clone')
        os.chdir(BUILD_GIT_DIR)
        os.system('git clone %s' % url)

def git_deploy(name):
    print('\n*** Deploy %s git to BUILD_DIR ***\n' % name)
    os.chdir(BUILD_GIT_DIR)
    os.system('cp -rf ./%s %s' % (name, BUILD_DIR))


def f_extractfiles():
    global fileList
    global gitList
    print('\n*** Extracting tar files ***\n')
    os.chdir(BUILD_DIR)
    for fileName in fileList:
        if fileName.rstrip('.xz').lower().endswith('.tar'):
            print(fileName.rstrip('.xz'))
            tar = tarfile.open(os.path.join(TAR_DIR, fileName.rstrip('.xz')))
            tar.extractall()
            tar.close()
    for item in gitList:
        git_deploy(item[0])
    f_sync()

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

def b_openssl():
    print('\n*** Building openssl ***\n')
    os.chdir(os.path.join(BUILD_DIR, openssl))
    os.system('./Configure no-shared --prefix=%s linux-x86_64' % (TARGET_DIR))
    os.system('make depend')
    os.system('make -j %s && make install' % cpuCount)

def b_libpng():
    print('\n*** Building libpng ***\n')
    os.chdir(os.path.join(BUILD_DIR, libpng))
    os.system('./configure --prefix=%s %s' % (TARGET_DIR, appendopt))
    os.system('make -j %s && make install' % cpuCount)

def b_openjpeg():
    print('\n*** Building openjpeg ***\n')
    os.chdir(os.path.join(BUILD_DIR, openjpeg))
    os.system('./bootstrap.sh')
    os.system('./configure --disable-png --prefix=%s %s' % (TARGET_DIR, appendopt))  # openjpeg 1.5
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
    os.system('./configure --prefix=%s --enable-static --disable-shared --disable-examples' % TARGET_DIR)
    os.system('make -j %s && make install' % cpuCount)

def b_libvpx():
    print('\n*** Building libvpx ***\n')
    os.chdir(os.path.join(BUILD_DIR, libvpx))
    os.system('./configure --prefix=%s --enable-static --disable-shared' % TARGET_DIR)
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

def b_twolame():
    print('\n*** Building twolame ***\n')
    os.chdir(os.path.join(BUILD_DIR, twolame))
    os.system('./configure --disable-shared --prefix=%s' % (TARGET_DIR))
    os.system('make -j %s && make install' % cpuCount)

def b_soxr():
    print('\n*** Building soxr ***\n')
    os.chdir(os.path.join(BUILD_DIR, soxr))
    os.system('mkdir Release')
    os.chdir(os.path.join(BUILD_DIR, soxr, 'Release'))
    os.system('cmake -DCMAKE_BUILD_TYPE=Release -Wno-dev -DCMAKE_INSTALL_PREFIX="%s" -DBUILD_SHARED_LIBS:bool=off ..' % TARGET_DIR)
    os.system('make -j %s && make install' % cpuCount)

def b_wavpack():
    print('\n*** Building wavpack ***\n')
    os.chdir(os.path.join(BUILD_DIR, wavpack))
    os.system('./configure --prefix=%s --disable-shared' % (TARGET_DIR))
    os.system('make -j %s && make install' % cpuCount)

def b_fdkaac():
    print('\n*** Building fdk-aac ***\n')
    os.chdir(os.path.join(BUILD_DIR, fdkaac))
    os.system('./configure --prefix=%s --disable-shared' % (TARGET_DIR))
    os.system('make -j %s && make install' % cpuCount)

def b_x264():
    print('\n*** Building x264 ***\n')
    os.chdir(os.path.join(BUILD_DIR, 'x264'))  # for git checkout
    os.system('./configure --prefix=%s --enable-static --disable-cli --disable-opencl --disable-swscale --disable-lavf --disable-ffms --disable-gpac --bit-depth=%s --chroma-format=%s' % (TARGET_DIR, x264BitDepth, x264Chroma))
    os.system('make -j %s && make install' % cpuCount)

def b_x265():
    print('\n*** Build x265 ***\n')
    os.chdir(os.path.join(BUILD_DIR, 'x265', 'build', 'linux'))  # for git checkout
    os.system('cmake -G "Unix Makefiles" -Wno-dev -DCMAKE_INSTALL_PREFIX="%s" -DENABLE_SHARED:bool=off ../../source' % TARGET_DIR)
    os.system('make -j %s && make install' % cpuCount)

def b_xvid():
    print('\n*** Building xvid ***\n')
    os.chdir(os.path.join(BUILD_DIR, xvid, 'build', 'generic'))
    # apply patch for static only build
    os.system('cp -f %s ./' % os.path.join(TAR_DIR, 'xvid_Makefile.patch'))
    os.system('patch -f < xvid_Makefile.patch')
    os.system('./configure --prefix=%s' % TARGET_DIR)
    os.system('make -j %s && make install' % cpuCount)
    #os.system('rm -f %s' % os.path.join(TARGET_DIR, 'lib', 'libxvidcore.so.*'))

def b_dcadec():
    print('\n*** Building dcadec ***\n')
    os.chdir(os.path.join(BUILD_DIR, dcadec))
    os.putenv('DESTDIR', TARGET_DIR)
    os.putenv('PREFIX', "")
    os.system('make -j %s && make install' % cpuCount)
    os.unsetenv('DESTDIR')
    os.unsetenv('PREFIX')

def b_snappy():
    print('\n*** Building snappy ***\n')
    os.chdir(os.path.join(BUILD_DIR, snappy))
    # CXX FLAGS
    os.putenv('CXXFLAGS', ENV_CFLAGS)

    os.system('make clean')
    os.system('./configure --disable-shared --prefix=%s' % TARGET_DIR)
    os.system('make -j %s && make install' % cpuCount)

def b_blackmagic():
    print('\n*** Deploying Blackmagic SDK ***\n')
    os.chdir(os.path.join(BUILD_DIR, blackmagic, 'Linux', 'include'))
    os.system('cp -f ./* %s' % os.path.join(TARGET_DIR, 'include'))

def b_nvenc():
    print('\n*** Deploying nvenc (Nvidia Video SDK) ***\n')
    os.chdir(os.path.join(BUILD_DIR, nvenc, 'Samples', 'common', 'inc'))
    os.system('cp -f ./nvEncodeAPI.h %s' % os.path.join(TARGET_DIR, 'include'))


def b_ffmpeg():
    print('\n*** Building ffmpeg ***\n')
    os.chdir(os.path.join(BUILD_DIR,'ffmpeg'))


    # modify env
    ENV_CFLAGS_NEW = '%s --static' % ENV_CFLAGS
    os.putenv('CFLAGS', ENV_CFLAGS_NEW)
    ENV_LDFLAGS_NEW = ENV_LDFLAGS
    ENV_LDFLAGS_NEW += ' -fopenmp'  # openmp is needed by soxr
    #ENV_LDFLAGS_NEW += ' -lstdc++'  # stdc++ is needed by snappy
    os.putenv('LDFLAGS', ENV_LDFLAGS_NEW)

    confcmd = ''
    confcmd += './configure --prefix=%s' % TARGET_DIR
    confcmd += ' --extra-version=static'
    confcmd += ' --pkg-config-flags="--static"'
    confcmd += ' --enable-gpl'
    confcmd += ' --enable-version3'
    confcmd += ' --enable-nonfree'
    confcmd += ' --enable-static'
    confcmd += ' --disable-shared'
    confcmd += ' --disable-debug'
    confcmd += ' --enable-runtime-cpudetect'
    confcmd += ' --disable-doc'
    confcmd += ' --disable-ffplay'
    confcmd += ' --enable-bzlib'
    confcmd += ' --enable-zlib'
    #confcmd += ' --enable-libbluray'
    confcmd += ' --enable-libdcadec'
    confcmd += ' --enable-libfdk-aac'
    confcmd += ' --enable-libmp3lame'
    confcmd += ' --enable-libopenjpeg'
    #confcmd += ' --enable-opus'
    #confcmd += ' --enable-librtmp'
    confcmd += ' --enable-libvorbis'
    confcmd += ' --enable-libtheora'
    confcmd += ' --enable-libvpx'
    confcmd += ' --enable-libspeex'
    confcmd += ' --enable-libx264'
    confcmd += ' --enable-libx265'
    #confcmd += ' --enable-libsnappy'
    confcmd += ' --enable-libsoxr'
    confcmd += ' --enable-libtwolame'
    confcmd += ' --enable-libwavpack'
    #confcmd += ' --enable-webp'
    confcmd += ' --enable-nvenc'
    confcmd += ' --enable-openssl'
    #confcfg += ' --enable-libschrodeinger'
    #confcmd += ' --disable-devices'
    #confcmd += ' --enable-lto'
    #confcmd += ' --enable-hardcoded-tables'
    #confcmd += ' --disable-safe-bitstream-reader'

    os.system('make distclean')
    os.system(confcmd)
    os.system('make -j %s && make install' % cpuCount)
    os.system('make tools/qt-faststart')
    os.system('cp tools/qt-faststart %s' % os.path.join(TARGET_DIR, 'bin'))

    # restore env
    os.putenv('CFLAGS', ENV_CFLAGS)
    os.putenv('LDFLAGS', ENV_LDFLAGS)

def out_pack():
    os.chdir(OUT_DIR)
    for item in ['ffmpeg', 'ffprobe', 'tiffcp', 'tiffinfo', 'qt-faststart']:
        os.system('cp -f {0} ./'.format(os.path.join(TARGET_DIR, 'bin', item)))
    os.system('strip *')
    os.chdir(ENV_ROOT)
    os.system('tar -cvf ./{0}.tar ./{0}'.format(OUT_FOLDER))
    os.system('xz -ve9 ./{0}.tar'.format(OUT_FOLDER))

def u_striplibs():
    os.system('strip %s/*' % os.path.join(TARGET_DIR, 'lib'))

def go_setup():
    prewarn()
    cleanOUT_DIR_FILES()
    cleanOUT_DIR()
    cleanTARGET_DIR()
    cleanBUILD_DIR()
    #cleanTAR_DIR()
    setupDIR()
    build_yasm()
    build_xz()
    f_getfiles()
    f_decompressfiles()
    f_extractfiles()

def go_main():
    b_zlib()
    b_bzip2()
    b_ncurses()
    b_openssl()
    #b_snappy()
    b_libtiff()
    b_libpng()
    b_openjpeg()
    b_libogg()
    b_libvorbis()
    b_libtheora()
    b_libvpx()
    b_speex()
    b_lame()
    b_twolame()
    b_soxr()
    b_wavpack()
    b_fdkaac()
    b_x264()
    b_x265()
    b_xvid()
    b_dcadec()
    b_blackmagic()
    b_nvenc()

def run():
    try:
        go_setup()
        go_main()
        b_ffmpeg()
        out_pack()
    except KeyboardInterrupt:
        print('\nBye\n')
        sys.exit(0)

if __name__ == '__main__':
    run()

    #b_x264()
    #b_ffmpeg()
    #out_pack()

