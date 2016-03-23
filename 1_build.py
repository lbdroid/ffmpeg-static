#!/usr/bin/env python

import os
import sys
import urllib2
import tarfile
import time
import subprocess
import argparse
import multiprocessing

# check python ver 2.6+
if sys.version_info < (2, 6):
    print('need python 2.6+')
    sys.exit(0)
# check python ver < 3
if sys.version_info > (3, 0):
    print('need python 2')
    sys.exit(0)

# TODO - tidy this up/move into class
# check for git
p = subprocess.Popen('which git', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
data = p.communicate()[0]
if data.count('which') > 0:
    print('unable to find git')
    sys.exit(0)

class ffmpeg_build():

    def __init__(self, nonfree=False):
        self.nonfree = nonfree

        self.cpuCount = multiprocessing.cpu_count()

        self.app_list()
        self.setup_folder_vars()
        self.setup_env_vars()


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

    def app_list(self):
        self.downloadList = []
        self.downloadAuxList = []
        self.gitList = []

        self.xz = 'xz-5.2.2'
        self.downloadList.append(self.xz)

        self.yasm = 'yasm-1.3.0'
        self.downloadList.append(self.yasm)

        self.zlib = 'zlib-1.2.8'
        self.downloadList.append(self.zlib)

        self.bzip2 = 'bzip2-1.0.6'
        self.downloadList.append(self.bzip2)

        self.ncurses = 'ncurses-6.0'
        self.downloadList.append(self.ncurses)

        self.openssl = 'openssl-1.0.2g'
        self.downloadList.append(self.openssl)

        self.snappy = 'snappy-1.1.3'
        self.downloadList.append(self.snappy)

        self.libpng = 'libpng-1.6.21'
        self.downloadList.append(self.libpng)

        self.openjpeg = 'openjpeg-1.5.2'  # ffmpeg works with 1.5, not 2.0
        self.downloadList.append(self.openjpeg)

        self.libtiff = 'tiff-4.0.3'
        self.downloadList.append(self.libtiff)

        self.libogg = 'libogg-1.3.2'
        self.downloadList.append(self.libogg)

        self.libvorbis = 'libvorbis-1.3.5'
        self.downloadList.append(self.libvorbis)

        self.libtheora = 'libtheora-1.1.1'
        self.downloadList.append(self.libtheora)

        self.libvpx = 'libvpx-1.5.0'
        self.downloadList.append(self.libvpx)

        self.speex = 'speex-1.2rc2'
        self.downloadList.append(self.speex)

        self.lame = 'lame-3.99.5'
        self.downloadList.append(self.lame)

        self.twolame = 'twolame-0.3.13'
        self.downloadList.append(self.twolame)

        self.soxr = 'soxr-0.1.2'
        self.downloadList.append(self.soxr)

        self.wavpack = 'wavpack-4.75.2'
        self.downloadList.append(self.wavpack)

        self.fdkaac = 'fdk-aac-0.1.4'
        self.downloadList.append(self.fdkaac)

        self.x264 = 'https://git.videolan.org/git/x264.git'
        self.gitList.append(['x264', self.x264])
        self.x264BitDepth = '8'
        self.x264Chroma = 'all'

        self.x265 = 'https://github.com/videolan/x265.git'
        self.gitList.append(['x265', self.x265])

        self.xvid = 'xvid-1.3.4'
        self.downloadList.append(self.xvid)
        self.downloadAuxList.append('xvid_Makefile.patch')

        self.dcadec = 'dcadec-0.2.0'
        self.downloadList.append(self.dcadec)

        self.nvenc = 'nvidia_video_sdk_6.0.1'
        self.downloadList.append(self.nvenc)

        self.blackmagic = 'Blackmagic_DeckLink_SDK_10.6.1'
        self.downloadList.append(self.blackmagic)

        self.ffmpeg = 'git://source.ffmpeg.org/ffmpeg.git'
        self.gitList.append(['ffmpeg', self.ffmpeg])

        self.fileList = []
        for item in self.downloadList:
            self.fileList.append('%s.tar.xz' % item)
        for item in self.downloadAuxList:
            self.fileList.append('%s.xz' % item)

    def setup_folder_vars(self):
        self.ENV_ROOT = os.getcwd()
        self.TARGET_DIR = os.path.join(self.ENV_ROOT, 'target')
        self.BUILD_DIR = os.path.join(self.ENV_ROOT, 'compile')
        self.BUILD_GIT_DIR = os.path.join(self.ENV_ROOT, 'sourcegit')
        self.TAR_DIR = os.path.join(self.ENV_ROOT, 'sourcetar')

        self.OUT_FOLDER = 'output'
        self.OUT_DIR = os.path.join(self.ENV_ROOT, self.OUT_FOLDER)

    def setup_env_vars(self):
        # setup ENV
        self.ENV_PATH_ORIG = os.getenv('PATH')
        self.ENV_LD_ORIG = os.getenv('LD_LIBRARY_PATH')
        #if sys.platform.startswith('darwin'):  # TODO - fix darwin vars
        #    addpath += ':/opt/local/bin'
        os.putenv('PATH', '%s:%s' % (os.path.join(self.TARGET_DIR, 'bin'), self.ENV_PATH_ORIG))
        os.putenv('LD_LIBRARY_PATH', '%s:%s' % (os.path.join(self.TARGET_DIR, 'lib'), self.ENV_LD_ORIG))
        os.putenv('PKG_CONFIG_PATH', os.path.join(self.TARGET_DIR, 'lib', 'pkgconfig'))
        self.ENV_CFLAGS = '-I%s' % os.path.join(self.TARGET_DIR, 'include')
        os.putenv('CFLAGS', self.ENV_CFLAGS)
        self.ENV_LDFLAGS = '-L%s -static -static-libgcc -static-libstdc++' % os.path.join(self.TARGET_DIR, 'lib')
        os.putenv('LDFLAGS', self.ENV_LDFLAGS)
        os.system('export')

    def setupDIR(self):
        for item in [self.ENV_ROOT, self.TARGET_DIR, self.BUILD_DIR, self.BUILD_GIT_DIR, self.TAR_DIR, self.OUT_DIR]:
            os.system('mkdir -p %s' % item)

    def cleanTARGET_DIR(self):
        os.system('rm -rf %s' % self.TARGET_DIR)

    def cleanBUILD_DIR(self):
        os.system('rm -rf %s' % self.BUILD_DIR)

    def cleanBUILDGIT_DIR(self):
        os.system('rm -rf %s' % self.BUILD_GIT_DIR)

    def cleanTAR_DIR(self):
        os.system('rm -rf %s' % self.TAR_DIR)

    def cleanOUT_DIR(self):
        os.system('rm -rf %s' % self.OUT_DIR)

    def cleanOUT_DIR_FILES(self):
        os.system('rm -f %s.tar' % self.OUT_DIR)
        os.system('rm -f %s.tar.xz' % self.OUT_DIR)

    def cleanALL(self):
        self.cleanTARGET_DIR()
        self.cleanBUILD_DIR()
        self.cleanTAR_DIR()
        self.cleanOUT_DIR()
        self.cleanOUT_DIR_FILES()

    @staticmethod
    def prewarn():
        print('\nneeded packages:\ngcc glibc-static git cmake\n\n')
        x = 2
        while x > 0:
            print(x)
            x = x - 1
            time.sleep(1)

    def f_getfiles(self):
        print('\n*** Downloading files ***\n')
        os.chdir(self.TAR_DIR)
        server = 'http://www.ghosttoast.com/pub/ffmpeg'
        for fileName in self.fileList:
            if os.path.exists(os.path.join(self.TAR_DIR, fileName.rstrip('.xz'))) is False:
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
        self.f_sync()

    def f_decompressfiles(self):
        print('\n*** Decompressing xz files ***\n')
        os.chdir(self.BUILD_DIR)
        for fileName in self.fileList:
            if os.path.exists(os.path.join(self.TAR_DIR, fileName.rstrip('.xz'))) is False:
                os.system('%s -dv %s' % (os.path.join(self.TARGET_DIR, 'bin', 'xz'), os.path.join(self.TAR_DIR, fileName)))
            else:
                print('%s already uncompressed' % fileName)
        self.f_sync()
        for item in self.gitList:
            self.git_clone(item[0], item[1])
        self.f_sync()

    @staticmethod
    def f_sync():
        print('\n*** Syncinig Hard Drive ***\n')
        os.system('sync')

    def build_yasm(self):
        print('\n*** downloading yasm ***\n')
        os.chdir(self.TAR_DIR)
        server = 'http://www.ghosttoast.com/pub/ffmpeg'
        fileName = '%s.tar.gz' % self.yasm
        if os.path.exists(os.path.join(self.TAR_DIR, fileName.rstrip('.gz'))) is False:
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
        self.f_sync()

        print('\n*** Decompressing yasm ***\n')
        os.chdir(self.BUILD_DIR)
        if os.path.exists(os.path.join(self.TAR_DIR, fileName.rstrip('.gz'))) is False:
            os.system('gunzip -v %s' % os.path.join(self.TAR_DIR, fileName))
        else:
            print('%s already uncompressed' % fileName)
        self.f_sync()

        print('\n*** Extracting yasm ***\n')
        os.chdir(self.BUILD_DIR)
        print(fileName.rstrip('.gz'))
        tar = tarfile.open(os.path.join(self.TAR_DIR, fileName.rstrip('.gz')))
        tar.extractall()
        tar.close()
        self.f_sync()

        print('\n*** Building yasm ***\n')
        os.chdir(os.path.join(self.BUILD_DIR, self.yasm))
        os.system('./configure --prefix=%s' % self.TARGET_DIR)
        os.system('make -j %s && make install' % self.cpuCount)
        self.f_sync()

    def build_xz(self):
        print('\n*** downloading xz/liblzma ***\n')
        os.chdir(self.TAR_DIR)
        server = 'http://www.ghosttoast.com/pub/ffmpeg'
        fileName = '%s.tar.gz' % self.xz
        if os.path.exists(os.path.join(self.TAR_DIR, fileName.rstrip('.gz'))) is False:
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
        self.f_sync()

        print('\n*** Decompressing xz/liblzma ***\n')
        os.chdir(self.BUILD_DIR)
        if os.path.exists(os.path.join(self.TAR_DIR, fileName.rstrip('.gz'))) is False:
            os.system('gunzip -v %s' % os.path.join(self.TAR_DIR, fileName))
        else:
            print('%s already uncompressed' % fileName)
        self.f_sync()

        print('\n*** Extracting xz/liblzma ***\n')
        os.chdir(self.BUILD_DIR)
        print(fileName.rstrip('.gz'))
        tar = tarfile.open(os.path.join(self.TAR_DIR, fileName.rstrip('.gz')))
        tar.extractall()
        tar.close()
        self.f_sync()

        print('\n*** Building xz/liblzma ***\n')
        os.chdir(os.path.join(self.BUILD_DIR, self.xz))
        os.system('./configure --prefix=%s' % self.TARGET_DIR)
        os.system('make -j %s && make install' % self.cpuCount)
        self.f_sync()

    def git_clone(self, name, url):
        print('\n*** Cloning %s ***\n' % name)
        if os.path.exists(os.path.join(self.BUILD_GIT_DIR, name)):
            print('git pull')
            os.chdir(os.path.join(self.BUILD_GIT_DIR, name))
            os.system('git pull')
        else:
            print('git clone')
            os.chdir(self.BUILD_GIT_DIR)
            os.system('git clone %s' % url)

    def git_deploy(self, name):
        print('\n*** Deploy %s git to BUILD_DIR ***\n' % name)
        os.chdir(self.BUILD_GIT_DIR)
        os.system('cp -rf ./%s %s' % (name, self.BUILD_DIR))

    def f_extractfiles(self):
        print('\n*** Extracting tar files ***\n')
        os.chdir(self.BUILD_DIR)
        for fileName in self.fileList:
            if fileName.rstrip('.xz').lower().endswith('.tar'):
                print(fileName.rstrip('.xz'))
                tar = tarfile.open(os.path.join(self.TAR_DIR, fileName.rstrip('.xz')))
                tar.extractall()
                tar.close()
        for item in self.gitList:
            self.git_deploy(item[0])
        self.f_sync()

    def b_zlib(self):
        print('\n*** Building zlib ***\n')
        os.chdir(os.path.join(self.BUILD_DIR, self.zlib))
        os.system('export CFLAGS="$CFLAGS -fPIC";./configure --prefix=%s --static' % self.TARGET_DIR)
        os.system('export CFLAGS="$CFLAGS -fPIC";make -j %s && make install' % self.cpuCount)

    def b_bzip2(self):
        print('\n*** Building bzip2 ***\n')
        os.chdir(os.path.join(self.BUILD_DIR, self.bzip2))
        os.system('make CFLAGS="-Wall -Winline -O2 -g -D_FILE_OFFSET_BITS=64 -fPIC"')
        os.system('make install PREFIX=%s' % self.TARGET_DIR)

    def b_ncurses(self):
        print('\n*** Building ncurses ***\n')
        os.chdir(os.path.join(self.BUILD_DIR, self.ncurses))
        os.system('./configure --with-termlib --with-ticlib --prefix=%s' % self.TARGET_DIR)
        os.system('make -j %s && make install' % self.cpuCount)

    def b_openssl(self):
        print('\n*** Building openssl ***\n')
        os.chdir(os.path.join(self.BUILD_DIR, self.openssl))
        os.system('./Configure no-shared --prefix=%s linux-x86_64' % (self.TARGET_DIR))
        os.system('make depend')
        os.system('make -j %s && make install' % self.cpuCount)

    def b_libpng(self):
        print('\n*** Building libpng ***\n')
        os.chdir(os.path.join(self.BUILD_DIR, self.libpng))
        os.system('./configure --prefix=%s' % self.TARGET_DIR)
        os.system('make -j %s && make install' % self.cpuCount)

    def b_openjpeg(self):
        print('\n*** Building openjpeg ***\n')
        os.chdir(os.path.join(self.BUILD_DIR, self.openjpeg))
        os.system('./bootstrap.sh')
        os.system('./configure --disable-png --prefix=%s' % self.TARGET_DIR)
        os.system('make -j %s && make install' % self.cpuCount)

    def b_libtiff(self):
        print('\n*** Building libtiff ***\n')
        os.chdir(os.path.join(self.BUILD_DIR, self.libtiff))
        os.system('export CFLAGS="--static -I%s";export LDFLAGS="-L%s -static -static-libgcc";./configure --prefix=%s --enable-shared=no --enable-static=yes' % (os.path.join(self.TARGET_DIR, 'include'), os.path.join(self.TARGET_DIR, 'lib'), self.TARGET_DIR))
        os.system('export CFLAGS="--static -I%s";export LDFLAGS="-L%s -static -static-libgcc";make -j %s && make install' % (os.path.join(self.TARGET_DIR, 'include'), os.path.join(self.TARGET_DIR, 'lib'), self.cpuCount))

    def b_libogg(self):
        print('\n*** Building libogg ***\n')
        os.chdir(os.path.join(self.BUILD_DIR, self.libogg))
        os.system('./configure --prefix=%s' % self.TARGET_DIR)
        os.system('make -j %s && make install' % self.cpuCount)

    def b_libvorbis(self):
        print('\n*** Building libvorbis ***\n')
        os.chdir(os.path.join(self.BUILD_DIR, self.libvorbis))
        os.system('./configure --prefix=%s' % self.TARGET_DIR)
        os.system('make -j %s && make install' % self.cpuCount)

    def b_libtheora(self):
        print('\n*** Building libtheora ***\n')
        os.chdir(os.path.join(self.BUILD_DIR, self.libtheora))
        os.system('./configure --prefix=%s --enable-static --disable-shared --disable-examples' % self.TARGET_DIR)
        os.system('make -j %s && make install' % self.cpuCount)

    def b_libvpx(self):
        print('\n*** Building libvpx ***\n')
        os.chdir(os.path.join(self.BUILD_DIR, self.libvpx))
        os.system('./configure --prefix=%s --enable-static --disable-shared' % self.TARGET_DIR)
        os.system('make -j %s && make install' % self.cpuCount)

    def b_speex(self):
        print('\n*** Building speex ***\n')
        os.chdir(os.path.join(self.BUILD_DIR, self.speex))
        os.system('./configure --prefix=%s --enable-sse' % self.TARGET_DIR)
        os.system('make -j %s && make install' % self.cpuCount)

    def b_lame(self):
        print('\n*** Building lame ***\n')
        os.chdir(os.path.join(self.BUILD_DIR, self.lame))
        os.system('./configure --disable-frontend --enable-shared=no --enable-static=yes --prefix=%s' % self.TARGET_DIR)
        os.system('make -j %s && make install' % self.cpuCount)

    def b_twolame(self):
        print('\n*** Building twolame ***\n')
        os.chdir(os.path.join(self.BUILD_DIR, self.twolame))
        os.system('./configure --disable-shared --prefix=%s' % (self.TARGET_DIR))
        os.system('make -j %s && make install' % self.cpuCount)

    def b_soxr(self):
        print('\n*** Building soxr ***\n')
        os.chdir(os.path.join(self.BUILD_DIR, self.soxr))
        os.system('mkdir Release')
        os.chdir(os.path.join(self.BUILD_DIR, self.soxr, 'Release'))
        os.system('cmake -DCMAKE_BUILD_TYPE=Release -Wno-dev -DCMAKE_INSTALL_PREFIX="%s" -DBUILD_SHARED_LIBS:bool=off ..' % self.TARGET_DIR)
        os.system('make -j %s && make install' % self.cpuCount)

    def b_wavpack(self):
        print('\n*** Building wavpack ***\n')
        os.chdir(os.path.join(self.BUILD_DIR, self.wavpack))
        os.system('./configure --prefix=%s --disable-shared' % (self.TARGET_DIR))
        os.system('make -j %s && make install' % self.cpuCount)

    def b_fdkaac(self):
        print('\n*** Building fdk-aac ***\n')
        os.chdir(os.path.join(self.BUILD_DIR, self.fdkaac))
        os.system('./configure --prefix=%s --disable-shared' % (self.TARGET_DIR))
        os.system('make -j %s && make install' % self.cpuCount)

    def b_x264(self):
        print('\n*** Building x264 ***\n')
        os.chdir(os.path.join(self.BUILD_DIR, 'x264'))  # for git checkout
        os.system('./configure --prefix=%s --enable-static --disable-cli --disable-opencl --disable-swscale --disable-lavf --disable-ffms --disable-gpac --bit-depth=%s --chroma-format=%s' % (self.TARGET_DIR, self.x264BitDepth, self.x264Chroma))
        os.system('make -j %s && make install' % self.cpuCount)

    def b_x265(self):
        print('\n*** Build x265 ***\n')
        os.chdir(os.path.join(self.BUILD_DIR, 'x265', 'build', 'linux'))  # for git checkout
        os.system('cmake -G "Unix Makefiles" -Wno-dev -DCMAKE_INSTALL_PREFIX="%s" -DENABLE_SHARED:bool=off ../../source' % self.TARGET_DIR)
        os.system('make -j %s && make install' % self.cpuCount)

    def b_xvid(self):
        print('\n*** Building xvid ***\n')
        os.chdir(os.path.join(self.BUILD_DIR, self.xvid, 'build', 'generic'))
        # apply patch for static only build
        os.system('cp -f %s ./' % os.path.join(self.TAR_DIR, 'xvid_Makefile.patch'))
        os.system('patch -f < xvid_Makefile.patch')
        os.system('./configure --prefix=%s' % self.TARGET_DIR)
        os.system('make -j %s && make install' % self.cpuCount)
        #os.system('rm -f %s' % os.path.join(TARGET_DIR, 'lib', 'libxvidcore.so.*'))

    def b_dcadec(self):
        print('\n*** Building dcadec ***\n')
        os.chdir(os.path.join(self.BUILD_DIR, self.dcadec))
        os.putenv('DESTDIR', self.TARGET_DIR)
        os.putenv('PREFIX', "")
        os.system('make -j %s && make install' % self.cpuCount)
        os.unsetenv('DESTDIR')
        os.unsetenv('PREFIX')

    def b_snappy(self):
        print('\n*** Building snappy ***\n')
        os.chdir(os.path.join(self.BUILD_DIR, self.snappy))
        # CXX FLAGS
        os.putenv('CXXFLAGS', self.ENV_CFLAGS)  # TODO, check if this is actually useful
        os.system('make clean')
        os.system('./configure --disable-shared --prefix=%s' % self.TARGET_DIR)
        os.system('make -j %s && make install' % self.cpuCount)

    def b_blackmagic(self):
        print('\n*** Deploying Blackmagic SDK ***\n')
        os.chdir(os.path.join(self.BUILD_DIR, self.blackmagic, 'Linux', 'include'))
        os.system('cp -f ./* %s' % os.path.join(self.TARGET_DIR, 'include'))

    def b_nvenc(self):
        print('\n*** Deploying nvenc (Nvidia Video SDK) ***\n')
        os.chdir(os.path.join(self.BUILD_DIR, self.nvenc, 'Samples', 'common', 'inc'))
        os.system('cp -f ./nvEncodeAPI.h %s' % os.path.join(self.TARGET_DIR, 'include'))

    def b_ffmpeg(self):
        print('\n*** Building ffmpeg ***\n')
        os.chdir(os.path.join(self.BUILD_DIR, 'ffmpeg'))


        # modify env
        ENV_CFLAGS_NEW = '%s --static' % self.ENV_CFLAGS
        os.putenv('CFLAGS', ENV_CFLAGS_NEW)
        ENV_LDFLAGS_NEW = self.ENV_LDFLAGS
        ENV_LDFLAGS_NEW += ' -fopenmp'  # openmp is needed by soxr
        #ENV_LDFLAGS_NEW += ' -lstdc++'  # stdc++ is needed by snappy
        os.putenv('LDFLAGS', ENV_LDFLAGS_NEW)

        confcmd = ''
        confcmd += './configure --prefix=%s' % self.TARGET_DIR
        confcmd += ' --extra-version=static'
        confcmd += ' --pkg-config-flags="--static"'
        confcmd += ' --enable-gpl'
        confcmd += ' --enable-version3'
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
        #confcfg += ' --enable-libschrodeinger'
        #confcmd += ' --disable-devices'
        #confcmd += ' --enable-lto'
        #confcmd += ' --enable-hardcoded-tables'
        #confcmd += ' --disable-safe-bitstream-reader'
        if self.nonfree:
            confcmd += ' --enable-nonfree'
            confcmd += ' --enable-libfdk-aac'
            confcmd += ' --enable-nvenc'
            confcmd += ' --enable-openssl'

        os.system('make distclean')
        os.system(confcmd)
        os.system('make -j %s && make install' % self.cpuCount)
        os.system('make tools/qt-faststart')
        os.system('cp tools/qt-faststart %s' % os.path.join(self.TARGET_DIR, 'bin'))

        # restore env
        os.putenv('CFLAGS', self.ENV_CFLAGS)
        os.putenv('LDFLAGS', self.ENV_LDFLAGS)

    def out_pack(self):
        os.chdir(self.OUT_DIR)
        for item in ['ffmpeg', 'ffprobe', 'tiffcp', 'tiffinfo', 'qt-faststart']:
            os.system('cp -f {0} ./'.format(os.path.join(self.TARGET_DIR, 'bin', item)))
        os.system('strip *')
        os.chdir(self.ENV_ROOT)
        os.system('tar -cvf ./{0}.tar ./{0}'.format(self.OUT_FOLDER))
        os.system('xz -ve9 ./{0}.tar'.format(self.OUT_FOLDER))

    def u_striplibs(self):
        os.system('strip %s/*' % os.path.join(self.TARGET_DIR, 'lib'))

    def go_setup(self):
        self.prewarn()
        self.cleanOUT_DIR_FILES()
        self.cleanOUT_DIR()
        self.cleanTARGET_DIR()
        self.cleanBUILD_DIR()
        #self.cleanTAR_DIR()
        self.setupDIR()
        self.build_yasm()
        self.build_xz()
        self.f_getfiles()
        self.f_decompressfiles()
        self.f_extractfiles()

    def go_main(self):
        self.b_zlib()
        self.b_bzip2()
        self.b_ncurses()
        #self.b_snappy()
        self.b_libtiff()
        self.b_libpng()
        self.b_openjpeg()
        self.b_libogg()
        self.b_libvorbis()
        self.b_libtheora()
        self.b_libvpx()
        self.b_speex()
        self.b_lame()
        self.b_twolame()
        self.b_soxr()
        self.b_wavpack()
        self.b_x264()
        self.b_x265()
        self.b_xvid()
        self.b_dcadec()
        self.b_blackmagic()
        if self.nonfree:
            self.b_fdkaac()
            self.b_nvenc()
            self.b_openssl()

    def run(self):
        try:
            self.go_setup()
            self.go_main()
            self.b_ffmpeg()
            self.out_pack()
        except KeyboardInterrupt:
            print('\nBye\n')
            sys.exit(0)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--nonfree', dest='nonfree',
            help='build non-free/non-redist', action='store_true',
            default=False)
    args = parser.parse_args()

    ffmpegb = ffmpeg_build(nonfree=args.nonfree)
    ffmpegb.run()


